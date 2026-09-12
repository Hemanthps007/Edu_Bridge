from typing import Dict, Any, List
from datetime import datetime, timedelta

def generate_study_plan(exam_targets: List[str] = None, hours_per_week: int = 15) -> Dict[str, Any]:
    """
    Generates a structured multi-week study planner and milestone timetable.
    """
    if not exam_targets:
        exam_targets = ["GRE Quant & Verbal", "IELTS Academic", "Machine Learning Foundations"]

    daily_hours = round(hours_per_week / 6, 1)

    schedule = [
        {"day": "Monday", "focus": "Quantitative Reasoning & Problem Solving", "hours": daily_hours, "tasks": ["30 Quant questions (Algebra & Geometry)", "Flashcards review (Verbal 50 words)"]},
        {"day": "Tuesday", "focus": "Verbal Reasoning & Reading Comprehension", "hours": daily_hours, "tasks": ["3 Long RC passages analysis", "Text Completion drill"]},
        {"day": "Wednesday", "focus": "Core Domain / Mathematics Foundations", "hours": daily_hours, "tasks": ["Linear Algebra chapter review", "Coding implementation in Python"]},
        {"day": "Thursday", "focus": "English Proficiency & Writing Practice", "hours": daily_hours, "tasks": ["IELTS Task 2 essay timed practice", "Listening practice section 3 & 4"]},
        {"day": "Friday", "focus": "Timed Practice Drills & Weak Area Revision", "hours": daily_hours, "tasks": ["Review error log from Tuesday", "Speed calculation exercises"]},
        {"day": "Saturday", "focus": "Full-Length Mock Test & Strategy Review", "hours": round(daily_hours * 1.5, 1), "tasks": ["Simulated test section (timed)", "Detailed question-by-question post-mortem"]},
        {"day": "Sunday", "focus": "Rest & Light Strategy Planning", "hours": 0.5, "tasks": ["Weekly review and planner update for next week"]}
    ]

    upcoming_deadlines = [
        {"name": "GRE Standardized Exam", "days_left": 18, "date": (datetime.now() + timedelta(days=18)).strftime("%b %d, %Y"), "urgency": "high"},
        {"name": "IELTS Academic Test", "days_left": 32, "date": (datetime.now() + timedelta(days=32)).strftime("%b %d, %Y"), "urgency": "medium"},
        {"name": "University Fall Intake Application Deadline", "days_left": 65, "date": (datetime.now() + timedelta(days=65)).strftime("%b %d, %Y"), "urgency": "normal"}
    ]

    return {
        "weekly_hours_target": hours_per_week,
        "weekly_completion_pct": 78,
        "upcoming_deadlines": upcoming_deadlines,
        "weekly_schedule": schedule,
        "exam_targets": exam_targets
    }
