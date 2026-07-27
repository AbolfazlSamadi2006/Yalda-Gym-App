from yalda.database.connection import get_session
from yalda.models.database_models import PhysicalAssessment, Member
from yalda.utils.jalali_date import get_today_shamsi

class AssessmentService:
    @staticmethod
    def add_assessment(member_id: int, data: dict) -> PhysicalAssessment:
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            height_cm = member.height_cm if member else 0.0
            
            weight_kg = float(data.get("weight_kg", 0.0) or 0.0)
            bmi = 0.0
            if height_cm and height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100.0
                bmi = round(weight_kg / (height_m * height_m), 1)

            assessment = PhysicalAssessment(
                member_id=member_id,
                assessment_date_shamsi=data.get("assessment_date_shamsi") or get_today_shamsi(),
                weight_kg=weight_kg,
                body_fat_percentage=float(data.get("body_fat_percentage", 0.0) or 0.0),
                bmi=bmi,
                arm_circ=float(data.get("arm_circ", 0.0) or 0.0),
                chest_circ=float(data.get("chest_circ", 0.0) or 0.0),
                waist_circ=float(data.get("waist_circ", 0.0) or 0.0),
                thigh_circ=float(data.get("thigh_circ", 0.0) or 0.0),
                before_photo_path=data.get("before_photo_path"),
                after_photo_path=data.get("after_photo_path"),
                notes=data.get("notes")
            )
            session.add(assessment)
            session.commit()
            return assessment
        finally:
            session.close()

    @staticmethod
    def get_member_assessments(member_id: int):
        session = get_session()
        try:
            return session.query(PhysicalAssessment)\
                .filter(PhysicalAssessment.member_id == member_id)\
                .order_by(PhysicalAssessment.id.desc())\
                .all()
        finally:
            session.close()

    @staticmethod
    def compare_assessments(id_first: int, id_second: int):
        session = get_session()
        try:
            a1 = session.query(PhysicalAssessment).filter(PhysicalAssessment.id == id_first).first()
            a2 = session.query(PhysicalAssessment).filter(PhysicalAssessment.id == id_second).first()
            if not a1 or not a2:
                return None
            
            diff = {
                "weight_diff": round(a2.weight_kg - a1.weight_kg, 1),
                "fat_diff": round((a2.body_fat_percentage or 0) - (a1.body_fat_percentage or 0), 1),
                "bmi_diff": round((a2.bmi or 0) - (a1.bmi or 0), 1),
                "arm_diff": round((a2.arm_circ or 0) - (a1.arm_circ or 0), 1),
                "chest_diff": round((a2.chest_circ or 0) - (a1.chest_circ or 0), 1),
                "waist_diff": round((a2.waist_circ or 0) - (a1.waist_circ or 0), 1),
                "thigh_diff": round((a2.thigh_circ or 0) - (a1.thigh_circ or 0), 1),
            }
            return {"first": a1, "second": a2, "diff": diff}
        finally:
            session.close()
