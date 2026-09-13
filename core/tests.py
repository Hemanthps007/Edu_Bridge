from django.test import TestCase
from .admission_predictor import admission_predictor
from utils.loan_calculator import calculate_emi, get_loan_options
from utils.profile_scorer import calculate_profile_scores
from utils.career_matcher import score_riasec
from utils.roi_engine import calculate_advanced_roi
from services.data_providers.curated import CuratedDataProvider
from services.ai_document_analyzer import analyze_sop_content

class AdmissionPredictorTests(TestCase):
    def test_predictor_outputs_and_boundaries(self):
        profile = {
            'gre': 325,
            'gpa': 3.8,
            'ielts': 7.5,
            'work_exp': 2,
            'research': 1,
            'internships': 2,
            'projects': 3
        }
        res = admission_predictor.predict(profile, target_rank=40)
        self.assertIn('probability', res)
        self.assertTrue(5.0 <= res['probability'] <= 95.0)
        self.assertIn(res['category'], ['Safe', 'Target', 'Reach'])
        self.assertGreater(len(res['factor_breakdown']), 4)
        self.assertTrue(any('CGPA' in f['factor'] for f in res['factor_breakdown']))

    def test_predictor_reach_tier_for_top_1(self):
        profile = {
            'gre': 295,
            'gpa': 2.8,
            'ielts': 6.0,
            'work_exp': 0,
            'research': 0,
            'internships': 0,
            'projects': 1
        }
        res = admission_predictor.predict(profile, target_rank=1)
        self.assertEqual(res['category'], 'Reach')


class LoanCalculatorTests(TestCase):
    def test_emi_calculation(self):
        # Principal 12 Lakhs at 10% for 1 year (12 months)
        principal = 1200000
        rate = 10.0
        tenure_months = 12
        emi = calculate_emi(principal, rate, tenure_months)
        # Expected EMI around ~₹105,499
        self.assertTrue(100000 <= emi <= 110000)

    def test_loan_options_catalog(self):
        opts = get_loan_options(3500000, tenure_years=10, has_collateral=False)
        self.assertIn('offers', opts)
        self.assertGreaterEqual(len(opts['offers']), 5)
        first_offer = opts['offers'][0]
        self.assertIn('bank_name', first_offer)
        self.assertIn('emi', first_offer)


class ProfileScorerTests(TestCase):
    def test_profile_scorer_dimensions(self):
        sample_profile = {
            'degree_cgpa': 8.6,
            'tenth_pct': 88,
            'twelfth_pct': 90,
            'country_goal': 'USA',
            'budget': '3500000',
            'target_program': 'MS Computer Science',
            'interests': ['AI & Machine Learning'],
            'career_assessment_completed': True,
            'gre_score': 320,
            'ielts_score': 7.5,
            'work_exp': 2,
            'internships': 2,
            'projects': 3
        }
        scores = calculate_profile_scores(sample_profile)
        self.assertIn('academic_strength', scores)
        self.assertIn('financial_readiness', scores)
        self.assertIn('career_clarity', scores)
        self.assertIn('admission_readiness', scores)
        self.assertIn('overall_score', scores)

        for dim in ['academic_strength', 'financial_readiness', 'career_clarity', 'admission_readiness', 'overall_score']:
            self.assertTrue(10 <= scores[dim] <= 100, f"Score {dim} = {scores[dim]} out of bounds")


class CareerMatcherTests(TestCase):
    def test_riasec_scoring_and_recommendations(self):
        answers = {
            'q_i_1': '5', 'q_i_2': '5',
            'q_r_1': '4', 'q_r_2': '4',
            'q_c_1': '4',
            'q_e_1': '2',
            'q_s_1': '3',
            'q_a_1': '2'
        }
        res = score_riasec(answers)
        self.assertIn('holland_code', res)
        self.assertIn('recommendations', res)
        self.assertGreater(len(res['recommendations']), 0)
        self.assertTrue(res['recommendations'][0]['match_pct'] >= 70)


