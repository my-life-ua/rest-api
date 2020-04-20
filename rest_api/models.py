from django.contrib.auth.models import User
from django.db import models


class CustomAdmin(models.Model):
    auth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    hospital = models.CharField(max_length=100)


class CustomUser(models.Model):
    auth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    photo = models.TextField(null=True, blank=True)
    birth_date = models.DateField()


class Doctor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    hospital = models.CharField(max_length=100)


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    sex = models.CharField(max_length=30)
    fitbit_access_token = models.CharField(max_length=300, null=True, blank=True)
    fitbit_refresh_token = models.CharField(max_length=300, null=True, blank=True)
    height = models.FloatField()
    current_weight = models.FloatField()
    weight_goal = models.FloatField()
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)


class Ingredient(models.Model):
    calories = models.FloatField(default=0)
    proteins = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    name = models.CharField(max_length=30)


class Meal(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=30)
    # https://docs.djangoproject.com/en/3.0/topics/db/models/#extra-fields-on-many-to-many-relationships
    ingredients = models.ManyToManyField(Ingredient, through="Quantity")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    calories = models.FloatField(default=0)
    proteins = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)


class Quantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.FloatField()


class MealHistory(models.Model):
    day = models.DateField()
    type_of_meal = models.CharField(max_length=25)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    number_of_servings = models.FloatField()
    calories = models.FloatField(default=0)
    proteins = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    target_body_area = models.CharField(max_length=25)
    difficulty = models.IntegerField()


class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_reps = models.IntegerField()
    time = models.FloatField()


class Workout(models.Model):
    workout_sets = models.ManyToManyField(Set)
    rest_time = models.DurationField()  # https://docs.djangoproject.com/en/3.0/ref/models/fields/#durationfield
    difficulty = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
