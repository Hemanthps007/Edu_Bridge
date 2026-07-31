import json, hashlib
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from . import firebase_client as fb


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(fn):
    def wrapper(request, *a, **kw):
        if not request.session.get('user'):
            messages.warning(request, 'Please sign in to continue.')
            return redirect('login')
        return fn(request, *a, **kw)
    wrapper.__name__ = fn.__name__
    return wrapper


# ── Public ────────────────────────────────────────────────────────────────────

def landing(request):
    if request.session.get('user'):
        return redirect('dashboard')
    return render(request, 'landing.html')


def register_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        pw    = request.POST.get('password', '')
        degree        = request.POST.get('degree', 'MS')
        country_goal  = request.POST.get('country_goal', 'USA')
        if not all([name, email, pw]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')
        uid = hashlib.md5(email.encode()).hexdigest()
        if fb.get_user_profile(uid):
            messages.error(request, 'Account already exists with this email.')
            return render(request, 'register.html')
        profile = {
            'uid': uid, 'name': name, 'email': email,
            'password_hash': _hash(pw),
            'degree': degree, 'country_goal': country_goal,
            'points': 10, 'level': 1, 'streak': 1,
            'badges': [], 'journey_stage': 'exploration',
            'created_at': datetime.now().isoformat(),
        }
        fb.save_user_profile(uid, profile)
        request.session['user'] = {'uid': uid, 'name': name, 'email': email}
        messages.success(request, f'Welcome to StudyBridge, {name}! +10 points')
        return redirect('dashboard')
    return render(request, 'register.html')


def login_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        pw    = request.POST.get('password', '')
        uid   = hashlib.md5(email.encode()).hexdigest()
        profile = fb.get_user_profile(uid)
        if profile and profile.get('password_hash') == _hash(pw):
            request.session['user'] = {'uid': uid, 'name': profile.get('name', email), 'email': email}
            messages.success(request, f"Welcome back, {profile.get('name')}!")
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('landing')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    uid = request.session['user']['uid']
    profile    = fb.get_user_profile(uid) or {}
    assessment = fb.get_assessment(uid) or {}
    loan_app   = fb.get_loan_application(uid) or {}

    stages = [
        {'id': 'exploration',   'label': 'Exploring',     'icon': '🔍'},
        {'id': 'shortlisting',  'label': 'Shortlisting',  'icon': '📋'},
        {'id': 'test_prep',     'label': 'Test Prep',     'icon': '📚'},
        {'id': 'applications',  'label': 'Applications',  'icon': '✏️'},
        {'id': 'visa',          'label': 'Visa',          'icon': '🛂'},
        {'id': 'financing',     'label': 'Financing',     'icon': '💰'},
        {'id': 'pre_departure', 'label': 'Pre-Departure', 'icon': '✈️'},
    ]
    current_stage = profile.get('journey_stage', 'exploration')
    stage_idx = next((i for i, s in enumerate(stages) if s['id'] == current_stage), 0)

    return render(request, 'dashboard.html', {
        'profile': profile,
        'assessment': assessment,
        'loan_app': loan_app,
        'stages': stages,
        'current_stage': current_stage,
        'stage_idx': stage_idx,
        'progress_pct': int(stage_idx / (len(stages) - 1) * 100),
    })


@login_required
def profile_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    if request.method == 'POST':
        updates = {
            'name': request.POST.get('name', profile.get('name', '')),
            'phone': request.POST.get('phone', ''),
            'degree': request.POST.get('degree', ''),
            'university_current': request.POST.get('university_current', ''),
            'gpa': request.POST.get('gpa', ''),
            'country_goal': request.POST.get('country_goal', ''),
            'target_program': request.POST.get('target_program', ''),
            'budget': request.POST.get('budget', ''),
            'journey_stage': request.POST.get('journey_stage', 'exploration'),
        }
        profile.update(updates)
        pts = (profile.get('points', 0) or 0) + 10
        profile['points'] = pts
        fb.save_user_profile(uid, profile)
        request.session['user']['name'] = updates['name']
        request.session.modified = True
        messages.success(request, 'Profile updated! +10 points')
        return redirect('profile')
    return render(request, 'profile.html', {'profile': profile})


# ── AI Tools ──────────────────────────────────────────────────────────────────

@login_required
def career_navigator(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    return render(request, 'career_navigator.html', {'profile': profile})


@login_required
def navigator_result(request):
    if request.method != 'POST':
        return redirect('career_navigator')

    uid  = request.session['user']['uid']
    data = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'}

    field    = data.get('field', 'Computer Science')
    country  = data.get('country_pref', 'USA')
    gre      = int(data.get('gre_score', 310) or 310)
    gpa      = float(data.get('gpa', 3.0) or 3.0)
    budget   = data.get('budget', 'medium')

    recs   = _recommendations(field, country, gre, gpa, budget)
    score  = _profile_score(gre, gpa, data)

    assessment = {
        'inputs': data,
        'recommendations': recs,
        'profile_score': score,
        'generated_at': datetime.now().isoformat(),
    }
    fb.save_assessment(uid, assessment)

    profile = fb.get_user_profile(uid) or {}
    pts = (profile.get('points', 0) or 0) + 25
    fb.set_doc('users', uid, {'points': pts, 'journey_stage': 'shortlisting'})
    messages.success(request, 'Assessment complete! +25 points')
    return render(request, 'navigator_result.html', {'assessment': assessment, 'data': data})


def _profile_score(gre, gpa, data):
    s = 0
    s += min(40, int((gre - 260) / 80 * 40))
    s += min(25, int((gpa - 2.0) / 2.0 * 25))
    s += min(15, int(data.get('work_exp', '0') or '0') * 5)
    s += 10 if int(data.get('research_papers', '0') or '0') > 0 else 0
    s += 10 if int(data.get('internships', '0') or '0') > 0 else 0
    return min(100, s)


def _recommendations(field, country, gre, gpa, budget):
    DB = {
        'Computer Science': {
            'USA': [
                {'name': 'Carnegie Mellon University', 'rank': 1,  'avg_gre': 325, 'avg_gpa': 3.8, 'tuition': 62000, 'accept_rate': 8},
                {'name': 'Georgia Tech',               'rank': 8,  'avg_gre': 320, 'avg_gpa': 3.6, 'tuition': 32000, 'accept_rate': 16},
                {'name': 'University of Texas Austin', 'rank': 12, 'avg_gre': 315, 'avg_gpa': 3.5, 'tuition': 21000, 'accept_rate': 22},
                {'name': 'Northeastern University',    'rank': 28, 'avg_gre': 312, 'avg_gpa': 3.4, 'tuition': 55000, 'accept_rate': 31},
                {'name': 'Arizona State University',   'rank': 35, 'avg_gre': 305, 'avg_gpa': 3.2, 'tuition': 28000, 'accept_rate': 48},
            ],
            'Canada': [
                {'name': 'University of Toronto',        'rank': 2, 'avg_gre': 318, 'avg_gpa': 3.7, 'tuition': 28000, 'accept_rate': 15},
                {'name': 'University of British Columbia','rank': 5, 'avg_gre': 315, 'avg_gpa': 3.5, 'tuition': 24000, 'accept_rate': 20},
                {'name': 'University of Waterloo',       'rank': 4, 'avg_gre': 319, 'avg_gpa': 3.6, 'tuition': 26000, 'accept_rate': 18},
                {'name': 'McGill University',            'rank': 7, 'avg_gre': 312, 'avg_gpa': 3.4, 'tuition': 22000, 'accept_rate': 25},
            ],
            'UK': [
                {'name': 'Imperial College London',  'rank': 1, 'avg_gre': 0, 'avg_gpa': 3.7, 'tuition': 38000, 'accept_rate': 14},
                {'name': 'University of Edinburgh',  'rank': 4, 'avg_gre': 0, 'avg_gpa': 3.4, 'tuition': 27000, 'accept_rate': 22},
                {'name': 'University of Manchester', 'rank': 6, 'avg_gre': 0, 'avg_gpa': 3.2, 'tuition': 25000, 'accept_rate': 30},
            ],
        },
        'Business Administration': {
            'USA': [
                {'name': 'Harvard Business School',  'rank': 1, 'avg_gre': 330, 'avg_gpa': 3.9, 'tuition': 73440, 'accept_rate': 9},
                {'name': 'Wharton (UPenn)',          'rank': 3, 'avg_gre': 325, 'avg_gpa': 3.6, 'tuition': 83230, 'accept_rate': 19},
                {'name': 'Booth (U. Chicago)',       'rank': 4, 'avg_gre': 323, 'avg_gpa': 3.5, 'tuition': 75000, 'accept_rate': 23},
                {'name': 'Kelley (Indiana Univ)',    'rank': 20,'avg_gre': 308, 'avg_gpa': 3.3, 'tuition': 35000, 'accept_rate': 37},
            ],
            'Canada': [
                {'name': 'Rotman (U. Toronto)',  'rank': 2, 'avg_gre': 318, 'avg_gpa': 3.5, 'tuition': 52000, 'accept_rate': 24},
                {'name': 'Ivey (UWO)',           'rank': 3, 'avg_gre': 315, 'avg_gpa': 3.3, 'tuition': 45000, 'accept_rate': 28},
            ],
            'UK': [
                {'name': 'London Business School', 'rank': 2, 'avg_gre': 0, 'avg_gpa': 3.6, 'tuition': 92000, 'accept_rate': 18},
                {'name': 'Oxford Said',            'rank': 4, 'avg_gre': 0, 'avg_gpa': 3.5, 'tuition': 68000, 'accept_rate': 22},
            ],
        },
        'Data Science': {
            'USA': [
                {'name': 'MIT IDSS',               'rank': 1, 'avg_gre': 328, 'avg_gpa': 3.8, 'tuition': 58000, 'accept_rate': 7},
                {'name': 'Columbia University',    'rank': 5, 'avg_gre': 322, 'avg_gpa': 3.6, 'tuition': 62000, 'accept_rate': 14},
                {'name': 'University of Michigan', 'rank': 9, 'avg_gre': 318, 'avg_gpa': 3.5, 'tuition': 26000, 'accept_rate': 19},
                {'name': 'NYU Tandon',             'rank': 22,'avg_gre': 312, 'avg_gpa': 3.3, 'tuition': 52000, 'accept_rate': 35},
            ],
            'Canada': [
                {'name': 'University of Toronto', 'rank': 1, 'avg_gre': 318, 'avg_gpa': 3.6, 'tuition': 26000, 'accept_rate': 18},
                {'name': 'McGill University',     'rank': 3, 'avg_gre': 312, 'avg_gpa': 3.4, 'tuition': 22000, 'accept_rate': 24},
            ],
            'UK': [
                {'name': 'University College London', 'rank': 2, 'avg_gre': 0, 'avg_gpa': 3.6, 'tuition': 32000, 'accept_rate': 20},
                {'name': 'University of Edinburgh',   'rank': 5, 'avg_gre': 0, 'avg_gpa': 3.3, 'tuition': 26000, 'accept_rate': 28},
            ],
        },
    }
    field_key   = field if field in DB else 'Computer Science'
    country_key = country if country in DB.get(field_key, {}) else 'USA'
    unis = DB.get(field_key, {}).get(country_key, [])

    results = []
    for u in unis:
        gre_gap = (gre - u['avg_gre']) * 0.4 if u['avg_gre'] > 0 else 0
        gpa_gap = (gpa - u['avg_gpa']) * 15
        prob = max(5, min(95, u['accept_rate'] + gre_gap + gpa_gap))
        cat = 'reach' if prob < 45 else 'target' if prob < 65 else 'safety'
        results.append({**u, 'probability': round(prob), 'category': cat})

    results.sort(key=lambda x: x['probability'], reverse=True)
    return results


@login_required
def roi_calculator(request):
    ctx = {}
    if request.method == 'POST':
        try:
            tuition   = float(request.POST.get('tuition', 35000))
            living    = float(request.POST.get('living', 15000))
            duration  = int(request.POST.get('duration', 2))
            loan_int  = float(request.POST.get('loan_interest', 10.5))
            pre_sal   = float(request.POST.get('pre_salary', 600000))
            field     = request.POST.get('field', 'Computer Science')
            country   = request.POST.get('country', 'USA')

            sal_db = {
                'Computer Science':     {'USA': 130000, 'Canada': 95000, 'UK': 75000, 'Germany': 65000, 'Australia': 90000},
                'Business Administration': {'USA': 110000, 'Canada': 85000, 'UK': 80000, 'Germany': 70000, 'Australia': 88000},
                'Data Science':         {'USA': 125000, 'Canada': 90000, 'UK': 72000, 'Germany': 68000, 'Australia': 92000},
                'Engineering':          {'USA': 105000, 'Canada': 88000, 'UK': 68000, 'Germany': 72000, 'Australia': 85000},
                'Finance':              {'USA': 115000, 'Canada': 82000, 'UK': 90000, 'Germany': 65000, 'Australia': 82000},
            }
            inr = 83.5
            est_sal_usd   = sal_db.get(field, sal_db['Computer Science']).get(country, 100000)
            total_usd     = (tuition + living) * duration
            total_inr     = total_usd * inr
            ann_gain_inr  = (est_sal_usd * inr) - pre_sal
            payback       = round(total_inr / ann_gain_inr, 1) if ann_gain_inr > 0 else 99
            mr            = loan_int / 100 / 12
            emi           = round(total_usd * inr * mr / (1 - (1 + mr) ** -120)) if total_usd > 0 else 0
            roi_pct       = round(((ann_gain_inr * 10) - total_inr) / total_inr * 100, 1)

            chart = {
                'years': list(range(1, 11)),
                'cost':  [round((total_inr + emi * 12 * y) / 100000) for y in range(1, 11)],
                'gain':  [round(ann_gain_inr * y / 100000) for y in range(1, 11)],
            }
            ctx = {
                'calc': True,
                'total_cost_usd': f'{total_usd:,.0f}',
                'total_cost_inr': f'{total_inr/100000:.1f}L',
                'est_sal_usd':    f'{est_sal_usd:,.0f}',
                'est_sal_inr':    f'{est_sal_usd * inr / 100000:.1f}L',
                'payback_years':  payback,
                'roi_pct':        roi_pct,
                'emi_monthly':    f'{emi:,.0f}',
                'ann_gain_inr':   f'{ann_gain_inr/100000:.1f}L',
                'chart_data':     chart,
                'form_data':      request.POST,
            }
        except Exception as e:
            messages.error(request, f'Calculation error: {e}')
    return render(request, 'roi_calculator.html', ctx)


@login_required
def admission_predictor(request):
    ctx = {}
    if request.method == 'POST':
        try:
            gre         = int(request.POST.get('gre', 300))
            gpa         = float(request.POST.get('gpa', 3.0))
            work_exp    = int(request.POST.get('work_exp', 0))
            research    = int(request.POST.get('research', 0))
            internships = int(request.POST.get('internships', 0))
            projects    = int(request.POST.get('projects', 0))
            target_rank = int(request.POST.get('target_rank', 50))

            s = 0
            s += min(35, int((gre - 260) / 80 * 35))
            s += min(25, int((gpa - 2.0) / 2.0 * 25))
            s += min(15, work_exp * 3)
            s += min(10, research * 5)
            s += min(8,  internships * 4)
            s += min(7,  projects * 2)
            s = min(100, s)

            rank_penalty = max(0, (150 - target_rank) / 150 * 20)
            prob = max(5, min(95, s - rank_penalty + 10))

            strengths, gaps = [], []
            if gre >= 315:  strengths.append('Strong GRE score')
            else:           gaps.append('GRE score below competitive range (aim 315+)')
            if gpa >= 3.5:  strengths.append('Excellent GPA')
            elif gpa >= 3.0: strengths.append('Decent GPA')
            else:           gaps.append('GPA needs improvement (aim 3.0+)')
            if work_exp >= 2:     strengths.append('Relevant work experience')
            elif work_exp == 0:   gaps.append('No work experience — consider internships')
            if research >= 1:     strengths.append('Research publication / experience')
            else:                 gaps.append('Research experience strengthens STEM apps')
            if internships >= 2:  strengths.append('Strong internship portfolio')

            ctx = {
                'calc': True,
                'score': s,
                'probability': round(prob),
                'strengths': strengths,
                'gaps': gaps,
                'grade': 'Excellent' if s >= 80 else 'Good' if s >= 60 else 'Average' if s >= 40 else 'Needs Work',
                'form_data': request.POST,
            }
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'admission_predictor.html', ctx)


@login_required
def timeline_view(request):
    uid = request.session['user']['uid']
    profile = fb.get_user_profile(uid) or {}
    country = profile.get('country_goal', 'USA')

    events = [
        {'label': 'Research Universities & Programs', 'desc': 'Explore rankings, fees, scholarships', 'category': 'research'},
        {'label': 'GRE / GMAT Preparation',           'desc': 'Register & start prep (3-6 months)',   'category': 'test'},
        {'label': 'GRE / GMAT Exam',                  'desc': 'Take the standardized test',           'category': 'test'},
        {'label': 'IELTS / TOEFL Exam',               'desc': 'English proficiency certification',    'category': 'test'},
        {'label': 'Shortlist Universities (8-10)',     'desc': 'Reach, target & safety mix',          'category': 'research'},
        {'label': 'Request Recommendations (LOR)',     'desc': 'Contact 3 professors / managers',     'category': 'application'},
        {'label': 'Draft Statement of Purpose',        'desc': 'Craft compelling SOP for each uni',   'category': 'application'},
        {'label': 'Financial Planning & Loan Research','desc': 'Explore education loans & scholarships','category': 'finance'},
        {'label': 'Submit Applications',               'desc': 'Apply to all shortlisted universities','category': 'application'},
        {'label': 'Loan Pre-Approval',                 'desc': 'Apply for education loan pre-approval','category': 'finance'},
        {'label': 'Receive Offer Letters',             'desc': 'Review and compare admits & rejects',  'category': 'decision'},
        {'label': 'Confirm Enrollment & Pay Deposit',  'desc': 'Accept offer, pay seat deposit',       'category': 'decision'},
        {'label': 'Finalize Education Loan',           'desc': 'Complete loan disbursement process',  'category': 'finance'},
        {'label': f'Student Visa Application ({country})', 'desc': 'Prepare & submit visa application', 'category': 'visa'},
        {'label': '✈️  Departure!',                    'desc': 'Begin your global journey',            'category': 'milestone'},
    ]

    return render(request, 'timeline.html', {'events': events, 'country': country})


# ── Loan views ────────────────────────────────────────────────────────────────

@login_required
def loan_estimator(request):
    ctx = {}
    if request.method == 'POST':
        try:
            tuition    = float(request.POST.get('tuition', 35000))
            living     = float(request.POST.get('living', 15000))
            duration   = int(request.POST.get('duration', 2))
            scholarship= float(request.POST.get('scholarship', 0))
            savings    = float(request.POST.get('savings', 0))
            gpa        = float(request.POST.get('gpa', 3.2))
            co_income  = float(request.POST.get('co_income', 600000))
            uni_rank   = int(request.POST.get('uni_rank', 50))
            inr        = 83.5

            total_usd   = (tuition + living) * duration
            total_inr   = total_usd * inr
            loan_needed = max(0, total_inr - scholarship * inr - savings)

            score = min(100,
                min(30, int((gpa - 2.0) / 2.0 * 30)) +
                min(30, int(co_income / 2000000 * 30)) +
                min(20, max(0, (100 - uni_rank) / 100 * 20)) + 20
            )

            lenders = [
                {'name': 'SBI Global Ed-Vantage', 'rate': 10.15, 'max_loan': 15000000, 'fee': 0,   'collateral': 'Required > ₹75L', 'days': '7-10'},
                {'name': 'HDFC Credila',          'rate': 10.50, 'max_loan':  7500000, 'fee': 1.0, 'collateral': 'Required > ₹40L', 'days': '3-5'},
                {'name': 'ICICI Bank',            'rate': 11.00, 'max_loan': 10000000, 'fee': 1.0, 'collateral': 'Required > ₹50L', 'days': '4-6'},
                {'name': 'Axis Bank',             'rate': 11.50, 'max_loan':  7500000, 'fee': 0.5, 'collateral': 'Required > ₹40L', 'days': '5-7'},
                {'name': 'Avanse',                'rate': 11.75, 'max_loan':  7500000, 'fee': 1.5, 'collateral': 'Flexible',         'days': '2-4'},
                {'name': 'InCred',                'rate': 12.50, 'max_loan':  6000000, 'fee': 2.0, 'collateral': 'Not Required',     'days': '2-3'},
            ]

            offers = []
            for l in lenders:
                eligible = min(l['max_loan'], co_income * 20)
                mr  = l['rate'] / 100 / 12
                emi = round(loan_needed * mr / (1 - (1 + mr) ** -120)) if loan_needed > 0 else 0
                offers.append({**l, 'eligible_fmt': f"{eligible/100000:.0f}L", 'emi_fmt': f"{emi:,.0f}"})

            ctx = {
                'calc': True,
                'loan_needed':     f'{loan_needed/100000:.1f}L',
                'total_cost_inr':  f'{total_inr/100000:.1f}L',
                'elig_score':      score,
                'offers':          offers,
                'form_data':       request.POST,
            }
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'loan_estimator.html', ctx)


