# Generated by Django 4.1.5 on 2023-03-23 18:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0015_alter_subpdo_end_target'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subpdo',
            options={'verbose_name_plural': 'Project Development objectives'},
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='project',
            name='only_view',
            field=models.ManyToManyField(blank=True, related_name='view_only', to=settings.AUTH_USER_MODEL),
        ),
    ]