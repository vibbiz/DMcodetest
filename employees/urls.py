from django.urls import path
from .views import EmployeeListCreateAPIView, EmployeeDestroyAPIView

urlpatterns = [
    path("employees/", EmployeeListCreateAPIView.as_view(), name="employee-list"),
    path("employees/<int:pk>/", EmployeeDestroyAPIView.as_view(), name="employee-detail"),
]