class AdvancedROIEngineTests(TestCase):
    def test_roi_calculation(self):
        params = {
            'tuition': 45000,
            'accommodation': 12000,
            'food': 6000,
            'insurance': 2000,
            'duration': 2,
            'country': 'USA',
            'field': 'Computer Science'
        }
        res = calculate_advanced_roi(params)
        self.assertIn('total_investment_usd', res)
        self.assertIn('payback_years', res)
        self.assertIn('five_year_roi_pct', res)
        self.assertIn('scenarios', res)
        self.assertIn('best_case', res['scenarios'])
        self.assertIn('expected_case', res['scenarios'])
        self.assertIn('worst_case', res['scenarios'])


class DataProviderTests(TestCase):
    def test_curated_data_provider(self):
        provider = CuratedDataProvider()
        unis = provider.search_universities(country='USA', limit=5)
        self.assertGreater(len(unis), 0)
        cmu = provider.get_university_by_id('cmu')
        self.assertIsNotNone(cmu)
        self.assertEqual(cmu['name'], 'Carnegie Mellon University')
        courses = provider.get_courses('cmu')
        self.assertGreater(len(courses), 0)


class DocumentAnalyzerTests(TestCase):
    def test_sop_analyzer_local_heuristics(self):
        sop_text = "I have always been driven by the mathematical principles of computation and distributed systems. At university, I built scalable pipeline tools."
        res = analyze_sop_content(sop_text, "Stanford University", "MS Computer Science")
        self.assertIn('structure_score', res)
        self.assertIn('clarity_score', res)
        self.assertIn('overall_score', res)
        self.assertIn('strengths', res)
        self.assertIn('suggestions', res)


class TemplateRenderingRegressionTests(TestCase):
    def setUp(self):
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware
        from core import firebase_client as fb

        self.factory = RequestFactory()
        self.uid = 'test_user_minimal'
        # Minimal profile without gre_score or gpa (matching user DB scenario)
        fb.set_doc('users', self.uid, {
            'uid': self.uid,
            'name': 'Hemanth P S',
            'email': 'pshemanth2@gmail.com',
            'degree': 'PhD',
            'country_goal': 'Germany'
        })

    def _prepare_request(self, request):
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(lambda r: None)
        message_middleware.process_request(request)
        request.session['user'] = {'uid': self.uid, 'email': 'pshemanth2@gmail.com', 'name': 'Hemanth P S'}
        request.session.save()

    def test_admission_predictor_view_get(self):
        from core.views import admission_predictor_view
        req = self.factory.get('/admission-predictor/')
        self._prepare_request(req)
        response = admission_predictor_view(req)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('University Admission Predictor', content)

    def test_scholarship_finder_view_get(self):
        from core.views import scholarship_finder
        req = self.factory.get('/scholarships/')
        self._prepare_request(req)
        response = scholarship_finder(req)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('International Scholarship Finder', content)

    def test_dashboard_view_get(self):
        from core.views import dashboard
        req = self.factory.get('/dashboard/')
        self._prepare_request(req)
        response = dashboard(req)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Study Abroad Journey', content)


class SupabaseAndDatabaseTests(TestCase):
    def test_supabase_client_unconfigured_safe_fallback(self):
        from core.supabase_client import get_supabase_client
        client = get_supabase_client()
        self.assertIsNone(client)

    def test_database_crud_operations(self):
        from core import firebase_client as fb
        test_uid = 'test_user_supabase_validation'
        test_data = {'name': 'Supabase Test', 'email': 'supabase@example.com', 'country_goal': 'Canada'}
        saved = fb.set_doc('users', test_uid, test_data)
        self.assertTrue(saved)

        doc = fb.get_doc('users', test_uid)
        self.assertIsNotNone(doc)
        self.assertEqual(doc.get('email'), 'supabase@example.com')

        matches = fb.query_docs('users', 'email', '==', 'supabase@example.com')
        self.assertGreaterEqual(len(matches), 1)

        deleted = fb.delete_doc('users', test_uid)
        self.assertTrue(deleted)
        self.assertIsNone(fb.get_doc('users', test_uid))


