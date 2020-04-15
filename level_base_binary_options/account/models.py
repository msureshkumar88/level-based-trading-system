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


class UserTransactionsIdLevels(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.UUID()
    created_date = columns.DateTime()


class LevelBasedById(DjangoCassandraModel):
    transaction_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    created_by = columns.UUID()
    created_date = columns.DateTime()
    purchase_type = columns.Text()
    currency = columns.Text()
    staring_price = columns.Float()
    closing_price = columns.Float()
    amount = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    changes_allowed_time = columns.DateTime()
    status = columns.Text()
    level_pips = columns.Integer()
    levels_price = columns.Text()
    level_owners = columns.Text()
    user_count = columns.Integer()


class UsersOwnedLevels(DjangoCassandraModel):
    user_id = columns.UUID(primary_key=True)
    transaction_id = columns.UUID()
    created_date = columns.DateTime()
    currency = columns.Text()
    level_start_price = columns.Float()
    level_end_price = columns.Float()
    level_selected = columns.Integer()
    owner = columns.Boolean()
    status = columns.Text()
    changes_allowed_time = columns.DateTime()
    staring_price = columns.Float()
    closing_price = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    amount = columns.Float()
    outcome = columns.Text()


class LevelBasedByStatus(DjangoCassandraModel):
    status = columns.Text(primary_key=True)
    transaction_id = columns.UUID()
    created_date = columns.DateTime()
    purchase_type = columns.Text()
    currency = columns.Text()
    staring_price = columns.Float()
    closing_price = columns.Float()
    amount = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    changes_allowed_time = columns.DateTime()
    level_pips = columns.DateTime()
    levels_price = columns.Text()
    level_owners = columns.Text()
    user_count = columns.Integer()


class UsersOwnedLevelsStatus(DjangoCassandraModel):
    status = columns.Text()
    user_id = columns.UUID(primary_key=True)
    transaction_id = columns.UUID()
    created_date = columns.DateTime()
    currency = columns.Text()
    level_start_price = columns.Float()
    level_end_price = columns.Float()
    level_selected = columns.Integer()
    owner = columns.Boolean()
    changes_allowed_time = columns.DateTime()
    staring_price = columns.Float()
    closing_price = columns.Float()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    amount = columns.DateTime()
    outcome = columns.Text()


class TransactionsByUser(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.UUID()
    created_date = columns.DateTime()


class UserTransactions(DjangoCassandraModel):
    transaction_id = columns.UUID(primary_key=True)
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
    changes_allowed_time = columns.DateTime()
    outcome = columns.Text()
    status = columns.Text()
    time_close = columns.DateTime()
    level_pips = columns.Integer()
    levels_price = columns.Text()
    level_owners = columns.Text()
    join_date = columns.DateTime()
    level_start_price = columns.Float()
    level_end_price = columns.Float()
    level_selected = columns.Integer()
    created_by = columns.UUID()
    parent_id = columns.UUID()
    child = columns.Boolean()
    available_levels = columns.List(columns.Integer())


class TransactionsByState(DjangoCassandraModel):
    transaction_id = columns.UUID()
    user_id = columns.UUID()
    currency = columns.Text()
    purchase_type = columns.Text()
    outcome = columns.Text()
    status = columns.Text(primary_key=True)
    created_date = columns.DateTime()
    amount = columns.Float()
    trade_type = columns.Text()


class TransactionsLevelsStatus(DjangoCassandraModel):
    transaction_id = columns.UUID()
    user_id = columns.UUID()
    outcome = columns.Text()
    status = columns.Text(primary_key=True)
    purchase_type = columns.Text()
    currency = columns.Text()
    amount_currency = columns.Text()
    created_date = columns.DateTime()
    amount = columns.Float()
    trade_type = columns.Text()
    start_time = columns.DateTime()
    end_time = columns.DateTime()
    available_levels = columns.List(columns.Integer())


class TransactionsByStartTime(DjangoCassandraModel):
    transaction_id = columns.UUID()
    user_id = columns.UUID()
    status = columns.Text(primary_key=True)
    start_time = columns.DateTime()


class TransactionsByEndTime(DjangoCassandraModel):
    transaction_id = columns.UUID()
    user_id = columns.UUID()
    status = columns.Text(primary_key=True)
    end_time = columns.DateTime()
    trade_type = columns.Text()


class TransactionsChangesAllowedTime(DjangoCassandraModel):
    transaction_id = columns.UUID()
    user_id = columns.UUID()
    status = columns.Text(primary_key=True)
    changes_allowed_time = columns.DateTime()


class LevelBasedUserCounts(DjangoCassandraModel):
    transaction_id = columns.UUID(primary_key=True)
    user_count = columns.Integer()
