# Generated by Django 4.1.5 on 2023-02-12 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0009_remove_projectyear_project_project_project_years'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdo',
            name='pdo_id',
            field=models.IntegerField(),
        ),
    ]
