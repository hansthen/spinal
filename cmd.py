import sys
import logging
from io import StringIO
import re
import os

import configargparse
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level="DEBUG")


def setup_parser():
    """Create a parser for the command line arguments

    We use configargparse to make it easy to also use
    environment variables and a config file to specify defaults"""
    parser = configargparse.ArgumentParser(description="store test results")
    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        env_var="SPINAL_CONFIG_FILE",
        default="~/.spinal.settings",
        help="configuration file",
    )
    parser.add_argument(
        "--server",
        type=str,
        env_var="SPINAL_SERVER",
        default="http://localhost:5000/project/",
        help="the address of the spinal server",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="abc",
        env_var="SPINAL_PROJECT",
        help="the project name",
    )
    parser.add_argument(
        "--token",
        type=str,
        env_var="SPINAL_TOKEN",
        help="the secret token used to identify the project",
    )
    parser.add_argument(
        "--env",
        type=str,
        nargs="*",
        env_var="SPINAL_ENV",
        default=[],
        help="environment variables to be copied to the server, accepts a regular expression",
    )
    return parser


def tee(reader):
    buf = StringIO()

    for line in reader:
        buf.write(line)
        print(line, end="")
    return buf


def tee(reader):
    for line in reader:
        print(line, end="")
        yield bytes(line, "utf-8")


def main():
    parser = setup_parser()
    args = parser.parse_args()

    patterns = [re.compile(env) for env in args.env]

    copies = []
    for env in os.environ:
        for p in patterns:
            m = p.match(env)
            if m:
                copies.append(env)

    headers = {"ENV_" + env: os.environ.get(env) for env in copies}

    result = requests.post(
        args.server + args.project, data=tee(sys.stdin), headers=headers
    )
    if result.status_code != 200:
        logger.debug("Error uploading TAP %s", result.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
