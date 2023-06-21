import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# init SQLAlchemy so we can use it later in our models
host = os.getenv('DB_HOST', "postgres-db-postgresql")
port = os.getenv('DB_PORT', "5432")
user = os.getenv('DB_USER', "root")
passWd = os.getenv('DB_PASS', "Portal2023")
db_name = os.getenv('DB_NAME', "driftnet_db")

url = URL.create(
    drivername="postgresql+psycopg2",
    username=user,
    password=passWd,
    host=host,
    port=port,
    database=db_name
)

engine = create_engine(url)

Session = sessionmaker(bind=engine)
session = Session()