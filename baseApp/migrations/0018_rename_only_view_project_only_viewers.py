# Generated by Django 4.1.5 on 2023-03-23 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0017_alter_project_creator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='only_view',
            new_name='only_viewers',
        ),
    ]
