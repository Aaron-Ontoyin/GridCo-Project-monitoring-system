from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date, timedelta


RESULT_LEVEL_CHOICES = [
    ('Output','Output'),
    ('Outcome','Outcome'),
    ('Goal', 'Goal')
    ]
MEASUREMENT_UNIT_CHOICES = [
    ('Number', 'Number'),
    ('Percentage', 'Percentage')
]
CLASSIFICATION_CHOICES = [
    ('Cummulative','Cummulative'),
    ('Number','Number'),
    ('Percentage','Percentage')
]


class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=7)
    is_admin = models.BooleanField(default=False)    
    def __str__(self):
        return self.username


class CollectionFrequency(models.Model):
    name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=15)
    num_entries = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Collection Frequencies"

    def __str__(self):  
        return self.name


class ProjectYear(models.Model):
    year_num = models.IntegerField()    
    # Shares same collection freq with projects that are related to it
    collection_freq = models.ForeignKey(CollectionFrequency,
    on_delete=models.SET_NULL, related_name='project_year', blank=True, null=True)

    def __str__(self):
        return f"Project year {self.year_num} :{self.collection_freq.name}"


class Project(models.Model):
    creator = models.ForeignKey(CustomUser, related_name='creator', 
    null=True, blank=True, on_delete=models.SET_NULL)
    project_years = models.ManyToManyField(ProjectYear, related_name="projects", blank=True)
    name = models.CharField(max_length=250)
    duration = models.IntegerField()
    genPDO = models.CharField(max_length=1000)
    reporters = models.ManyToManyField(CustomUser, related_name='editing_projects', blank=True)
    # Shares same collection freq with project years that are related to it
    collection_freq = models.ForeignKey(CollectionFrequency, on_delete=models.SET_NULL,
    null=True, related_name='projects', blank=True)
    created = models.DateField(auto_now_add=True)

    def get_year_entries(self):
        freq = self.collection_freq
        entries = [f"{freq.prefix} {position}" for position in range(1, freq.num_entries+1)]
        return entries

    def perc_completed(self):
        return 15

    def all_years_fill(self):
        return (self.collection_freq.value + 3) * self.duration
    
    def __str__(self):
        return self.name

class Pdo(models.Model):
    """
    This is the indicator. Under each indicator we have PDO but named SubPDO
    """
    name = models.CharField(max_length=250)
    pdo_num = models.IntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pdos")

    def __str__(self):
        return f"{self.project}: {self.name}"

    class Meta:        
        ordering = ['project']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'pdo_num'], name='unique_pdo_num'
            )
        ]
        verbose_name_plural = "Indicators"


class Entry(models.Model):
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    subpdo = models.ForeignKey('SubPDO', on_delete=models.CASCADE, related_name='entries')


class SubPDO(models.Model):
    """
    Supposed to be PDO rather. Because every PDO is under an Indicator
    """
    result_level = models.CharField(
        max_length=20,
        choices = RESULT_LEVEL_CHOICES,
        default = ""
    )
    classification = models.CharField(
        max_length=20,
        choices = CLASSIFICATION_CHOICES,
        default = ""
    )
    measurement_unit = models.CharField(
        max_length=20,
        choices = MEASUREMENT_UNIT_CHOICES,
        default = ""
    )
    pdo = models.ForeignKey(Pdo, related_name='subpdos', on_delete=models.CASCADE)

    baseline = models.IntegerField(default=1)
    baselineyear = models.IntegerField()
    actual_to_date = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    end_target = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    perc_complete = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    detailed_data_src = models.CharField(max_length=1000, null=True, blank=True)
    comments = models.CharField(max_length=1000, null=True, blank=True)
    subpdo_id = models.CharField(max_length=25, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            iden = f'{self.pdo.pdo_num}'
            pos = self.pdo.subpdos.count() + 1
            self.subpdo_id = f'PDO {iden}.{pos}'

            super().save(*args, **kwargs)

            project = self.pdo.project
            total_entries =  project.collection_freq.num_entries * project.project_years.count()            
            for _ in range(total_entries):
                Entry.objects.create(subpdo=self)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subpdo_id}"
