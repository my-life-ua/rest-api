from django.contrib.auth.models import User, Group

from rest_api.models import CustomAdmin


def login(client, username, pwd):
    response = client.post("/login", {"username": username, "password": pwd})
    token = response.data["token"]
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")


def create_user_and_login(client, role, username, email, password, hospital="Hospital de São João"):
    if role == "client":
        user = User.objects.create_user(username, email, password)
        clients_group = Group.objects.get_or_create(name="clients_group")[0]
        clients_group.user_set.add(user)
    elif role == "admin":
        User.objects.create_superuser(username, email, password)
    elif role == "custom_admin":
        auth_user = User.objects.create_superuser(username, email, password)
        CustomAdmin.objects.create(auth_user=auth_user, hospital=hospital)
    login(client, username, password)