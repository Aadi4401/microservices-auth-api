
from sqlalchemy import Table, Column, String, MetaData,Integer,DateTime,Boolean
from sqlalchemy import func

metadata = MetaData()

USER = Table(
    "tbl_user",
    metadata,
    Column("id", Integer,primary_key=True, autoincrement=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("email", String),
    Column("password", String),
    Column("emailotp", String),
    Column("reset_otp", String),
    Column("login_otp", String),
    Column("phone_number", String),
    Column("is_verified",Boolean, default=False)
)
