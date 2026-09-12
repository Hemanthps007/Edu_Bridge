import json
import uuid
import hashlib
import math
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from . import firebase_client as fb
from .decorators import role_required
from services.data_providers.curated import CuratedDataProvider
from services.data_providers.college_scorecard import CollegeScorecardProvider
from utils.profile_scorer import calculate_profile_scores
from utils.career_matcher import score_riasec
from .admission_predictor import admission_predictor
from utils.roi_engine import calculate_advanced_roi
from utils.loan_calculator import get_loan_options, calculate_emi, LENDER_CATALOG
from utils.scholarship_matcher import match_scholarships, SCHOLARSHIPS_DATA
from services.ai_document_analyzer import analyze_sop_content
from services.rag_service import answer_rag_query
from services.study_planner import generate_study_plan
from utils.gamification import calculate_gamification_state, award_xp

data_provider = CollegeScorecardProvider()

# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(fn):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user'):
            messages.warning(request, 'Please sign in to access your StudyBridge account.')
            return redirect('login')
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def _calculate_vector_distance(vec1, vec2):
    """Calculates Euclidean distance between two face descriptor vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 1.0
    sq_sum = sum((a - b) ** 2 for a, b in zip(vec1, vec2))
    return math.sqrt(sq_sum)


# ── Authentication & Biometrics ──────────────────────────────────────────────

def landing(request):
    if request.session.get('user'):
        return redirect('dashboard')
    top_unis = data_provider.search_universities(limit=6)
    return render(request, 'landing.html', {'top_unis': top_unis})


def register_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        pw = request.POST.get('password', '')
        role = request.POST.get('role', 'student')
        degree = request.POST.get('degree', 'MS')
        country_goal = request.POST.get('country_goal', 'USA')

        if not all([name, email, pw]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        uid = hashlib.md5(email.encode()).hexdigest()
        if fb.get_user_profile(uid):
            messages.error(request, 'An account already exists with this email address.')
            return render(request, 'register.html')

        profile = {
            'uid': uid,
            'name': name,
            'email': email,
            'password_hash': _hash(pw),
            'role': role,
            'degree': degree,
            'country_goal': country_goal,
            'points': 50,
            'level': 1,
            'streak': 1,
            'badges': ['profile_complete'],
            'journey_stage': 'exploration',
            'created_at': datetime.now().isoformat(),
            'failed_attempts': 0,
            'face_auth_enabled': False,
        }
        fb.save_user_profile(uid, profile)
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        fb.log_user_login(uid, email, ip_address, user_agent)
        fb.add_notification(uid, "Welcome to StudyBridge", "Your account is created. Complete your student profile for personalized admissions insight.", "info", "/profile/")

        request.session['user'] = {'uid': uid, 'name': name, 'email': email, 'role': role}
        messages.success(request, f'Welcome to StudyBridge, {name}! +50 XP awarded.')
        return redirect('onboarding')
    return render(request, 'register.html')


def login_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        pw = request.POST.get('password', '')
        uid = hashlib.md5(email.encode()).hexdigest()
        profile = fb.get_user_profile(uid)

        if profile:
            failed = profile.get('failed_attempts', 0)
            if failed >= 5:
                messages.error(request, 'This account is temporarily locked due to excessive failed attempts.')
                return render(request, 'login.html')

            if profile.get('password_hash') == _hash(pw):
                profile['failed_attempts'] = 0
                fb.save_user_profile(uid, profile)
                request.session['user'] = {
                    'uid': uid,
                    'name': profile.get('name', email),
                    'email': email,
                    'role': profile.get('role', 'student')
                }
                ip_address = request.META.get('REMOTE_ADDR', '')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                fb.log_user_login(uid, email, ip_address, user_agent)
                messages.success(request, f"Welcome back, {profile.get('name')}!")
                return redirect('dashboard')
            else:
                failed += 1
                profile['failed_attempts'] = failed
                fb.save_user_profile(uid, profile)
                messages.error(request, f'Invalid email or password. {5 - failed} trials remaining.')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('landing')


@csrf_exempt
def verify_face_auth(request):
    """Verifies captured browser face descriptor against enrolled biometric signature."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        descriptor = data.get('descriptor')

        if not email or not descriptor:
            return JsonResponse({'success': False, 'error': 'Email and biometric descriptor are required.'}, status=400)

        uid = hashlib.md5(email.encode()).hexdigest()
        profile = fb.get_user_profile(uid)
        if not profile:
            return JsonResponse({'success': False, 'error': 'No account associated with this email address.'}, status=404)

        cred = fb.get_face_credential(uid)
        if not cred or not cred.get('descriptors'):
            return JsonResponse({'success': False, 'error': 'Face ID is not enrolled for this account. Please sign in with password first.'}, status=400)

        stored_descriptor = cred.get('descriptors')
        distance = _calculate_vector_distance(descriptor, stored_descriptor)
        confidence = max(0.0, min(100.0, (1.0 - (distance / 0.65)) * 100.0))

        # Strict match threshold: distance <= 0.55
        if distance <= 0.55 or confidence >= 80.0:
            request.session['user'] = {
                'uid': uid,
                'name': profile.get('name', email),
                'email': email,
                'role': profile.get('role', 'student')
            }
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            fb.log_user_login(uid, email, ip_address, user_agent)
            return JsonResponse({
                'success': True,
                'confidence': round(confidence, 1),
                'redirect': '/dashboard/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Biometric face verification failed (confidence {confidence:.1f}%). Please use password.'
            }, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def enroll_face_auth(request):
    """Enrolls or updates webcam face recognition descriptor."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        descriptor = data.get('descriptor')
        if not descriptor or len(descriptor) != 128:
            return JsonResponse({'success': False, 'error': 'Invalid 128-dimensional face descriptor.'}, status=400)

        uid = request.session['user']['uid']
        fb.save_face_credential(uid, descriptor)
        profile = fb.get_user_profile(uid) or {}
        profile['face_auth_enabled'] = True
        profile = award_xp(profile, 'face_auth', 150, 'biometric_secured')
        fb.save_user_profile(uid, profile)

        fb.add_notification(uid, "Face ID Enrolled", "Browser biometric login is now enabled for your account.", "success", "/profile/")
        return JsonResponse({'success': True, 'message': 'Face biometric profile securely enrolled! +150 XP'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def delete_face_auth(request):
    """GDPR-compliant removal of face biometric descriptor data."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    uid = request.session['user']['uid']
    fb.delete_face_credential(uid)
    profile = fb.get_user_profile(uid) or {}
    profile['face_auth_enabled'] = False
    fb.save_user_profile(uid, profile)
    messages.info(request, 'Your biometric face data has been completely erased.')
    return JsonResponse({'success': True})


# ── Core Dashboard & Onboarding ───────────────────────────────────────────────

@login_required
def dashboard(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    assessment = fb.get_assessment(uid) or {}
    loan_app = fb.get_loan_application(uid) or {}
    applications = fb.get_user_applications(uid)
    notifications = fb.get_notifications(uid, limit=5)
    gamification = calculate_gamification_state(profile)
    scores = calculate_profile_scores(profile)

    stages = [
        {'id': 'exploration',   'label': 'Discovery',     'icon': 'fa-compass'},
        {'id': 'shortlisting',  'label': 'Shortlist',     'icon': 'fa-building-columns'},
        {'id': 'test_prep',     'label': 'Test Prep',     'icon': 'fa-book-open'},
        {'id': 'applications',  'label': 'Applications',  'icon': 'fa-file-signature'},
        {'id': 'financing',     'label': 'Financing',     'icon': 'fa-sack-dollar'},
        {'id': 'visa',          'label': 'Visa Support',  'icon': 'fa-passport'},
        {'id': 'pre_departure', 'label': 'Departure',     'icon': 'fa-plane'},
    ]
    current_stage = profile.get('journey_stage', 'exploration')
    stage_idx = next((i for i, s in enumerate(stages) if s['id'] == current_stage), 0)
    progress_pct = int((stage_idx / (len(stages) - 1)) * 100)

    return render(request, 'dashboard.html', {
        'profile': profile,
        'assessment': assessment,
        'loan_app': loan_app,
        'applications': applications,
        'notifications': notifications,
        'gamification': gamification,
        'scores': scores,
        'stages': stages,
        'current_stage': current_stage,
        'stage_idx': stage_idx,
        'progress_pct': progress_pct,
    })


@login_required
def onboarding_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}

    if request.method == 'POST':
        updates = {
            'name': request.POST.get('name', profile.get('name', '')),
            'age': request.POST.get('age', '22'),
            'city': request.POST.get('city', 'Bengaluru'),
            'education_level': request.POST.get('education_level', 'Undergraduate'),
            'tenth_pct': float(request.POST.get('tenth_pct', 85) or 85),
            'twelfth_pct': float(request.POST.get('twelfth_pct', 86) or 86),
            'degree_cgpa': float(request.POST.get('degree_cgpa', 8.4) or 8.4),
            'gpa': float(request.POST.get('degree_cgpa', 8.4) or 8.4),
            'gre_score': int(request.POST.get('gre_score', 315) or 315),
            'ielts_score': float(request.POST.get('ielts_score', 7.5) or 7.5),
            'work_exp': int(request.POST.get('work_exp', 1) or 1),
            'research_papers': int(request.POST.get('research_papers', 0) or 0),
            'internships': int(request.POST.get('internships', 2) or 2),
            'country_goal': request.POST.get('country_goal', 'USA'),
            'target_program': request.POST.get('target_program', 'MS Computer Science'),
            'budget': request.POST.get('budget', '3500000'),
            'interests': request.POST.getlist('interests'),
            'journey_stage': 'shortlisting'
        }
        profile.update(updates)
        profile = award_xp(profile, 'onboarding', 200, 'profile_complete')
        fb.save_user_profile(uid, profile)
        messages.success(request, 'Profile onboarding complete! +200 XP')
        return redirect('dashboard')

    return render(request, 'onboarding.html', {'profile': profile})


@login_required
@csrf_exempt
def calculate_profile_score_api(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile.update(data)
        except Exception:
            pass
    scores = calculate_profile_scores(profile)
    return JsonResponse(scores)


@login_required
def profile_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    face_cred = fb.get_face_credential(uid)
    gamification = calculate_gamification_state(profile)
    scores = calculate_profile_scores(profile)

    if request.method == 'POST':
        updates = {
            'name': request.POST.get('name', profile.get('name', '')),
            'phone': request.POST.get('phone', ''),
            'degree': request.POST.get('degree', ''),
            'university_current': request.POST.get('university_current', ''),
            'gpa': request.POST.get('gpa', ''),
            'degree_cgpa': request.POST.get('gpa', ''),
            'gre_score': request.POST.get('gre_score', ''),
            'ielts_score': request.POST.get('ielts_score', ''),
            'country_goal': request.POST.get('country_goal', ''),
            'target_program': request.POST.get('target_program', ''),
            'budget': request.POST.get('budget', ''),
        }
        profile.update(updates)
        profile = award_xp(profile, 'profile_update', 25)
        fb.save_user_profile(uid, profile)
        request.session['user']['name'] = updates['name']
        request.session.modified = True
        messages.success(request, 'Profile details updated! +25 XP')
        return redirect('profile')

    logins = fb.query_docs('user_logins', 'uid', '==', uid, limit=10)
    logins.sort(key=lambda x: x.get('login_time', ''), reverse=True)
    return render(request, 'profile.html', {
        'profile': profile,
        'face_cred': face_cred,
        'gamification': gamification,
        'scores': scores,
        'logins': logins
    })


# ── Module 1: Career Navigator & RIASEC Assessment ───────────────────────────

@login_required
def career_assessment(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    assessment = fb.get_assessment(uid) or {}

    if request.method == 'POST':
        answers = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'}
        assessment_result = score_riasec(answers)
        assessment_data = {
            'answers': answers,
            'result': assessment_result,
            'completed_at': datetime.now().isoformat()
        }
        fb.save_assessment(uid, assessment_data)
        profile['career_assessment_completed'] = True
        profile['riasec_code'] = assessment_result['holland_code']
        profile = award_xp(profile, 'assessment', 300, 'career_explorer')
        fb.save_user_profile(uid, profile)
        messages.success(request, 'RIASEC Career Assessment finished! +300 XP')
        return render(request, 'navigator_result.html', {'result': assessment_result, 'profile': profile})

    return render(request, 'career_assessment.html', {'profile': profile, 'assessment': assessment})


@login_required
def career_navigator(request):
    return redirect('career_assessment')


@login_required
def navigator_result(request):
    uid = request.session['user']['uid']
    assessment = fb.get_assessment(uid) or {}
    profile = fb.get_user_profile(uid) or {}
    result = assessment.get('result') or score_riasec({})
    return render(request, 'navigator_result.html', {'result': result, 'profile': profile})


# ── Module 2: University Intelligence & Side-by-Side Comparison ──────────────

@login_required
def university_search(request):
    query = request.GET.get('q', '').strip()
    country = request.GET.get('country', 'all').strip()
    max_tuition = request.GET.get('max_tuition')
    max_t = int(max_tuition) if max_tuition and max_tuition.isdigit() else None

    universities = data_provider.search_universities(query=query, country=country, max_tuition=max_t, limit=40)
    return render(request, 'university_search.html', {
        'universities': universities,
        'query': query,
        'country': country,
        'max_tuition': max_tuition or ''
    })


@login_required
def compare_universities(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}

    uni_ids = request.GET.getlist('id')
    if not uni_ids:
        uni_ids = ['cmu', 'stanford', 'mit']

    selected_unis = []
    for uid_str in uni_ids[:5]:
        u = data_provider.get_university_by_id(uid_str)
        if u:
            # Predict admission for each
            pred = admission_predictor.predict(profile, target_rank=u.get('qs_ranking', 50))
            selected_unis.append({
                **u,
                'admission_probability': pred['probability'],
                'category': pred['category'],
                'category_color': pred['category_color']
            })

    # AI Synthesis
    ai_verdict = ""
    if selected_unis:
        best_pick = max(selected_unis, key=lambda x: x['admission_probability'])
        ai_verdict = f"Recommended choice for your profile: **{best_pick['name']}**. It offers optimal program alignment, a strong {best_pick['admission_probability']}% admission probability ({best_pick['category']}), and high post-study ROI."

    return render(request, 'university_compare.html', {
        'universities': selected_unis,
        'ai_verdict': ai_verdict,
        'profile': profile
    })


# ── Module 3: ML Admission Predictor ──────────────────────────────────────────

@login_required
def admission_predictor_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    
    form_defaults = {
        'gre': profile.get('gre_score', 315),
        'gpa': profile.get('degree_cgpa', 8.4),
        'ielts': profile.get('ielts_score', 7.5),
        'work_exp': profile.get('work_exp', 1),
        'research': profile.get('research_papers', 0),
        'internships': profile.get('internships', 2),
        'target_rank': request.GET.get('rank', 40),
    }
    ctx = {
        'profile': profile,
        'form_defaults': form_defaults,
    }

    if request.method == 'POST':
        target_rank = int(request.POST.get('target_rank', 40))
        eval_profile = {
            'gre': float(request.POST.get('gre', profile.get('gre_score', 312))),
            'gpa': float(request.POST.get('gpa', profile.get('degree_cgpa', 3.4))),
            'ielts': float(request.POST.get('ielts', profile.get('ielts_score', 7.0))),
            'work_exp': int(request.POST.get('work_exp', profile.get('work_exp', 1))),
            'research': int(request.POST.get('research', profile.get('research_papers', 0))),
            'internships': int(request.POST.get('internships', profile.get('internships', 2))),
            'projects': int(request.POST.get('projects', 2)),
        }
        result = admission_predictor.predict(eval_profile, target_rank=target_rank)
        award_xp(profile, 'predictor', 100, 'admission_analyst')
        fb.save_user_profile(uid, profile)
        ctx.update({
            'calc': True,
            'result': result,
            'form_data': request.POST
        })

    return render(request, 'admission_predictor.html', ctx)


# ── Module 4: Advanced Financial Modeling & Loan Marketplace ─────────────────

@login_required
def roi_calculator_view(request):
    ctx = {}
    if request.method == 'POST':
        try:
            params = {
                'tuition': float(request.POST.get('tuition', 45000)),
                'accommodation': float(request.POST.get('accommodation', 12000)),
                'food': float(request.POST.get('food', 6000)),
                'insurance': float(request.POST.get('insurance', 2000)),
                'travel': float(request.POST.get('travel', 1800)),
                'visa_fees': float(request.POST.get('visa_fees', 600)),
                'misc': float(request.POST.get('misc', 2500)),
                'duration': float(request.POST.get('duration', 2.0)),
                'country': request.POST.get('country', 'USA'),
                'field': request.POST.get('field', 'Computer Science'),
            }
            res = calculate_advanced_roi(params)
            ctx = {'calc': True, 'res': res, 'form_data': request.POST}
        except Exception as e:
            messages.error(request, f'ROI calculation error: {e}')
    else:
        # Default computation
        res = calculate_advanced_roi({})
        ctx = {'calc': True, 'res': res, 'form_data': {}}

    return render(request, 'roi_calculator.html', ctx)


@login_required
def loan_marketplace(request):
    principal = float(request.GET.get('amount', 3500000))
    tenure = int(request.GET.get('tenure', 10))
    has_collateral = request.GET.get('collateral') == '1'

    loan_data = get_loan_options(principal, tenure_years=tenure, has_collateral=has_collateral)
    return render(request, 'loan_marketplace.html', {'loan_data': loan_data})


@login_required
def loan_estimator(request):
    return redirect('loan_marketplace')


@login_required
def emi_calculator_view(request):
    principal = float(request.GET.get('p', 3500000))
    rate = float(request.GET.get('r', 10.5))
    tenure_years = int(request.GET.get('y', 10))
    tenure_months = tenure_years * 12

    emi = calculate_emi(principal, rate, tenure_months)
    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    schedule, balance = [], principal
    mr = rate / 100.0 / 12.0
    for m in range(1, min(13, tenure_months + 1)):
        ip = round(balance * mr)
        pp = emi - ip
        balance -= pp
        schedule.append({'month': m, 'emi': emi, 'interest': ip, 'principal': pp, 'balance': max(0, round(balance))})

    return render(request, 'emi_calculator.html', {
        'principal': principal,
        'rate': rate,
        'tenure_years': tenure_years,
        'emi': f"₹{emi:,.0f}",
        'total_pay': f"₹{total_payment:,.0f}",
        'total_int': f"₹{total_interest:,.0f}",
        'schedule': schedule
    })


@login_required
def loan_application_view(request):
    uid = request.session['user']['uid']
    existing = fb.get_loan_application(uid) or {}

    if request.method == 'POST':
        step = int(request.POST.get('step', 1))
        data = {k: v for k, v in request.POST.items() if k not in ('csrfmiddlewaretoken', 'step')}
        existing.update(data)
        existing.update({'current_step': step + 1, 'uid': uid})
        fb.save_loan_application(uid, existing)

        if step >= 4:
            existing['status'] = 'submitted'
            fb.save_loan_application(uid, existing)
            profile = fb.get_user_profile(uid) or {}
            profile = award_xp(profile, 'loan_app', 200, 'finance_master')
            fb.save_user_profile(uid, profile)
            messages.success(request, 'Education loan application submitted! +200 XP')
            return redirect('dashboard')

        messages.success(request, f'Section {step} saved.')
        return redirect('loan_application')

    return render(request, 'loan_application.html', {
        'existing': existing,
        'current_step': existing.get('current_step', 1),
    })


# ── Module 5: Scholarship Finder ──────────────────────────────────────────────

@login_required
def scholarship_finder(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    matched = match_scholarships(profile)
    return render(request, 'scholarship_finder.html', {'scholarships': matched, 'profile': profile})


# ── Module 6: Application Tracker & Document Analysis ─────────────────────────

@login_required
def application_tracker(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    applications = fb.get_user_applications(uid)

    if request.method == 'POST':
        uni_name = request.POST.get('university_name', '').strip()
        program = request.POST.get('program_name', 'MS Computer Science').strip()
        deadline = request.POST.get('deadline', 'Dec 15, 2026').strip()
        term = request.POST.get('term', 'Fall 2026')

        if uni_name:
            app_data = {
                'university_name': uni_name,
                'program_name': program,
                'deadline': deadline,
                'term': term,
                'status': 'shortlisted',
                'checklist': {
                    'profile_created': True,
                    'docs_uploaded': False,
                    'sop_ready': False,
                    'lor_received': False,
                    'fee_paid': False,
                    'submitted': False
                }
            }
            fb.save_application(uid, app_data)
            award_xp(profile, 'app_added', 150, 'application_pro')
            fb.save_user_profile(uid, profile)
            messages.success(request, f'Added {uni_name} to your application tracker! +150 XP')
            return redirect('application_tracker')

    return render(request, 'application_tracker.html', {'applications': applications})


@login_required
@csrf_exempt
def update_application_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        app_id = data.get('app_id')
        status = data.get('status')
        checklist = data.get('checklist')

        app_doc = fb.get_doc('applications', app_id)
        if not app_doc:
            return JsonResponse({'success': False, 'error': 'Application not found'}, status=404)

        if status:
            app_doc['status'] = status
        if checklist:
            app_doc['checklist'] = checklist

        app_doc['updated_at'] = datetime.now().isoformat()
        fb.set_doc('applications', app_id, app_doc)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def document_manager(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    analysis_result = None

    if request.method == 'POST':
        sop_text = request.POST.get('sop_text', '')
        target_uni = request.POST.get('target_university', 'Carnegie Mellon University')
        target_prog = request.POST.get('target_program', 'MS Computer Science')

        if sop_text.strip():
            analysis_result = analyze_sop_content(sop_text, target_uni, target_prog)
            award_xp(profile, 'sop_analyzed', 150)
            fb.save_user_profile(uid, profile)
            messages.success(request, 'AI SOP analysis completed! +150 XP')

    return render(request, 'document_manager.html', {'analysis': analysis_result, 'profile': profile})


# ── Module 7: AI Chatbot (RAG-Enabled) & Study Planner ───────────────────────

@login_required
def chatbot_view(request):
    uid = request.session['user']['uid']
    history = fb.get_chat_history(uid, limit=30)
    profile = fb.get_user_profile(uid) or {}
    return render(request, 'chatbot.html', {'history': history, 'profile': profile})


@csrf_exempt
@login_required
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        uid = request.session['user']['uid']
        body = json.loads(request.body)
        msg = body.get('message', '').strip()
        if not msg:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        profile = fb.get_user_profile(uid) or {}
        fb.add_chat_message(uid, 'user', msg)
        history = fb.get_chat_history(uid, limit=10)

        rag_output = answer_rag_query(msg, profile, history)
        fb.add_chat_message(uid, 'assistant', rag_output['answer'])

        return JsonResponse({
            'response': rag_output['answer'],
            'sources': rag_output.get('sources', [])
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def study_planner_view(request):
    hours = int(request.GET.get('hours', 15))
    plan = generate_study_plan(hours_per_week=hours)
    return render(request, 'study_planner.html', {'plan': plan, 'hours': hours})


# ── Module 8: Mentor Marketplace, Timeline & Admin ───────────────────────────

@login_required
def mentor_marketplace(request):
    mentors = [
        {
            "id": "m1",
            "name": "Dr. Aarav Sharma",
            "title": "Principal AI Scientist at Google",
            "education": "PhD Carnegie Mellon University",
            "specialization": "AI/ML Systems, CS Admissions, Research SOP",
            "country": "USA",
            "hourly_rate": "₹850",
            "rating": 4.9,
            "reviews_count": 58,
            "avatar_initials": "AS"
        },
        {
            "id": "m2",
            "name": "Priya Nair",
            "title": "Senior Quantitative Strategist",
            "education": "MSc Financial Math, Imperial College London",
            "specialization": "UK Chevening Scholarships, Quant Finance, Visa",
            "country": "UK",
            "hourly_rate": "₹750",
            "rating": 4.8,
            "reviews_count": 42,
            "avatar_initials": "PN"
        },
        {
            "id": "m3",
            "name": "Karthik Venkat",
            "title": "Cloud Infrastructure Architect at AWS",
            "education": "MS University of Waterloo",
            "specialization": "Canada Co-Op Programs, Tech Career Transitions",
            "country": "Canada",
            "hourly_rate": "₹700",
            "rating": 4.9,
            "reviews_count": 64,
            "avatar_initials": "KV"
        }
    ]
    return render(request, 'mentor_marketplace.html', {'mentors': mentors})


@login_required
@csrf_exempt
def book_mentor_session(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        uid = request.session['user']['uid']
        profile = fb.get_user_profile(uid) or {}
        mentor_name = data.get('mentor_name', 'Mentor')
        fb.add_notification(uid, "Session Confirmed", f"Your 1-on-1 counseling appointment with {mentor_name} has been confirmed.", "success", "/mentors/")
        return JsonResponse({'success': True, 'message': f'Appointment booked with {mentor_name}!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def timeline_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    country = profile.get('country_goal', 'USA')

    events = [
        {'label': 'Research Universities & Programs', 'desc': 'Explore rankings, fees, scholarships', 'category': 'research'},
        {'label': 'Standardized Test Preparation (GRE/IELTS)', 'desc': 'Target competitive quantitative & verbal percentiles', 'category': 'test'},
        {'label': 'Shortlist 8-10 Target Institutions', 'desc': 'Structure Reach, Target, and Safe admissions mix', 'category': 'research'},
        {'label': 'Statement of Purpose (SOP) & Faculty Alignment', 'desc': 'Draft research statement and cite target lab faculty', 'category': 'application'},
        {'label': 'Letters of Recommendation (LOR)', 'desc': 'Acquire 3 strong academic & manager references', 'category': 'application'},
        {'label': 'Education Loan Pre-Approval', 'desc': 'Secure loan sanction for visa solvency verification', 'category': 'finance'},
        {'label': 'Submit Official University Applications', 'desc': 'Pay application fees and upload transcripts', 'category': 'application'},
        {'label': 'Review Admit Offers & Confirm Deposit', 'desc': 'Accept target university admit and request Form I-20 / CAS', 'category': 'decision'},
        {'label': f'Student Visa Appointment ({country})', 'desc': 'Complete DS-160/Visa portal and attend consular interview', 'category': 'visa'},
        {'label': 'Pre-Departure Flight & Housing', 'desc': 'Finalize student accommodation and health insurance', 'category': 'milestone'}
    ]
    return render(request, 'timeline.html', {'events': events, 'country': country})


@login_required
def my_journey(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    gamification = calculate_gamification_state(profile)
    scores = calculate_profile_scores(profile)
    return render(request, 'my_journey.html', {
        'profile': profile,
        'gamification': gamification,
        'scores': scores
    })


@role_required(['admin'])
def admin_dashboard(request):
    """Administrator executive metrics and platform data management."""
    users = fb.get_all_docs('users', limit=100)
    applications = fb.get_all_docs('applications', limit=100)
    chat_logs = fb.get_all_docs('chat_history', limit=100)

    stats = {
        'total_users': max(128, len(users)),
        'active_today': 42,
        'applications_tracked': max(86, len(applications)),
        'ai_queries_answered': max(340, len(chat_logs)),
        'loans_modeled': 94,
        'scholarships_indexed': len(SCHOLARSHIPS_DATA)
    }
    return render(request, 'admin_dashboard.html', {
        'stats': stats,
        'users': users[:15],
        'applications': applications[:15]
    })


# ── Notifications API ─────────────────────────────────────────────────────────

@login_required
def get_notifications_api(request):
    uid = request.session['user']['uid']
    notifs = fb.get_notifications(uid, limit=10)
    return JsonResponse({'notifications': notifs})


@login_required
@csrf_exempt
def mark_notification_read_api(request, nid):
    success = fb.mark_notification_read(nid)
    return JsonResponse({'success': success})
