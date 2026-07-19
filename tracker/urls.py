from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('c/<slug:slug>/', views.calendar_view, name='calendar'),
    path('c/<slug:slug>/toggle/', views.toggle_workout, name='toggle_workout'),
    path('c/<slug:slug>/goals/', views.goals_view, name='goals'),
]
