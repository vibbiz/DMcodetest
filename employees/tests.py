from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from.models import Employee

class EmployeeAPITests(APITestCase):
    def setUp(self):
        self.employee1 = Employee.objects.create(
            first_name="Rambo", last_name="Lambo", email="Rambo.Lambo@DM.com"
        )
        self.list_url = reverse('employee-list')

    def test_get_all_employees(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_new_employee(self):
        data = {
            "first_name": "Tand",
            "last_name": "Läkare",
            "email": "Tand.Läkare@DM.com"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

    def test_add_employee_with_duplicate_email_fails(self):
        data = {
            "first_name": "Rambo",
            "last_name": "Lambo",
            "email": "Rambo.Lambo@DM.com"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_delete_employee(self):
        detail_url = reverse('employee-detail', kwargs={'pk': self.employee1.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)
