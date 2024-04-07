# db.py
from datetime import datetime
from os import environ

import psycopg
from psycopg import OperationalError, ProgrammingError, IntegrityError

database = environ.get("POSTGRES_DB")
user = environ.get("POSTGRES_USER")
password = environ.get("POSTGRES_PASSWORD")

db_params = f"dbname={database} user={user} password={password} host=postgres_db"


def insert_task(id, result, state) -> None:
    try:
        with psycopg.connect(db_params) as conn:
            with conn.cursor() as cur:
                insert_query = "INSERT INTO task_results (task_id, result, state, created_at) VALUES (%s, %s, %s, %s);"
                cur.execute(insert_query, (id, result, state, datetime.utcnow()))
    except (OperationalError, ProgrammingError, IntegrityError) as e:
        print(f"Database error: {e}")


def fetch_tasks() -> list[tuple]:
    try:
        with psycopg.connect(db_params) as conn:
            with conn.cursor() as cur:
                fetch_query = "SELECT task_id, result, state FROM task_results;"
                cur.execute(fetch_query)
                tasks = cur.fetchall()
                return tasks
    except (OperationalError, ProgrammingError, IntegrityError) as e:
        print(f"Database error: {e}")
        return []
