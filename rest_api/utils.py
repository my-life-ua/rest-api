from datetime import datetime, date

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from rest_api.models import Doctor, CustomAdmin, Client


def get_role(username, request=None):
    role = None
    try:
        if username is None:
            username = request.user.username

        if User.objects.get(username=username).is_superuser:
            role = "admin"
        elif User.objects.get(username=username).groups.all()[0].name in ["clients_group"]:
            role = "client"
        elif User.objects.get(username=username).groups.all()[0].name in ["doctors_group"]:
            role = "doctor"

    except User.DoesNotExist:
        role = None

    return role


def who_am_i(request):
    token = Token.objects.get(user=request.user).key
    username = request.user.username
    role = get_role(username)

    return token, username, role


def verify_authorization(role, group):
    return role == group


def is_self(role, group, username, email):
    return verify_authorization(role, group) and username == email


def is_doctor_admin(doctor_username, admin_username):
    doctor_hospital = Doctor.objects.get(user__auth_user__username=doctor_username).hospital
    admin_hospital = CustomAdmin.objects.get(auth_user__username=admin_username).hospital
    return admin_hospital == doctor_hospital


def is_client_doctor(doctor_username, client_username):
    if not get_role(client_username) == "client":
        return False

    doctor = Doctor.objects.get(user__auth_user__username=doctor_username)
    client = Client.objects.get(user__auth_user__username=client_username)
    return client.doctor == doctor


def is_valid_date(date, date_pattern):
    ret_val = True

    try:
        datetime.strptime(date, date_pattern)
    except ValueError:
        ret_val = False

    return ret_val


def get_total_nutrients(meal_history):
    total_calories = round(sum(entry.calories for entry in meal_history), 0)
    total_carbs = round(sum(entry.carbs for entry in meal_history), 0)
    total_fat = round(sum(entry.fat for entry in meal_history), 0)
    total_proteins = round(sum(entry.proteins for entry in meal_history), 0)

    dict = {
        "calories": {"total": total_calories},
        "carbs": {"total": total_carbs},
        "fat": {"total": total_fat},
        "proteins": {"total": total_proteins},
    }

    return dict


def get_client_age(birth_date):
    today = date.today()

    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return age


def get_calories_daily_goal(client):
    sex = client.sex
    weight = client.current_weight
    weight_goal = client.weight_goal
    height = client.height
    age = get_client_age(client.user.birth_date)

    if sex == "male":
        daily_cal_goal = (10 * weight) + (6.25 * height) - (5 * age) + 5

    else:
        daily_cal_goal = (10 * weight) + (6.25 * height) - (5 * age) - 161

    daily_cal_goal *= 1.55

    if weight_goal > weight:
        daily_cal_goal += 500
    else:
        daily_cal_goal -= 500

    return round(daily_cal_goal, 0)


def get_daily_goals(client):
    calories_goal = get_calories_daily_goal(client)
    carbs_goal = round(0.5 * calories_goal / 4, 0)
    fat_goal = round(0.3 * calories_goal / 9, 0)
    protein_goal = round(0.2 * calories_goal / 4, 0)

    return {"calories": calories_goal, "carbs": carbs_goal, "fat": fat_goal, "proteins": protein_goal}


def get_nutrients_info(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = 4 * info_dict["carbs"]["total"]
    total_fat = 9 * info_dict["fat"]["total"]
    total_proteins = 4 * info_dict["proteins"]["total"]
    total_others = total_calories - (total_carbs + total_fat + total_proteins)

    info_dict["carbs"]["ratio"] = round(total_carbs / total_calories * 100, 0)
    info_dict["fat"]["ratio"] = round(total_fat / total_calories * 100, 0)
    info_dict["proteins"]["ratio"] = round(total_proteins / total_calories * 100, 0)
    info_dict["others"] = {"ratio": round(total_others / total_calories * 100, 0)}

    goals = get_daily_goals(client)

    info_dict["carbs"]["goals"] = {"total": round(goals["carbs"], 0), "ratio": 50}
    info_dict["fat"]["goals"] = {"total": round(goals["fat"], 0), "ratio": 30}
    info_dict["proteins"]["goals"] = {"total": round(goals["proteins"], 0), "ratio": 20}
    info_dict["calories"]["goals"] = round(goals["calories"], 0)

    return info_dict


def get_nutrients_left_values(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = info_dict["carbs"]["total"]
    total_fat = info_dict["fat"]["total"]
    total_proteins = info_dict["proteins"]["total"]

    goals = get_daily_goals(client)

    carbs_goal = round(goals["carbs"], 0)
    fat_goal = round(goals["fat"], 0)
    calories_goal = round(goals["calories"], 0)
    proteins_goal = round(goals["proteins"], 0)

    left_carbs = total_carbs - carbs_goal
    left_calories = total_calories - calories_goal
    left_fat = total_fat - fat_goal
    left_proteins = total_proteins - proteins_goal

    info_dict["carbs"]["goal"] = carbs_goal
    info_dict["carbs"]["left"] = left_carbs
    info_dict["fat"]["goal"] = fat_goal
    info_dict["fat"]["left"] = left_fat
    info_dict["proteins"]["goal"] = proteins_goal
    info_dict["proteins"]["left"] = left_proteins
    info_dict["calories"]["goal"] = calories_goal
    info_dict["calories"]["left"] = left_calories

    return info_dict
