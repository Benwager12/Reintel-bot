import psycopg2
from helpers.config import config


DATABASE_URL = config['DATABASE_URL']

connection = psycopg2.connect(DATABASE_URL, sslmode="require")
