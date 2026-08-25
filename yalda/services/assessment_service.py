from yalda.database.connection import get_session, mark_data_changed
from yalda.models.database_models import PhysicalAssessment, Member
from yalda.utils.jalali_date import get_today_shamsi

class AssessmentService:
    @staticmethod
    def add_assessment(member_id: int, data: dict) -> PhysicalAssessment:
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            input_height = float(data.get("height_cm", 0.0) or 0.0)
            height_cm = input_height if input_height > 0 else (member.height_cm if member else 0.0)
            
            weight_kg = float(data.get("weight_kg", 0.0) or 0.0)
            bmi = 0.0
            if height_cm and height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100.0
                bmi = round(weight_kg / (height_m * height_m), 1)

            assessment = PhysicalAssessment(
                member_id=member_id,
                assessment_date_shamsi=data.get("assessment_date_shamsi") or get_today_shamsi(),
                height_cm=input_height if input_height > 0 else None,
                weight_kg=weight_kg,
                body_fat_percentage=float(data.get("body_fat_percentage", 0.0) or 0.0),
                bmi=bmi,
                neck_circ=float(data.get("neck_circ", 0.0) or 0.0),
                chest_circ=float(data.get("chest_circ", 0.0) or 0.0),
                arm_circ=float(data.get("arm_circ", 0.0) or 0.0),
                abdomen_circ=float(data.get("abdomen_circ", 0.0) or 0.0),
                waist_circ=float(data.get("waist_circ", 0.0) or 0.0),
                hip_circ=float(data.get("hip_circ", 0.0) or 0.0),
                thigh_circ=float(data.get("thigh_circ", 0.0) or 0.0),
                before_photo_path=data.get("before_photo_path"),
                after_photo_path=data.get("after_photo_path"),
                notes=data.get("notes")
            )
            session.add(assessment)
            session.commit()
            mark_data_changed()
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
                "height_diff": round((getattr(a2, 'height_cm', None) or 0) - (getattr(a1, 'height_cm', None) or 0), 1),
                "weight_diff": round(a2.weight_kg - a1.weight_kg, 1),
                "fat_diff": round((a2.body_fat_percentage or 0) - (a1.body_fat_percentage or 0), 1),
                "bmi_diff": round((a2.bmi or 0) - (a1.bmi or 0), 1),
                "neck_diff": round((a2.neck_circ or 0) - (a1.neck_circ or 0), 1),
                "chest_diff": round((a2.chest_circ or 0) - (a1.chest_circ or 0), 1),
                "arm_diff": round((a2.arm_circ or 0) - (a1.arm_circ or 0), 1),
                "abdomen_diff": round((a2.abdomen_circ or 0) - (a1.abdomen_circ or 0), 1),
                "waist_diff": round((a2.waist_circ or 0) - (a1.waist_circ or 0), 1),
                "hip_diff": round((a2.hip_circ or 0) - (a1.hip_circ or 0), 1),
                "thigh_diff": round((a2.thigh_circ or 0) - (a1.thigh_circ or 0), 1),
            }
            return {"first": a1, "second": a2, "diff": diff}
        finally:
            session.close()

    @staticmethod
    def update_assessment(assessment_id: int, data: dict) -> bool:
        session = get_session()
        try:
            assessment = session.query(PhysicalAssessment).filter(PhysicalAssessment.id == assessment_id).first()
            if not assessment:
                return False
            
            member = session.query(Member).filter(Member.id == assessment.member_id).first()
            input_height = float(data.get("height_cm", 0.0) or 0.0)
            height_cm = input_height if input_height > 0 else (member.height_cm if member else 0.0)
            weight_kg = float(data.get("weight_kg", 0.0) or 0.0)
            bmi = 0.0
            if height_cm and height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100.0
                bmi = round(weight_kg / (height_m * height_m), 1)

            if "assessment_date_shamsi" in data and data["assessment_date_shamsi"]:
                assessment.assessment_date_shamsi = data["assessment_date_shamsi"]
            assessment.height_cm = input_height if input_height > 0 else None
            assessment.weight_kg = weight_kg
            assessment.body_fat_percentage = float(data.get("body_fat_percentage", 0.0) or 0.0)
            assessment.bmi = bmi
            assessment.neck_circ = float(data.get("neck_circ", 0.0) or 0.0)
            assessment.chest_circ = float(data.get("chest_circ", 0.0) or 0.0)
            assessment.arm_circ = float(data.get("arm_circ", 0.0) or 0.0)
            assessment.abdomen_circ = float(data.get("abdomen_circ", 0.0) or 0.0)
            assessment.waist_circ = float(data.get("waist_circ", 0.0) or 0.0)
            assessment.hip_circ = float(data.get("hip_circ", 0.0) or 0.0)
            assessment.thigh_circ = float(data.get("thigh_circ", 0.0) or 0.0)
            if "before_photo_path" in data and data["before_photo_path"] is not None:
                assessment.before_photo_path = data["before_photo_path"]
            if "after_photo_path" in data and data["after_photo_path"] is not None:
                assessment.after_photo_path = data["after_photo_path"]
            
            session.commit()
            mark_data_changed()
            return True
        finally:
            session.close()

    @staticmethod
    def delete_assessment(assessment_id: int) -> bool:
        session = get_session()
        try:
            assessment = session.query(PhysicalAssessment).filter(PhysicalAssessment.id == assessment_id).first()
            if assessment:
                session.delete(assessment)
                session.commit()
                mark_data_changed()
                return True
            return False
        finally:
            session.close()
