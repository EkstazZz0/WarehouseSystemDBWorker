import os


application_environment = os.getenv("APP_ENV", "dev")

db_logs = False

if application_environment == "dev":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    db_logs = True

db_connect_url = "postgresql+psycopg2://" + os.getenv("POSTGRES_USER", "postgres") + ":" + os.getenv("POSTGRES_PASSWORD", "123456") + "@" + os.getenv("DB_HOST", "localhost") + ":" + os.getenv("DB_PORT", "5432") + "/" + os.getenv("POSTGRES_DB", "postgres")

db_connect_configuration = {
    "url": db_connect_url,
    "connect_args": {},
    "echo": db_logs
}

kafka_consumer_config = {
    'bootstrap.servers': os.getenv("KAFKA_HOST", "localhost:9092"),
    'group.id': 'order_status_updater',
    'auto.offset.reset': 'earliest',
}

kafka_consumer_topics = ["db_work"]

time_zone = os.getenv("TZ")