@login_required
def emi_calculator(request):
    ctx = {}
    if request.method == 'POST':
        try:
            principal     = float(request.POST.get('principal', 4500000))
            rate          = float(request.POST.get('rate', 10.5))
            tenure_months = int(request.POST.get('tenure', 120))
            mr  = rate / 100 / 12
            emi = round(principal * mr / (1 - (1 + mr) ** -tenure_months))
            total_pay = emi * tenure_months
            total_int = total_pay - principal

            schedule, balance = [], principal
            for m in range(1, min(13, tenure_months + 1)):
                ip = round(balance * mr)
                pp = emi - ip
                balance -= pp
                schedule.append({'month': m, 'emi': emi, 'interest': ip, 'principal': pp, 'balance': max(0, round(balance))})

            ctx = {
                'calc': True,
                'emi':         f'{emi:,.0f}',
                'total_pay':   f'{total_pay:,.0f}',
                'total_int':   f'{total_int:,.0f}',
                'principal':   f'{principal:,.0f}',
                'int_pct':     round(total_int / total_pay * 100, 1),
                'schedule':    schedule,
                'chart_data':  {'principal': round(principal), 'interest': round(total_int)},
                'form_data':   request.POST,
            }
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'emi_calculator.html', ctx)


@login_required
def loan_application(request):
    uid      = request.session['user']['uid']
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
            pts = (profile.get('points', 0) or 0) + 100
            fb.set_doc('users', uid, {'points': pts, 'journey_stage': 'financing'})
            messages.success(request, 'Loan application submitted! +100 points')
            return redirect('dashboard')

        messages.success(request, f'Step {step} saved — continue to next section.')
        return redirect('loan_application')

    return render(request, 'loan_application.html', {
        'existing': existing,
        'current_step': existing.get('current_step', 1),
    })


