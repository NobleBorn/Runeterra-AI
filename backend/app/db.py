
import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn
