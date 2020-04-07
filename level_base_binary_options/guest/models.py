from django.db import models

# Create your models here.
# myapp/models.py

import uuid
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel


class UserById(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, required=True)
    address = columns.Text()
    country = columns.Text()
    created_date = columns.DateTime()
    currency = columns.Text()
    fname = columns.Text()
    lname = columns.Text()
    mobile = columns.Text()
    vcurrency = columns.Float()


class UserCredential(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    email = columns.Text(required=True)
    username = columns.Text(required=True)
    password = columns.Text(required=True)
