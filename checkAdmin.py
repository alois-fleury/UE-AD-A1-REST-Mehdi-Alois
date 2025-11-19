import requests

USER_SERVICE_URL = "http://127.0.0.1:3203/"

def checkAdmin(user_id):
    print("on passe par checkadmin")
    try:
        resp = requests.get(f"{USER_SERVICE_URL}/users/isadmin/{user_id}?uid={user_id}")
        print("on a eu le get")
        if resp.status_code == 200:
            return resp.json().get("admin", False)
    except Exception:
        pass
    return False