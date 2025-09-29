from django.urls import path
from .views import EmployeeView, EmployeeDetail

urlpatterns = [
    path('employees/', EmployeeView.as_view(), name='employee-list'),
    path('employees/<int:employee_id>/', EmployeeDetail.as_view(), name='employee-detail'),
]
