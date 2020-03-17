from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND
)
from rest_api import queries
from rest_api.authentication import token_expire_handler
from rest_api.serializers import UserSerializer, UserLoginSerializer
from .models import Doctor, Client, CustomAdmin
from .utils import *


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=login_serializer.data["username"], password=login_serializer.data["password"])

    if not user:
        message = "Invalid login credentials!"
        return Response({"detail": message}, status=HTTP_404_NOT_FOUND)

    # TOKEN STUFF
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)
    user_serialized = UserSerializer(user)

    return Response({"role": get_role(user.username), "data": user_serialized.data, "token": token.key},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def logout(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    try:
        Token.objects.get(key=auth_token).delete()
    except Token.DoesNotExist:
        pass
    return Response(status=HTTP_200_OK)


@api_view(["POST"])
def new_admin(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "admin"):
        state = "Error"
        message = "You do not have permissions to add a new admin"
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data

    if not (
            "email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "hospital" in data
    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_admin(data)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET", "PUT", "DELETE"])
def admin_rud(request, email):
    if request.method == "PUT":
        return update_admin(request, email)
    elif request.method == "DELETE":
        return delete_admin(request, email)
    elif request.method == "GET":
        return get_admin(request, email)


def update_admin(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.update_admin(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_admin(request, email):
    token, username, role = who_am_i(request)

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_admin(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.get_admin(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["POST"])
@permission_classes((AllowAny,))
def new_client(request):
    data = request.data
    if not ("email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "height" in data
            and "weight_goal" in data
            and "birth_date" in data):
        return Response({"state": "Error", "message": "Missing parameters"}, status=HTTP_400_BAD_REQUEST)

    state, message = queries.add_client(data)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"state": state, "message": message}, status=status)


@api_view(["GET", "PUT", "DELETE"])
def client_rud(request, email):
    if request.method == "PUT":
        return update_client(request, email)
    elif request.method == "DELETE":
        return delete_client(request, email)
    elif request.method == "GET":
        return get_client(request, email)


def update_client(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.update_client(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_client(request, email):
    token, username, role = who_am_i(request)

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_client(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.get_client(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_client(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["POST"])
def new_doctor(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "admin"):
        state = "Error"
        message = "You do not have permissions to add a new doctor"
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not (
            "email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "birth_date" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    admin_hospital = CustomAdmin.objects.get(auth_user__username=username).hospital
    state, message = queries.add_doctor(data, admin_hospital)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET", "PUT", "DELETE"])
def doctor_rud(request, email):
    if request.method == "PUT":
        return update_doctor(request, email)
    elif request.method == "DELETE":
        return delete_doctor(request, email)
    elif request.method == "GET":
        return get_doctor(request, email)


def update_doctor(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.update_doctor(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_doctor(request, email):
    token, username, role = who_am_i(request)
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state = "Error"
    message = "You do not have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "admin") and is_doctor_admin(email, username):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_doctor(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.get_doctor(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "client") and is_client_doctor(email, username):
        state, message = queries.get_doctor(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "admin") and is_doctor_admin(email, username):
        state, message = queries.get_doctor(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["POST"])
def new_food_log(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to create a food log in this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.update_admin(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    data = request.data
    if not (
            "day" in data
            and "type_of_meal" in data
            and "meal" in data
            and "client" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_food_log(data)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)
