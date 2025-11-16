import requests

USER_SERVICE_URL = "http://localhost:3203/"

def checkAdmin(user_id):
    try:
        resp = requests.get(f"{USER_SERVICE_URL}/users/isadmin/{user_id}")
        if resp.status_code == 200:
            return resp.json().get("admin", False)
    except Exception:
        pass
    return False