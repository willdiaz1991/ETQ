from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from config.config import Config
from infrastructure.logging.LoggerImplements import LoggerImplements

from .decrypt import decrypt

log_impl = LoggerImplements("DbContextLogger")
config = Config()

DB_CONFIGS = {"sgl": decrypt(config.get("DB_SGL"))}
SESSIONS = {}

# Initialize SQLAlchemy engines and sessions
for name, url in DB_CONFIGS.items():
    try:
        make_url(url)
    except Exception as e:
        log_impl.log_error("Invalid database URL", "make_url", f"name: {name}")

    engine = create_engine(
        url,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
    SESSIONS[name] = sessionmaker(bind=engine)


@contextmanager
def get_db_session(db_name):
    """
    Context manager to retrieve a session for the specified database.
    Usage:
        with get_db_session("sgl") as session:
            session.execute(...)
    """
    Session = SESSIONS.get(db_name)
    if not Session:
        log_impl.log_error("Database is not configured", "get_db_session", f"db name: {db_name}")
        yield None
        return

    session = Session()
    log_impl.log_information("Opened session", "get_db_session", f"db name: {db_name}")

    try:
        yield session
    finally:
        session.close()
        log_impl.log_information("Closed session", "get_db_session", f"db name: {db_name}")


def get_available_databases():
    """
    Returns the list of configured databases.
    """
    return list(SESSIONS.keys())
