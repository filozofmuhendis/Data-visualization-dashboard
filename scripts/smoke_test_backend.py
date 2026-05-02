import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("GET /api/health:")
resp = client.get("/api/health")
print(resp.status_code, resp.text)

print("\nPOST /api/auth/login (commander/cmd123):")
login = client.post("/api/auth/login", json={"username": "commander", "password": "cmd123"})
print(login.status_code, login.text[:300])
try:
    data = login.json()
except Exception as e:
    print("Login JSON parse error:", e)
    data = {}
print("Has access_token:", "access_token" in data)

if "access_token" in data:
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("\nGET /api/auth/me:")
    me = client.get("/api/auth/me", headers=headers)
    print(me.status_code, me.text[:300])

print("\nGET /api/alerts:")
alerts = client.get("/api/alerts")
print(alerts.status_code, alerts.text[:300])

print("\nGET /api/weather:")
weather = client.get("/api/weather")
print(weather.status_code, weather.text[:300])