# ── Chatbot ───────────────────────────────────────────────────────────────────

@login_required
def chatbot(request):
    uid     = request.session['user']['uid']
    history = fb.get_chat_history(uid, limit=30)
    return render(request, 'chatbot.html', {'history': history})


@csrf_exempt
@login_required
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    uid  = request.session['user']['uid']
    body = json.loads(request.body)
    msg  = body.get('message', '').strip()
    if not msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    fb.add_chat_message(uid, 'user', msg)
    history  = fb.get_chat_history(uid, limit=12)
    api_msgs = [{'role': h['role'], 'content': h['content']} for h in history]

    response = _call_claude(api_msgs)
    fb.add_chat_message(uid, 'assistant', response)
    return JsonResponse({'response': response})


def _call_claude(messages_list):
    key = settings.ANTHROPIC_API_KEY
    if not key:
        return _demo_response(messages_list[-1]['content'])
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        system = (
            "You are StudyBridge AI — a warm, knowledgeable advisor for Indian students planning postgraduate education abroad "
            "(US, UK, Canada, Germany, Australia) or in India.\n\n"
            "You help with: university selection, program fit, GRE/GMAT/IELTS tips, SOP guidance, visa process (F-1, UK, Canada), "
            "education loan comparison (SBI, HDFC Credila, Axis, Avanse, InCred), scholarships, cost of living, and career prospects.\n\n"
            "Always use Indian context — INR conversions, Indian universities as baselines, CGPA systems. "
            "Be specific, encouraging, and actionable. Use markdown formatting. "
            "End with a brief follow-up question to keep the conversation going."
        )
        r = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system,
            messages=messages_list,
        )
        return r.content[0].text
    except Exception:
        return _demo_response(messages_list[-1]['content'])


