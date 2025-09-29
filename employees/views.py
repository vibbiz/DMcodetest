from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeSerializer

# In-memory storage (försvinner vid omstart)
EMPLOYEES = []
NEXT_ID = 1

class EmployeeView(APIView):
    """
    GET  /employees/       -> lista alla anställda
    POST /employees/       -> skapa ny anställd (unikt email, case-insensitive)
    """
    def get(self, request):
        serializer = EmployeeSerializer(EMPLOYEES, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        global NEXT_ID
        serializer = EmployeeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        # Kontrollera unik e-post (case-insensitive)
        if any(e['email'].lower() == email.lower() for e in EMPLOYEES):
            return Response(
                {"error": "E-postadressen finns redan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = {
            'id': NEXT_ID,
            'first_name': serializer.validated_data['first_name'],
            'last_name': serializer.validated_data['last_name'],
            'email': email,
        }
        EMPLOYEES.append(employee)
        NEXT_ID += 1
        return Response(employee, status=status.HTTP_201_CREATED)


class EmployeeDetail(APIView):
    """
    GET    /employees/<id>/ -> hämta en anställd
    DELETE /employees/<id>/ -> radera anställd med id
    """
    def get(self, request, employee_id: int):
        match = next((e for e in EMPLOYEES if e['id'] == employee_id), None)
        if not match:
            return Response({"error": "Anställd hittades inte."}, status=status.HTTP_404_NOT_FOUND)
        return Response(match, status=status.HTTP_200_OK)

    def delete(self, request, employee_id: int):
        global EMPLOYEES
        match = next((e for e in EMPLOYEES if e['id'] == employee_id), None)
        if not match:
            return Response({"error": "Anställd hittades inte."}, status=status.HTTP_404_NOT_FOUND)
        EMPLOYEES = [e for e in EMPLOYEES if e['id'] != employee_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
