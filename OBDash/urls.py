from django.urls import path
from .views import (
    add_student, dashboard, login_view, logout_view, evaluation_checklist,
    submit_cognitive_evaluation, submit_expressive_evaluation,
    submit_fine_evaluation, submit_gross_evaluation,
    submit_receptive_evaluation,
    submit_selfhelp_evaluation, submit_social_evaluation,
    performance_view,
    settings_view,
    parent_view_social_emotional
)

urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add_student/', add_student, name='add_student'),
    path('logout/', logout_view, name='logout'),
    path('evaluation-checklist/', evaluation_checklist, name='evaluation_checklist'),
    path('submit-cognitive-evaluation/', submit_cognitive_evaluation, name='submit_cognitive_evaluation'),
    path('submit-expressive-evaluation/', submit_expressive_evaluation, name='submit_expressive_evaluation'),
    path('submit-fine-evaluation/', submit_fine_evaluation, name='submit_fine_evaluation'),
    path('submit-gross-evaluation/', submit_gross_evaluation, name='submit_gross_evaluation'),
    path('submit-receptive-evaluation/', submit_receptive_evaluation, name='submit_receptive_evaluation'),
    path('submit-selfhelp-evaluation/', submit_selfhelp_evaluation, name='submit_selfhelp_evaluation'),
    path('submit-social-evaluation/', submit_social_evaluation, name='submit_social_evaluation'),
    path('performance/', performance_view, name='performance'),
    path('settings/', settings_view, name='settings'),
    
]
