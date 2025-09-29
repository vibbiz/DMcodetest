import sys
import requests

BASE = "http://127.0.0.1:8000"
EMP = f"{BASE}/employees/"

def must_status(resp, expected, note=""):
    if resp.status_code != expected:
        print(f"[{note}] Expected {expected}, got {resp.status_code}")
        try:
            print("Response JSON:", resp.json())
        except Exception:
            print("Response TEXT:", resp.text[:500])
        sys.exit(1)

def purge_all():
    print("Purging any pre-existing employees")
    r = requests.get(EMP)
    must_status(r, 200, "GET list (purge step)")
    data = r.json()
    if not isinstance(data, list):
        print("ERROR: /employees/ did not return a JSON list.")
        print("Payload:", data)
        sys.exit(1)
    for e in data:
        delr = requests.delete(f"{EMP}{e['id']}/")
        must_status(delr, 204, f"DELETE id={e['id']}")
    # verify empty
    r = requests.get(EMP)
    must_status(r, 200, "GET verify empty after purge")
    assert isinstance(r.json(), list) and len(r.json()) == 0

def run():
    print("Test: reset state")
    purge_all()

    print("Test: GET tom lista")
    r = requests.get(EMP)
    must_status(r, 200, "GET empty")
    assert isinstance(r.json(), list) and len(r.json()) == 0

    print("Test: POST validering saknade fält")
    r = requests.post(EMP, json={"first_name": "Rambo"})
    assert r.status_code == 400 and "last_name" in r.json() and "email" in r.json()

    print("Test: POST validering ogiltig e-post")
    r = requests.post(EMP, json={"first_name":"A","last_name":"B","email":"not-an-email"})
    assert r.status_code == 400 and "email" in r.json()

    print("Test: POST tre korrekta anställda")
    ram = {"first_name":"Rambo","last_name":"Lambo","email":"rambo.lambo@DM.se"}
    lak = {"first_name":"Tand","last_name":"Läkare","email":"tand.lakare@DM.se"}
    hyg = {"first_name":"Tand","last_name":"Hygienst","email":"tand.hygienst@DM.se"}

    r1 = requests.post(EMP, json=ram); must_status(r1, 201, "POST rambo")
    r2 = requests.post(EMP, json=lak); must_status(r2, 201, "POST lakare")
    r3 = requests.post(EMP, json=hyg); must_status(r3, 201, "POST hygienst")

    # Kontrollera schema i POST-svaret
    for resp in (r1, r2, r3):
        body = resp.json()
        for k in ("id","first_name","last_name","email"):
            assert k in body, f"POST response missing key: {k}"

    ids = [r1.json()["id"], r2.json()["id"], r3.json()["id"]]
    assert len(set(ids)) == 3

    print("Test: POST dublett-e-post (exakt)")
    r = requests.post(EMP, json=ram)
    assert r.status_code == 400 and "error" in r.json()

    print("Test: POST dublett-e-post (case-insensitive + trim)")
    r = requests.post(EMP, json={**ram, "email":"   RAMBO.LAMBO@dm.se   "})
    assert r.status_code == 400 and "error" in r.json()

    print("Test: Tillåt samma namn med annan e-post (krav i uppgiften)")
    same_name = {"first_name":"Rambo","last_name":"Lambo","email":"rambo.lambo2@DM.se"}
    r_same = requests.post(EMP, json=same_name); must_status(r_same, 201, "POST same-name-diff-email")
    # Rensa den direkt så ursprungliga räkningarna nedan fortfarande stämmer
    same_id = r_same.json()["id"]
    must_status(requests.delete(f"{EMP}{same_id}/"), 204, "DELETE same-name temp")

    print("Test: GET lista efter skapanden")
    r = requests.get(EMP); must_status(r, 200, "GET after create")
    data = r.json()
    assert len(data) == 3
    emails = {e["email"] for e in data}
    assert emails == {"rambo.lambo@DM.se","tand.lakare@DM.se","tand.hygienst@DM.se"}

    print("Test: GET enskild (finns)")
    rid = ids[1]
    r = requests.get(f"{EMP}{rid}/"); must_status(r, 200, "GET one existing")
    assert r.json()["id"] == rid

    print("Test: GET enskild (saknas)")
    r = requests.get(f"{EMP}999999/"); must_status(r, 404, "GET one missing")

    print("Test: 405 Method Not Allowed på samling (PUT)")
    r = requests.put(EMP, json={})
    assert r.status_code in (405, 403), f"Expected 405/403 for PUT on collection, got {r.status_code}"

    print("Test: DELETE (finns)")
    r = requests.delete(f"{EMP}{ids[0]}/"); must_status(r, 204, "DELETE existing")

    print("Test: DELETE (saknas)")
    r = requests.delete(f"{EMP}{ids[0]}/"); must_status(r, 404, "DELETE missing")

    print("Test: GET lista efter delete")
    r = requests.get(EMP); must_status(r, 200, "GET after delete")
    assert len(r.json()) == 2

    print("ALLA TESTER OK")

if __name__ == "__main__":
    try:
        run()
    except requests.exceptions.ConnectionError:
        print("Kunde inte ansluta. Är servern igång? Kör: python manage.py runserver")
        sys.exit(1)
