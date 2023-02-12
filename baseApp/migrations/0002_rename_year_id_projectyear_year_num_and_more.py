# Generated by Django 4.1.5 on 2023-02-12 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectyear',
            old_name='year_id',
            new_name='year_num',
        ),
        migrations.AddField(
            model_name='projectyear',
            name='collection_freq',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='baseApp.collectionfrequency'),
        ),
        migrations.AlterField(
            model_name='project',
            name='genPDO',
            field=models.CharField(max_length=1000),
        ),
        migrations.RemoveField(
            model_name='projectyear',
            name='project',
        ),
        migrations.AlterField(
            model_name='subpdo',
            name='comments',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='subpdo',
            name='detailed_data_src',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='projectyear',
            name='project',
            field=models.ManyToManyField(related_name='project_years', to='baseApp.project'),
        ),
    ]
