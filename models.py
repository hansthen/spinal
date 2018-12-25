from umongo import fields, Instance, Document, EmbeddedDocument
import motor
import asyncio


def connect(database):
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost")
    return client[database]


db = connect("spinal")
instance = Instance(db)


@instance.register
class Project(Document):
    name = fields.StrField(required=True)


@instance.register
class TestCase(Document):
    project = fields.ReferenceField(Project)
    name = fields.StrField(required=True)

    class Meta:
        indexes = {"key": ["project", "name"], "unique": True}


@instance.register
class Result(EmbeddedDocument):
    title = fields.StrField(required=True)
    testcase = fields.ReferenceField(TestCase)
    result = fields.StringField(required=True)
    skip = fields.StringField(default=None, allow_none=True)


@instance.register
class Run(Document):
    project = fields.ReferenceField(Project)
    timestamp = fields.DateTimeField(required=True)
    version = fields.StrField()
    results = fields.EmbeddedField(Result, missing=[], many=True)

    class Meta:
        indexes = ("project", "-timestamp")


TestCase.ensure_indexes()
Run.ensure_indexes()
