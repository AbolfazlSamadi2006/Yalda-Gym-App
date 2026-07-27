from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import config
from yalda.models.database_models import Base

engine = create_engine(config.DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))

def get_session():
    """Returns a new SQLAlchemy session."""
    return SessionLocal()

def init_db():
    """Creates database tables and seeds initial default data if needed."""
    Base.metadata.create_all(bind=engine)
    
    # Import and run seed data initialization
    from yalda.database.seed_data import seed_initial_data
    session = SessionLocal()
    try:
        seed_initial_data(session)
    finally:
        session.close()