def _demo_response(msg):
    m = msg.lower()
    if any(w in m for w in ['gre', 'gmat', 'score', 'exam', 'test']):
        return (
            "**GRE Score Ranges for Competitive Admissions:**\n\n"
            "| Program Tier | GRE Score | Quant | Verbal |\n"
            "|---|---|---|---|\n"
            "| Top 10 US | 323+ | 167+ | 156+ |\n"
            "| Rank 11-30 | 315-322 | 163+ | 152+ |\n"
            "| Rank 31-75 | 305-315 | 158+ | 148+ |\n\n"
            "**Preparation Tips:**\n"
            "- **Manhattan Prep** or **Magoosh** for structured prep (3-4 months)\n"
            "- Take a free **ETS practice test** first to baseline yourself\n"
            "- Indian students usually score higher on Quant — focus on Verbal\n"
            "- Last 4 weeks: 3 full-length practice tests per week\n\n"
            "What's your target university tier? I can give you a more specific score goal."
        )
    if any(w in m for w in ['loan', 'finance', 'emi', 'money', 'cost', 'fund']):
        return (
            "**Education Loan Options for Indian Students:**\n\n"
            "| Lender | Rate (p.a.) | Max Amount | Collateral |\n"
            "|---|---|---|---|\n"
            "| SBI Global Ed-Vantage | 10.15% | ₹1.5 Cr | Yes (>75L) |\n"
            "| HDFC Credila | 10.5% | ₹75L | Yes (>40L) |\n"
            "| ICICI Bank | 11.0% | ₹1 Cr | Yes (>50L) |\n"
            "| Axis Bank | 11.5% | ₹75L | Yes (>40L) |\n"
            "| Avanse | 11.75% | ₹75L | Flexible |\n"
            "| InCred | 12.5% | ₹60L | Not Required |\n\n"
            "**Documents needed:** Admission letter, fee structure, income proof (ITR/salary slips), KYC, property docs\n\n"
            "**Pro tip:** Apply for loan **pre-approval** 2-3 months before you receive your admit — saves 4-6 weeks later.\n\n"
            "Want me to calculate your EMI for a specific loan amount?"
        )
    if any(w in m for w in ['usa', 'us', 'america', 'united states']):
        return (
            "**Studying in the USA — Key Facts for Indian Students:**\n\n"
            "**Visa:** F-1 Student Visa (get I-20 from university first)\n"
            "**Duration:** MS = 1.5-2 years, MBA = 2 years, PhD = 4-6 years\n"
            "**Annual Tuition:** $20,000–$65,000 depending on program\n"
            "**Living Costs:** $12,000–$22,000/year (varies by city)\n\n"
            "**Post-Study Work:**\n"
            "- OPT: 12 months work authorization after graduation\n"
            "- STEM OPT extension: additional 24 months (CS/DS/Engg)\n"
            "- H-1B lottery for long-term stay\n\n"
            "**Popular destinations:** Bay Area, Austin, New York, Seattle, Boston\n\n"
            "**Top programs for Indians:** CS, Data Science, EE, Business Analytics, Finance\n\n"
            "Which field are you considering for the US?"
        )
    return (
        "Hello! I'm your **StudyBridge AI Advisor** 🎓\n\n"
        "I'm here to guide you through every step of your higher education journey. Here's what I can help with:\n\n"
        "- 🧭 **University selection** — Personalized program recommendations\n"
        "- 📚 **Test prep** — GRE, GMAT, IELTS, TOEFL strategies\n"
        "- ✍️ **Applications** — SOP, LOR, resume tips\n"
        "- 🛂 **Visa guidance** — F-1, UK, Canada, Germany student visas\n"
        "- 💰 **Education loans** — Compare SBI, HDFC, Axis, InCred & more\n"
        "- 🌍 **Career planning** — Salary benchmarks, ROI analysis\n\n"
        "*(Running in demo mode — add your Anthropic API key for full AI responses)*\n\n"
        "What would you like to explore today?"
    )
