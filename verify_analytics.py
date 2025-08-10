import json
import sys
import urllib.request as u
import urllib.error as e

BASE = "http://localhost:8000/api/v1"
EMAIL = "analytics_test@example.com"
PASSWORD = "Passw0rd!"


def post(path, payload, headers=None):
    data = json.dumps(payload).encode()
    req = u.Request(BASE + path, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    return u.urlopen(req)


def get(path, headers=None):
    req = u.Request(BASE + path, headers=headers or {})
    return u.urlopen(req)


def main():
    token = None
    # Try register first
    try:
        resp = post("/register/", {
            "email": EMAIL,
            "password": PASSWORD,
            "first_name": "Analytics",
            "last_name": "User"
        })
        data = json.loads(resp.read())
        token = data.get("access")
        print("register: ", resp.getcode())
    except e.HTTPError as err:
        print("register_error:", err.code)
        # Try login (custom login accepts email/password)
        try:
            resp = post("/login/", {"email": EMAIL, "password": PASSWORD})
            data = json.loads(resp.read())
            token = data.get("access")
            print("login: ", resp.getcode())
        except e.HTTPError as err2:
            print("login_error:", err2.code, err2.read())
            sys.exit(2)

    if not token:
        print("No access token received")
        sys.exit(3)

    headers = {"Authorization": f"Bearer {token}"}

    # Probe endpoints
    for path in ["/analytics/summary/", "/analytics/export/devices.csv", "/analytics/export/impressions.csv"]:
        try:
            resp = get(path, headers=headers)
            content_type = resp.headers.get("Content-Type")
            print(f"{path} -> {resp.getcode()} {content_type}")
        except e.HTTPError as herr:
            print(f"{path} -> ERROR {herr.code}", herr.read())
            sys.exit(4)


if __name__ == "__main__":
    main()
