from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from app.settings import PostgresConfiguration

pg = PostgresConfiguration()
path = pg.postgres_db_path
# path_mock = 'postgres://postgres:postgres@0.0.0.0:5432/users_data'

engine = create_engine(path)
# engine = create_engine(path_mock)
if not database_exists(engine.url):
    # print(f"Creating {pg.POSTGRES_DB_NAME}")
    print(f"Creating {path_mock}")
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if __name__ == "__main__":
    print(f'{path}')
    # print(f'{path_mock}')
