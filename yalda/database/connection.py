from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import config
from yalda.models.database_models import Base

engine = create_engine(config.DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))

def get_session():
    """Returns a new SQLAlchemy session."""
    return SessionLocal()

def check_and_migrate_db():
    """Checks and migrates new columns for existing SQLite database files."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "members" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("members")]
        with engine.connect() as conn:
            if "registration_date_shamsi" not in columns:
                conn.execute(text("ALTER TABLE members ADD COLUMN registration_date_shamsi VARCHAR(10);"))
            if "insurance_date_shamsi" not in columns:
                conn.execute(text("ALTER TABLE members ADD COLUMN insurance_date_shamsi VARCHAR(10);"))
            if "tuition_fee" not in columns:
                conn.execute(text("ALTER TABLE members ADD COLUMN tuition_fee FLOAT;"))
            if "job" not in columns:
                conn.execute(text("ALTER TABLE members ADD COLUMN job VARCHAR(100);"))
            conn.commit()

    if "physical_assessments" in inspector.get_table_names():
        pa_columns = [c["name"] for c in inspector.get_columns("physical_assessments")]
        with engine.connect() as conn:
            if "height_cm" not in pa_columns:
                conn.execute(text("ALTER TABLE physical_assessments ADD COLUMN height_cm FLOAT;"))
            conn.commit()



def init_db():
    """Creates database tables and seeds initial default data if needed."""
    Base.metadata.create_all(bind=engine)
    check_and_migrate_db()
    
    # Import and run seed data initialization
    from yalda.database.seed_data import seed_initial_data
    session = SessionLocal()
    try:
        seed_initial_data(session)
    finally:
        session.close()
