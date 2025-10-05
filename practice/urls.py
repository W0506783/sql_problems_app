# practice/urls.py
from django.urls import path
from . import views

app_name = 'practice'

urlpatterns = [
    # This line has the correct function name: 'views.problem_detail'
    path('<int:problem_id>/', views.problem_detail, name='problem_detail'),
]