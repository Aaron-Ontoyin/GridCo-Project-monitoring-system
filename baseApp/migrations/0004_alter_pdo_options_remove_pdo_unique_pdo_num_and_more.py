# Generated by Django 4.1.5 on 2023-02-15 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0003_alter_subpdo_measurement_unit_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pdo',
            options={'verbose_name_plural': 'Indicators'},
        ),
        migrations.RemoveConstraint(
            model_name='pdo',
            name='unique_pdo_num',
        ),
        migrations.RemoveField(
            model_name='subpdo',
            name='indicator',
        ),
        migrations.AlterField(
            model_name='entry',
            name='subpdo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='baseApp.subpdo'),
        ),
    ]
