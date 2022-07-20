import psycopg2
from helpers.config import config


DATABASE_URL = config['DATABASE_URL']
DB_URL = DATABASE_URL  # Used for checking for changes in the config file.

connection = psycopg2.connect(DATABASE_URL, sslmode="require")