"""
URL configuration for Employee_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import SignupView, Verify_otp_View, LoginView
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignupView, name='signup'),
    path('verify/', Verify_otp_View, name='verify'),
    path('login/', LoginView, name='login'),
    path('forgot-password/', views.Forgot_password_View, name='forgot-password'),
    path('verify-reset-otp/', views.Verify_otp_View, name='verify-reset-otp'),
    path('reset-password/', views.reset_password_View, name='reset-password'),
    path('logout/', views.LOgoutView, name='logout'),
    path('assign/task/employee/', views.assign_task_to_employee, name='assign-task-employee'),
    path('manager/task/list/', views.Manager_assigned_task_list, name='manager-task-list'),
    path('manager/employee/list/', views.Manager_list_all_employees, name='manager-employee-list'),
    path('manager/employee/<int:pk>/',views.Manager_employee_details, name='manager-employee-details'),
    path('manager/employee/<int:pk>/delete/',views.Manager_delete_employee, name='manager-employee-delete'),


    # employee urls
    path('employee/task/list/', views.Employee_task_list_view, name='employee-tasks'),
    path('employee/leave/', views.Employee_leave_view, name='employee-leave'),
]
