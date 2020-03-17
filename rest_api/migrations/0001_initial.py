# Generated by Django 3.0.4 on 2020-03-17 12:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomAdmin',
            fields=[
                ('auth_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('hospital', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('auth_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('photo', models.TextField(blank=True, null=True)),
                ('birth_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('target_body_area', models.CharField(max_length=25)),
                ('difficulty', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calories', models.FloatField()),
                ('proteins', models.FloatField()),
                ('fat', models.FloatField()),
                ('carbs', models.FloatField()),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_reps', models.IntegerField()),
                ('time', models.FloatField()),
                ('exercise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rest_api.Exercise')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='rest_api.CustomUser')),
                ('height', models.FloatField()),
                ('weight_goal', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='rest_api.CustomUser')),
                ('hospital', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MealCatalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('type_of_meal', models.CharField(max_length=30)),
                ('ingredients', models.ManyToManyField(to='rest_api.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('number_of_servings', models.FloatField()),
                ('type_of_meal', models.CharField(max_length=30)),
                ('ingredients', models.ManyToManyField(to='rest_api.Ingredient')),
                ('meal_from_catalog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rest_api.MealCatalog')),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rest_time', models.DurationField()),
                ('difficulty', models.IntegerField()),
                ('workout_sets', models.ManyToManyField(to='rest_api.Set')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.Client')),
            ],
        ),
        migrations.CreateModel(
            name='MealHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('meals', models.ManyToManyField(to='rest_api.Meal')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.Client')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rest_api.Doctor'),
        ),
    ]
