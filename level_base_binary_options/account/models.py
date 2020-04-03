from django.db import models

import uuid
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel


# Create your models here.
class UserTransactionsBinary(DjangoCassandraModel):
    id = columns.UUID(primary_key=True)
    user_id = columns.UUID()
    created_date = columns.DateTime()
    trade_type = columns.Text()
    purchase_type = columns.Text()
    currency = columns.Text()
    staring_price = columns.Float()
    closing_price = columns.Float()
    amount = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    time_close = columns.DateTime()
    outcome = columns.Text()
    status = columns.Text()


class TransactionsByStatusBinary(DjangoCassandraModel):
    status = columns.Text(primary_key=True)
    id = columns.UUID()
    user_id = columns.UUID()
    created_date = columns.DateTime()
    trade_type = columns.Text()
    purchase_type = columns.Text()
    currency = columns.Text()
    staring_price = columns.Float()
    closing_price = columns.Float()
    amount = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    time_close = columns.DateTime()
    outcome = columns.Text()


class UserTransactionsIdBinary(DjangoCassandraModel):
    id = columns.UUID(default=uuid.uuid4)
    user_id = columns.UUID(primary_key=True)
    created_date = columns.DateTime()

