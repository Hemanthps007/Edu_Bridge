from django.db import models
import json

class User(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('counselor', 'Counselor'),
        ('university', 'University Rep'),
        ('mentor', 'Mentor'),
        ('admin', 'Administrator'),
    ]

    uid = models.CharField(max_length=64, unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    degree = models.CharField(max_length=60, default='MS')
    country_goal = models.CharField(max_length=60, default='USA')
    points = models.IntegerField(default=10)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=1)
    journey_stage = models.CharField(max_length=40, default='exploration')
    face_descriptors = models.TextField(blank=True, null=True, help_text="Encrypted face descriptor vector (JSON)")
    face_auth_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    failed_attempts = models.IntegerField(default=0)
    profile_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"


class University(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    country = models.CharField(max_length=80, db_index=True)
    city = models.CharField(max_length=80)
    qs_ranking = models.IntegerField(default=999)
    the_ranking = models.IntegerField(default=999)
    tuition_usd = models.IntegerField(default=35000)
    living_cost_usd = models.IntegerField(default=15000)
    acceptance_rate = models.FloatField(default=25.0)
    application_deadline = models.CharField(max_length=50, default="January 15")
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    admission_requirements = models.JSONField(default=dict, blank=True)
    popular_programs = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.country}) - #{self.qs_ranking}"


class Course(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=200)
    degree_level = models.CharField(max_length=50, default='Masters')
    duration_years = models.FloatField(default=2.0)
    tuition_usd = models.IntegerField(default=35000)
    requirements = models.JSONField(default=dict, blank=True)
    intake_months = models.JSONField(default=list, blank=True)
    career_outcomes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.course_name} at {self.university.name}"


class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=80, default="Global")
    university_name = models.CharField(max_length=200, blank=True, default="Multiple Universities")
    amount_usd = models.IntegerField(default=10000)
    amount_display = models.CharField(max_length=100, default="$10,000 / Full Tuition")
    eligibility_criteria = models.JSONField(default=dict, blank=True)
    deadline = models.CharField(max_length=60, default="Rolling / November 2026")
    application_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=60, default="Merit-based")

    def __str__(self):
        return f"{self.name} ({self.amount_display})"


class LoanProvider(models.Model):
    bank_name = models.CharField(max_length=120)
    country = models.CharField(max_length=60, default="India")
    interest_rate_min = models.FloatField(default=9.5)
    interest_rate_max = models.FloatField(default=12.5)
    max_loan_inr = models.BigIntegerField(default=7500000)
    tenure_years = models.IntegerField(default=10)
    processing_fee_pct = models.FloatField(default=1.0)
    collateral_required = models.CharField(max_length=80, default="No")
    approval_turnaround_days = models.CharField(max_length=30, default="3-5 days")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bank_name} ({self.interest_rate_min}% - {self.interest_rate_max}%)"


class Application(models.Model):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('documents_pending', 'Documents Pending'),
        ('in_review', 'In Review'),
        ('submitted', 'Submitted'),
        ('interview', 'Interview Scheduled'),
        ('admitted', 'Admitted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    ]

    uid = models.CharField(max_length=64, db_index=True)
    university_name = models.CharField(max_length=200)
    program_name = models.CharField(max_length=200)
    term = models.CharField(max_length=40, default="Fall 2026")
    deadline = models.CharField(max_length=60, default="Dec 15, 2026")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='shortlisted')
    checklist = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uid} - {self.university_name} ({self.status})"


class Mentor(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    company_or_uni = models.CharField(max_length=150)
    country = models.CharField(max_length=60, default="USA")
    experience_years = models.IntegerField(default=5)
    specializations = models.JSONField(default=list, blank=True)
    hourly_rate_inr = models.IntegerField(default=750)
    rating = models.FloatField(default=4.9)
    sessions_completed = models.IntegerField(default=42)
    bio = models.TextField()
    avatar_initials = models.CharField(max_length=4, default="ME")
    calendly_link = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.title}"


class MentorSession(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    student_uid = models.CharField(max_length=64)
    student_name = models.CharField(max_length=120)
    scheduled_at = models.DateTimeField()
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default='scheduled')
    session_link = models.URLField(blank=True)


class Notification(models.Model):
    uid = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=40, default='info')
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{'READ' if self.is_read else 'UNREAD'}] {self.title}"
