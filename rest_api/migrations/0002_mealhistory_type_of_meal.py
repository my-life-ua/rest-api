# Generated by Django 3.0.4 on 2020-03-17 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealhistory',
            name='type_of_meal',
            field=models.CharField(default='Lunch', max_length=25),
            preserve_default=False,
        ),
    ]
