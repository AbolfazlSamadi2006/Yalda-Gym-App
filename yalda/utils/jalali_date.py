import jdatetime
from datetime import datetime

def get_today_shamsi() -> str:
    """Returns today's date in Shamsi format: YYYY/MM/DD"""
    now = jdatetime.date.today()
    return now.strftime("%Y/%m/%d")

def format_shamsi(date_str: str) -> str:
    """Ensures YYYY/MM/DD format with leading zeros"""
    if not date_str:
        return ""
    parts = date_str.replace("-", "/").split("/")
    if len(parts) == 3:
        y, m, d = parts
        return f"{int(y):04d}/{int(m):02d}/{int(d):02d}"
    return date_str

def parse_shamsi(shamsi_str: str) -> jdatetime.date:
    """Parses YYYY/MM/DD into a jdatetime.date object"""
    clean_str = format_shamsi(shamsi_str)
    parts = clean_str.split("/")
    return jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))

def shamsi_to_gregorian(shamsi_str: str) -> datetime:
    """Converts a Shamsi date string (YYYY/MM/DD) to Python datetime"""
    j_date = parse_shamsi(shamsi_str)
    g_date = j_date.togregorian()
    return datetime.combine(g_date, datetime.min.time())

def gregorian_to_shamsi(dt: datetime) -> str:
    """Converts Python datetime to Shamsi date string"""
    if isinstance(dt, datetime):
        g_date = dt.date()
    else:
        g_date = dt
    j_date = jdatetime.date.fromgregorian(date=g_date)
    return j_date.strftime("%Y/%m/%d")

def add_days_shamsi(shamsi_str: str, days: int) -> str:
    """Adds N days to a Shamsi date string"""
    j_date = parse_shamsi(shamsi_str)
    new_date = j_date + jdatetime.timedelta(days=days)
    return new_date.strftime("%Y/%m/%d")

def add_months_shamsi(shamsi_str: str, months: int) -> str:
    """Adds N months to a Shamsi date string"""
    j_date = parse_shamsi(shamsi_str)
    month = j_date.month + months
    year = j_date.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(j_date.day, 29 if month == 12 else 30 if month > 6 else 31)
    new_date = jdatetime.date(year, month, day)
    return new_date.strftime("%Y/%m/%d")

def calculate_age_from_shamsi(birth_shamsi_str: str) -> int:
    """Calculates age in years from Shamsi birth date"""
    if not birth_shamsi_str:
        return 0
    try:
        b_date = parse_shamsi(birth_shamsi_str)
        today = jdatetime.date.today()
        age = today.year - b_date.year
        if (today.month, today.day) < (b_date.month, b_date.day):
            age -= 1
        return max(0, age)
    except Exception:
        return 0

def days_until_expire(expire_shamsi_str: str) -> int:
    """Returns number of days remaining until expiration"""
    if not expire_shamsi_str:
        return -999
    try:
        exp_date = parse_shamsi(expire_shamsi_str)
        today = jdatetime.date.today()
        delta = (exp_date - today).days
        return delta
    except Exception:
        return -999

def is_membership_active(expire_shamsi_str: str) -> bool:
    """Checks whether membership is active today"""
    return days_until_expire(expire_shamsi_str) >= 0
