import os
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config
from yalda.utils.jalali_date import get_today_shamsi

def reshape_text(text: str) -> str:
    """Helper to reshape Persian text and apply BiDi algorithm for ReportLab rendering."""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except Exception:
        return str(text)

# Register TTF Font for Persian PDF rendering
FONT_NAME = "Helvetica"
def setup_fonts():
    global FONT_NAME
    candidate_paths = [
        config.BASE_DIR / "resources" / "fonts" / "Vazirmatn-Regular.ttf",
        Path("C:/Windows/Fonts/tahoma.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf")
    ]
    for path in candidate_paths:
        if path.exists():
            try:
                font_id = "PersianFont"
                pdfmetrics.registerFont(TTFont(font_id, str(path)))
                FONT_NAME = font_id
                return
            except Exception:
                continue

    FONT_NAME = 'Helvetica'

setup_fonts()

class PDFGenerator:
    @staticmethod
    def _create_header_footer(canvas_obj, doc):
        canvas_obj.saveState()
        # Draw dark red top bar
        canvas_obj.setFillColor(colors.HexColor(config.COLOR_PRIMARY_ACCENT))
        canvas_obj.rect(0, doc.height + doc.topMargin + 10, doc.width + doc.leftMargin + doc.rightMargin, 15, fill=1, stroke=0)
        
        # Footer
        canvas_obj.setFillColor(colors.HexColor("#666666"))
        canvas_obj.setFont(FONT_NAME, 9)
        footer_text = reshape_text(f"نرم‌افزار مدیریت باشگاه بدنسازی یلدا  |  تاریخ چاپ: {get_today_shamsi()}")
        canvas_obj.drawRightString(doc.width + doc.leftMargin, 20, footer_text)
        canvas_obj.restoreState()

    @staticmethod
    def generate_workout_pdf(member, workout_plan, output_filepath: str):
        """Generates printable PDF for Member's Workout Plan."""
        setup_fonts()
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=18,
            leading=22,
            alignment=1, # Center
            textColor=colors.HexColor(config.COLOR_PRIMARY_ACCENT)
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=11,
            leading=16,
            alignment=2, # Right
            textColor=colors.HexColor("#333333")
        )
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            alignment=2 # Right
        )
        cell_header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            alignment=1, # Center
            textColor=colors.white
        )

        # Title
        elements.append(Paragraph(reshape_text(f"برنامه تمرینی باشگاه بدنسازی یلدا"), title_style))
        elements.append(Spacer(1, 10))

        # Member Info Box Table
        info_data = [
            [
                Paragraph(reshape_text(f"هدف: {workout_plan.goal}"), subtitle_style),
                Paragraph(reshape_text(f"نام ورزشکار: {member.full_name}"), subtitle_style)
            ],
            [
                Paragraph(reshape_text(f"تعداد روزهای تمرین: {workout_plan.days_per_week} روز در هفته"), subtitle_style),
                Paragraph(reshape_text(f"تاریخ انقضای عضویت: {member.membership_expire_shamsi}"), subtitle_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[260, 260])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F5F5F5")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # Days and Exercises
        for day in workout_plan.days:
            day_title = Paragraph(reshape_text(f"◄ {day.day_title}"), ParagraphStyle('DayTitle', fontName=FONT_NAME, fontSize=12, textColor=colors.HexColor(config.COLOR_PRIMARY_ACCENT)))
            elements.append(day_title)
            elements.append(Spacer(1, 5))

            table_data = [[
                Paragraph(reshape_text("توضیحات / ریتم"), cell_header_style),
                Paragraph(reshape_text("زمان استراحت"), cell_header_style),
                Paragraph(reshape_text("وزنه (کیلو)"), cell_header_style),
                Paragraph(reshape_text("تکرار"), cell_header_style),
                Paragraph(reshape_text("ست"), cell_header_style),
                Paragraph(reshape_text("نام حرکت ورزشی"), cell_header_style),
                Paragraph(reshape_text("ردیف"), cell_header_style),
            ]]

            for idx, we in enumerate(day.workout_exercises, start=1):
                ex_name = we.exercise.name_fa if we.exercise else "-"
                table_data.append([
                    Paragraph(reshape_text(f"{we.tempo or '-'} / {we.trainer_notes or ''}"), cell_style),
                    Paragraph(reshape_text(f"{we.rest_seconds} ثانیه"), cell_style),
                    Paragraph(reshape_text(str(we.weight_suggestion or "-")), cell_style),
                    Paragraph(reshape_text(str(we.reps)), cell_style),
                    Paragraph(reshape_text(str(we.sets)), cell_style),
                    Paragraph(reshape_text(ex_name), cell_style),
                    Paragraph(reshape_text(str(idx)), cell_style),
                ])

            t = Table(table_data, colWidths=[100, 70, 60, 50, 40, 160, 40])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor(config.COLOR_PRIMARY_ACCENT)),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))

        doc.build(elements, onFirstPage=PDFGenerator._create_header_footer, onLaterPages=PDFGenerator._create_header_footer)
        return output_filepath

    @staticmethod
    def generate_nutrition_pdf(member, nutrition_plan, output_filepath: str):
        """Generates printable PDF for Member's Nutrition Plan."""
        setup_fonts()
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=18,
            leading=22,
            alignment=1,
            textColor=colors.HexColor(config.COLOR_PRIMARY_ACCENT)
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=11,
            leading=16,
            alignment=2
        )
        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10, leading=14, alignment=2)
        cell_header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10, leading=14, alignment=1, textColor=colors.white)

        elements.append(Paragraph(reshape_text(f"برنامه غذایی و رژیمی باشگاه بدنسازی یلدا"), title_style))
        elements.append(Spacer(1, 10))

        # Target Macros Box
        macro_text = f"کالری هدف: {int(nutrition_plan.target_calories)} ک‌کال | پروتئین: {int(nutrition_plan.target_protein)}g | کربوهیدرات: {int(nutrition_plan.target_carbs)}g | چربی: {int(nutrition_plan.target_fat)}g"
        info_data = [
            [
                Paragraph(reshape_text(f"هدف برنامه: {nutrition_plan.goal}"), subtitle_style),
                Paragraph(reshape_text(f"نام ورزشکار: {member.full_name}"), subtitle_style)
            ],
            [
                Paragraph(reshape_text(macro_text), subtitle_style),
                Paragraph(reshape_text(f"عنوان برنامه: {nutrition_plan.title}"), subtitle_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[260, 260])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F5F5F5")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        meal_names_map = {
            "breakfast": "صبحانه",
            "morning_snack": "میان‌وعده صبح",
            "lunch": "ناهار",
            "afternoon_snack": "عصرانه",
            "dinner": "شام",
            "evening_snack": "قبل از خواب"
        }

        for meal in nutrition_plan.meals:
            fa_meal_name = meal_names_map.get(meal.meal_name, meal.meal_name)
            meal_header = Paragraph(reshape_text(f"◄ وعده: {fa_meal_name}"), ParagraphStyle('MealTitle', fontName=FONT_NAME, fontSize=12, textColor=colors.HexColor(config.COLOR_PRIMARY_ACCENT)))
            elements.append(meal_header)
            elements.append(Spacer(1, 5))

            table_data = [[
                Paragraph(reshape_text("توضیحات مربی"), cell_header_style),
                Paragraph(reshape_text("مقدار / واحد"), cell_header_style),
                Paragraph(reshape_text("نام ماده غذایی"), cell_header_style),
                Paragraph(reshape_text("ردیف"), cell_header_style),
            ]]

            for idx, item in enumerate(meal.items, start=1):
                food_name = item.food.name_fa if item.food else "-"
                table_data.append([
                    Paragraph(reshape_text(item.notes or "-"), cell_style),
                    Paragraph(reshape_text(f"{item.amount} {item.unit or item.food.unit}"), cell_style),
                    Paragraph(reshape_text(food_name), cell_style),
                    Paragraph(reshape_text(str(idx)), cell_style),
                ])

            t = Table(table_data, colWidths=[180, 120, 180, 40])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor(config.COLOR_PRIMARY_ACCENT)),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))

        doc.build(elements, onFirstPage=PDFGenerator._create_header_footer, onLaterPages=PDFGenerator._create_header_footer)
        return output_filepath
