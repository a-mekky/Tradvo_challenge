from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('', views.app_list, name='app_list'),

    path('app/<int:pk>/', views.app_detail, name='app_detail'),
    path('app/add/', views.app_add, name='app_add'),

    path('run_test/<int:app_id>/', views.run_appium_test, name='run_appium_test'),

    path('app/<int:pk>/edit/', views.app_edit, name='app_edit'),
    path('app/<int:pk>/delete/', views.app_delete, name='app_delete'),
]
