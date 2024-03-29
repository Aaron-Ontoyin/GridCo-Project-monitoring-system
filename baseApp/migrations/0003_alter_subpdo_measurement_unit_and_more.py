# Generated by Django 4.1.5 on 2023-02-14 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0002_alter_pdo_pdo_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subpdo',
            name='measurement_unit',
            field=models.CharField(choices=[('Cummulative', 'Cummulative'), ('Number', 'Number'), ('Percentage', 'Percentage')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='subpdo',
            name='result_level',
            field=models.CharField(choices=[('Output', 'Output'), ('Outcome', 'Outcome'), ('Goal', 'Goal')], default='', max_length=20),
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('subpdo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseApp.subpdo')),
            ],
        ),
    ]
