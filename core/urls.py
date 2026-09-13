from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('',                               views.landing,                     name='landing'),
    path('register/',                      views.register_view,               name='register'),
    path('login/',                         views.login_view,                  name='login'),
    path('logout/',                        views.logout_view,                 name='logout'),

    # Student Journey & Onboarding
    path('dashboard/',                     views.dashboard,                   name='dashboard'),
    path('onboarding/',                    views.onboarding_view,             name='onboarding'),
    path('calculate-profile-score/',       views.calculate_profile_score_api, name='calculate_profile_score'),
    path('profile/',                       views.profile_view,                name='profile'),
    path('my-journey/',                    views.my_journey,                  name='my_journey'),
    path('timeline/',                      views.timeline_view,               name='timeline'),

    # Module 1: Career Navigator (RIASEC)
    path('career-assessment/',             views.career_assessment,          name='career_assessment'),
    path('navigator/',                     views.career_navigator,            name='career_navigator'),
    path('navigator/result/',              views.navigator_result,            name='navigator_result'),

    # Module 2: University Intelligence & Comparison
    path('universities/',                  views.university_search,           name='university_search'),
    path('compare-universities/',          views.compare_universities,        name='compare_universities'),

    # Module 3: Admission Predictor (ML Scoring Engine)
    path('admission-predictor/',           views.admission_predictor_view,    name='admission_predictor'),

    # Module 4: Advanced Financial Modeling & Loans
    path('roi-calculator/',                views.roi_calculator_view,         name='roi_calculator'),
    path('loans/',                         views.loan_marketplace,            name='loan_marketplace'),
    path('loans/estimator/',               views.loan_estimator,              name='loan_estimator'),
    path('loans/emi/',                     views.emi_calculator_view,         name='emi_calculator'),
    path('loans/apply/',                   views.loan_application_view,       name='loan_application'),

    # Module 5: Scholarships
    path('scholarships/',                  views.scholarship_finder,          name='scholarships'),

    # Module 6: Applications & SOP Document Analysis
    path('track-applications/',            views.application_tracker,         name='application_tracker'),
    path('update-application-status/',     views.update_application_status,   name='update_application_status'),
    path('documents/',                     views.document_manager,            name='document_manager'),

    # Module 7: AI Advisor & Study Planner
    path('chat/',                          views.chatbot_view,                name='chatbot'),
    path('api/chat/',                      views.chat_api,                    name='chat_api'),
    path('study-planner/',                 views.study_planner_view,          name='study_planner'),

    # Module 8: Mentors, Admin & Notifications
    path('mentors/',                       views.mentor_marketplace,          name='mentor_marketplace'),
    path('book-mentor/',                   views.book_mentor_session,         name='book_mentor_session'),
    path('admin-dashboard/',               views.admin_dashboard,             name='admin_dashboard'),
    path('api/notifications/',             views.get_notifications_api,       name='get_notifications_api'),
    path('api/notifications/<str:nid>/read/', views.mark_notification_read_api, name='mark_notification_read_api'),
]
