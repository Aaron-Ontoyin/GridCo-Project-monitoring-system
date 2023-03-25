from django.urls import path

from . import views


urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('index', views.IndexView.as_view(), name='index'),
    path('project/<str:pk>', views.ProjectView.as_view(), name='project'),
    path('profile/<str:pk>', views.ProfileView.as_view(), name='profile'),
    path('logout', views.logoutView, name='logout'),

    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]