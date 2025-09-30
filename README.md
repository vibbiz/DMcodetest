# Personalregister API (Django REST Framework, in-memory)

Ett minimalistiskt REST-API för att hantera anställda. Data lagras i minnet (försvinner vid omstart).  
Operationer:
- **GET** `/employees/` – hämta alla anställda
- **POST** `/employees/` – skapa ny anställd (`first_name`, `last_name`, `email` krävs; e-post unik, case-insensitive)
- **GET** `/employees/<id>/` – hämta en specifik anställd
- **DELETE** `/employees/<id>/` – ta bort en anställd

## Tech
- Python 3.10+ (testad på 3.13)
- Django 4.2
- Django REST Framework 3.15
- requests (för integrationstest)

## Projektstruktur (kort)
```
.
├─ manage.py
├─ requirements.txt
├─ README.md
├─ test.py                # integrationstest (kör mot servern)
├─ personnel_api/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
└─ employees/
   ├─ __init__.py
   ├─ apps.py
   ├─ serializers.py
   ├─ urls.py
   └─ views.py
```

## Installation (Windows)

```powershell
# 1) Gå till projektmappen (den som innehåller manage.py)
cd C:\Users\<du>\Downloads\DMcodetest

# 2) Skapa och aktivera virtuell miljö (rekommenderas)
python -m venv venv
.
env\Scripts\Activate.ps1

# 3) Installera beroenden
pip install -r requirements.txt
```

> **Obs om migrationer:** Django kan varna om "unapplied migrations" (t.ex. contenttypes/sessions). Dessa behövs inte för själva API-logiken (allt är in-memory), men du kan köra:
> ```powershell
> python manage.py migrate
> ```

## Starta servern

```powershell
python manage.py runserver
```

Server: `http://127.0.0.1:8000/`  
API:
- Lista: `http://127.0.0.1:8000/employees/`
- En specifik: `http://127.0.0.1:8000/employees/2/` (byt `2`)

## Testa manuellt (PowerShell)

**PowerShell-native (`Invoke-RestMethod`)**
```powershell
# Lista alla
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/ -Method Get

# Skapa – Rambo Lambo
$body = @{ first_name="Rambo"; last_name="Lambo"; email="rambo.lambo@DM.se" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/ -Method Post -ContentType 'application/json' -Body $body

# Skapa – Tand Läkare
$body = @{ first_name="Tand"; last_name="Läkare"; email="tand.lakare@DM.se" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/ -Method Post -ContentType 'application/json' -Body $body

# Skapa – Tand Hygienst
$body = @{ first_name="Tand"; last_name="Hygienst"; email="tand.hygienst@DM.se" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/ -Method Post -ContentType 'application/json' -Body $body

# Dublett-test (ska ge 400)
$body = @{ first_name="Rambo"; last_name="Lambo"; email="rambo.lambo@DM.se" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/ -Method Post -ContentType 'application/json' -Body $body

# Hämta en specifik (byt 2)
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/2/ -Method Get

# Ta bort (byt 2)
Invoke-RestMethod -Uri http://127.0.0.1:8000/employees/2/ -Method Delete
```

**Riktig curl i PowerShell (`curl.exe`)**
```powershell
curl.exe http://127.0.0.1:8000/employees/

curl.exe -X POST http://127.0.0.1:8000/employees/ ^
  -H "Content-Type: application/json" ^
  -d "{""first_name"":""Rambo"",""last_name"":""Lambo"",""email"":""rambo.lambo@DM.se""}"
```

## Integrationstester

`test.py` kör hela flödet (validering, skapande, dublett, GET/DELETE, etc). Kör i **ny terminal** med samma venv aktiv och servern igång:

```powershell
python test.py
```

Täckning i `test.py`:
- GET tom lista
- POST utan obligatoriska fält (400)
- POST med ogiltig e-post (400)
- POST tre giltiga (Rambo Lambo, Tand Läkare, Tand Hygienst)
- POST dublett-e-post (exakt & case-insensitive) → 400
- GET lista efter skapanden (3 st)
- GET enskild (finns & saknas)
- DELETE (finns & saknas)
- GET lista efter delete (2 kvar)



## Säkerhet

- `SECRET_KEY` är hårdkodad för test. **Använd aldrig så i produktion.**
- Ingen auth krävs för endpoints i denna version, ej rekommenderat.

