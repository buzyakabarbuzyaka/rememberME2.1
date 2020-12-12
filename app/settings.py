import logging
import os
# from os.path import join, dirname
# from dotenv import load_dotenv

log = logging.getLogger()
log.setLevel(logging.DEBUG)

# load .env
# env = load_dotenv()

# load .secret
# secret_path = join(dirname(__file__), '..', '.secret')
# load_dotenv(secret_path)

# env from docker-compose env

APP_PORT = os.getenv('APP_PORT')


class PostgresConfiguration:
    POSTGRES_DB_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DB_NAME = os.getenv('POSTGRES_DB')
    POSTGRES_DB_LOGIN = os.getenv('POSTGRES_USER')
    POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB_ADDRESS = os.getenv('POSTGRES_ADDRESS')

    @property
    def postgres_db_path(self):
        return f'postgres://{self.POSTGRES_DB_LOGIN}:{self.POSTGRES_DB_PASSWORD}@' \
               f'{self.POSTGRES_DB_ADDRESS}:' \
               f'{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB_NAME}'


if __name__ == "__main__":
    print(f"{os.getenv('POSTGRES_PASSWORD')}")
