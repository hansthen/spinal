from quart import Quart, flash, request
import motor
from chargebee.models import Event
import chargebee

from jinja2 import Environment, PackageLoader, select_autoescape

import configargparse
import datetime
import json
from collections import defaultdict

import models
import logging
from signature import create_security_token, verify_security_token

logger = logging.getLogger(__name__)

app = Quart(__name__)

env = Environment(
    loader=PackageLoader("server", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

from tap.parser import Parser

RESULT_ENUM = {"ok", "not ok"}


def setup_parser():
    """Create a parser for the command line arguments

    We use configargparse to make it easy to also use
    environment variables and a config file to specify defaults"""
    parser = configargparse.ArgumentParser(description="store test results")
    parser.add_argument("command", help="startup command")
    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        env_var="SPINAL_CONFIG_FILE",
        default="~/.spinal.settings",
        help="configuration file",
    )
    parser.add_argument(
        "--public-key",
        type=str,
        env_var="SPINAL_PUBLIC_KEY",
        default=open("id_rsa.pub").read(),
        help="the public key to use for validating a signature",
    )
    parser.add_argument(
        "--private-key",
        type=str,
        env_var="SPINAL_PRIVATE_KEY",
        default=open("id_rsa").read(),
        help="the private key to use for validating a signature",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        env_var="LOG_LEVEL",
        default="WARNING",
        help="Log level for main program",
    )
    return parser


class TapLineWrapper:
    def __init__(self, line):
        self.category = line.category


def merge_lists(list1, list2):
    tests = list1
    results = list2
    last = len(results) - 1
    indices = list(range(len(results)))
    while indices:
        for i in indices:
            if results[i] in tests:
                indices.remove(i)
                break
            elif i != 0 and results[i - 1] in tests:
                j = tests.index(results[i - 1])
                indices.remove(i)
                # append results[i]` behind
                tests.insert(j + 1, results[i])
                break
            elif i != last and results[i + 1] in tests:
                j = tests.index(results[i + 1])
                indices.remove(i)
                tests.insert(j, results[i])
                break
            elif i == last:
                tests.append(results[i])
                indices.remove(i)
    return list1


def create_table(runs, tests):
    table = []
    for test in tests:
        row = []
        row.append(test)

        for run in runs:
            if test in run:
                row.append(run[test].result)
            else:
                row.append(None)
        table.append(row)
    return table


async def default_webhook(event):
    logger.debug("Ignore event of type %s", event.event_type)
    return "IGNORE: " + event.event_type, 200


webhooks = defaultdict(lambda: default_webhook)


def webhook(event_type):
    def decorator_register(func):
        webhooks[event_type] = func
        return func

    return decorator_register


@webhook("subscription_created")
async def subscription_created(event):
    logger.debug("Registered new project")
    project_name = event.content.subscription.cf_project_name
    logger.debug(project_name)
    logger.debug(event)
    project = models.Project(
        name=project_name, subscription_id=event.content.subscription.id
    )
    await project.commit()
    logger.debug("New project created")
    return "OK", 200


@webhook("pending_invoice_created")
async def pending_invoice_created(event):
    invoice_id = event.content.invoice.id
    result = chargebee.Invoice.add_charge(
        invoice_id, {"amount": 150, "description": "150 test runs in this period"}
    )
    invoice = result.invoice
    logger.debug(invoice)
    result = chargebee.Invoice.close(invoice_id)
    logger.debug(result)
    logger.debug(invoice)

    return "OK", 200


@app.route("/webhooks/chargebee/<token>", methods=["POST"])
async def handle_webhook(token):
    event = await request.data
    event = Event.deserialize(event)
    func = webhooks[event.event_type]
    logger.debug("handling webhook for %s by %s", event.event_type, func.__name__)
    return await func(event)


@app.route("/signup", methods=["GET"])
async def signup():
    template = env.get_template("signup.html")
    return template.render()


@app.route("/signup_completed", methods=["GET"])
async def signup_completed():
    subscription_id = request.args.get("sub_id")
    result = chargebee.Subscription.retrieve(subscription_id)
    subscription = result.subscription
    project_name = subscription.cf_project_name
    plan_name = request.args.get("plan_name")
    template = env.get_template("signup_completed.html")
    token = create_security_token(app.args.private_key, subscription_id)
    # generate a secure id
    # random hash: subscription_id
    return template.render({"project_name": project_name, "token": token})


@app.route("/project/<project>/", methods=["GET"])
async def get(project):
    db = models.connect("spinal")
    N = 4
    tests = []
    runs = []
    for run in TestRun.objects.order_by("-started"):
        runs.append({result.title: result for result in run.results})
        results = [result.title for result in run.results]
        tests = merge_lists(tests, results)
    table = create_table(runs, tests)
    template = env.get_template("test-results.html")
    return template.render(table=table)


@app.route("/project/<project_name>/", methods=["POST"])
async def insert(project_name):
    db = models.connect("spinal")
    project = await models.Project.find_one({"name": project_name})
    if not project:
        return json.dumps({"error": "Invalid project"}), 404
    else:
        logger.debug("Using existing project")

    tapper = Parser()
    run = models.Run(project=project.pk, timestamp=datetime.datetime.now())

    data = await request.get_data()
    for line in tapper.parse_text(str(data, "utf-8")):
        print(
            "{}: {}".format(
                line.category, line.description if line.category == "test" else ""
            )
        )
        if line.category == "test":
            result = models.Result(
                title=line.description,
                result="ok" if line.ok else "not ok",
                skip=line.directive.text if line.skip else None,
            )

            run.results.append(result)
        run.commit()
    return "hello"


logging.basicConfig(level="DEBUG")

chargebee.configure("test_hdeu7cKnChy96LLM5sHXixxOY3mYymie", "spinal-test")
if __name__ == "__main__":
    app.run()
else:
    parser = setup_parser()
    app.args = parser.parse_args()
