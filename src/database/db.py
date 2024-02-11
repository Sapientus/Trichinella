from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    A context manager function for handling database sessions.

    This function initializes a database session using SessionLocal() and yields the session object
    within a try block. If an exception occurs during the execution of the block, the session is rolled
    back to its original state using db.rollback(). Finally, the session is closed to release resources.

    :return: A context manager yielding a database session object.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(e)
        db.rollback()
    finally:
        db.close()
