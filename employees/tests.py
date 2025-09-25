from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from.models import Employee

class EmployeeAPITests(APITestCase):
    def setUp(self):
        """Denna metod körs före varje enskilt test och sätter upp en ren miljö."""
        self.employee1 = Employee.objects.create(
            first_name="Rambo", last_name="Lambo", email="Rambo.Lambo@DM.com"
        )
        self.employee2 = Employee.objects.create(
            first_name="Tand", last_name="Läkare", email="Tand.Läkare@DM.com"
        )
        self.list_url = reverse('employee-list')

    def test_get_all_employees(self):
        """Verifierar att vi kan hämta en lista över alla anställda."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_add_new_employee(self):
        """Verifierar att vi kan lägga till en ny anställd."""
        data = {
            "first_name": "Tand",
            "last_name": "Hygienist",
            "email": "Tand.Hygienist@DM.com"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 3)

    def test_add_employee_with_duplicate_name_and_unique_email_succeeds(self):
        """
        NYTT TEST: Verifierar att vi kan skapa en anställd med samma namn som en
        befintlig, så länge e-postadressen är unik.
        """
        data = {
            "first_name": "Rambo",           # Samma förnamn som employee1
            "last_name": "Lambo",       # Samma efternamn som employee1
            "email": "Rambo.Lambo.2@DM.com" # Unik e-post
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 3)

    def test_add_employee_with_duplicate_email_fails(self):
        """Verifierar att API:et korrekt nekar en anställd med en upptagen e-post."""
        data = {
            "first_name": "Tand",
            "last_name": "Läkare",
            "email": "Tand.Läkare@DM.com" # Duplicerad e-post
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_delete_specific_employee(self):
        """
        UPPDATERAT TEST: Verifierar att vi kan ta bort en specifik anställd
        utan att påverka andra anställda.
        """
        # Vi har två anställda från start: employee1 (Ada) och employee2 (Grace)
        self.assertEqual(Employee.objects.count(), 2)
        
        # Radera endast employee1 (Ada)
        detail_url = reverse('employee-detail', kwargs={'pk': self.employee1.pk})
        response = self.client.delete(detail_url)
        
        # Verifiera att anropet lyckades och att antalet anställda nu är 1
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 1)
        
        # Verifiera att employee1 är borta, men employee2 fortfarande finns kvar
        self.assertFalse(Employee.objects.filter(pk=self.employee1.pk).exists())
        self.assertTrue(Employee.objects.filter(pk=self.employee2.pk).exists())
