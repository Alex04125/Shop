import requests, os


def login(request):
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        json={"email": email, "password": password},
    )
    if response.status_code == 200:
        return response.text
    else:
        return None


def register(request):
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/register",
        json={"email": email, "password": password},
    )

    if response.status_code == 200:
        return response.text
    else:
        return None


def validate(request):
    token = request.header["Authorization"]

    if not token:
        return None, ("Missing credentials", 401)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return True
    else:
        return None
