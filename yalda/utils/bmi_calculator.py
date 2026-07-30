def calculate_bmi_info(height_cm: float, weight_kg: float):
    """
    محاسبه شاخص توده بدنی (BMI) و دسته مربوط به آن
    """
    try:
        height_cm = float(height_cm or 0.0)
        weight_kg = float(weight_kg or 0.0)
    except (ValueError, TypeError):
        return 0.0, "نامشخص", "#888888"

    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "نامشخص", "#888888"

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "کم‌وزن"
        color = "#3B82F6" # Blue
    elif 18.5 <= bmi < 25.0:
        category = "وزن طبیعی (نرمال)"
        color = "#10B981" # Green
    elif 25.0 <= bmi < 30.0:
        category = "اضافه وزن"
        color = "#F59E0B" # Orange/Yellow
    else:
        category = "چاقی"
        color = "#EF4444" # Red

    return bmi, category, color
