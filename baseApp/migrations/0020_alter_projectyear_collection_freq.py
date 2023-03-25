# Generated by Django 4.1.5 on 2023-03-25 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0019_alter_project_only_viewers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectyear',
            name='collection_freq',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_year', to='baseApp.collectionfrequency'),
        ),
    ]
