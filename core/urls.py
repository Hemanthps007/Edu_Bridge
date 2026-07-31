from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.landing,            name='landing'),
    path('register/',               views.register_view,      name='register'),
    path('login/',                  views.login_view,         name='login'),
    path('logout/',                 views.logout_view,        name='logout'),
    path('dashboard/',              views.dashboard,          name='dashboard'),
    path('profile/',                views.profile_view,       name='profile'),
    path('navigator/',              views.career_navigator,   name='career_navigator'),
    path('navigator/result/',       views.navigator_result,   name='navigator_result'),
    path('roi-calculator/',         views.roi_calculator,     name='roi_calculator'),
    path('admission-predictor/',    views.admission_predictor,name='admission_predictor'),
    path('timeline/',               views.timeline_view,      name='timeline'),
    path('loans/estimator/',        views.loan_estimator,     name='loan_estimator'),
    path('loans/emi/',              views.emi_calculator,     name='emi_calculator'),
    path('loans/apply/',            views.loan_application,   name='loan_application'),
    path('chat/',                   views.chatbot,            name='chatbot'),
    path('api/chat/',               views.chat_api,           name='chat_api'),
]
