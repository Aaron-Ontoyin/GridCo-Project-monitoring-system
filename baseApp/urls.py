from django.urls import path
from . import views


urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home', views.IndexView.as_view(), name='index'),
    path('project/<str:pk>', views.ProjectView.as_view(), name='project'),
]