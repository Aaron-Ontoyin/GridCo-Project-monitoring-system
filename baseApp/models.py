from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date, timedelta


RESULT_LEVEL_CHOICES = [('1',1), ('2',2)]
INDICATOR_CHOICES = [('1',1), ('2',2)]
CLASSIFICATION_CHOICES = [('1',1), ('2',2)]
MEASUREMENT_UNIT_CHOICES = [('1',1), ('2',2)]
MONTH_CHOICES = [(1,1), (2,2)]
    

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
    years = models.ManyToManyField(ProjectYear, related_name="projects", blank=True)
    name = models.CharField(max_length=250)
    duration = models.IntegerField()
    genPDO = models.CharField(max_length=1000)
    reporters = models.ManyToManyField(CustomUser, related_name='editing_projects', blank=True)
    # Shares same collection freq with project years that are related to it
    collection_freq = models.ForeignKey(CollectionFrequency, on_delete=models.SET_NULL,
    null=True, related_name='projects', blank=True)
    created = models.DateField(auto_now_add=True)

    def perc_completed(self):
        return 15

    def all_years_fill(self):
        return (self.collection_freq.value + 3) * self.duration
    
    def __str__(self):
        return self.name

class Pdo(models.Model):
    name = models.CharField(max_length=250)
    pdo_id = models.IntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pdos")


class SubPDO(models.Model):
    result_level = models.CharField(
        max_length=20,
        choices = RESULT_LEVEL_CHOICES,
        default = ""
    )
    indicator = models.CharField(
        max_length=20,
        choices = INDICATOR_CHOICES,
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
    baselineyear = models.DateField()
    year_fills = [] # values corresponds to fields in the project years
    actual_to_date = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    end_target = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    perc_complete = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    detailed_data_src = models.CharField(max_length=1000, null=True, blank=True)
    comments = models.CharField(max_length=1000, null=True, blank=True)

    def subpdo_id(self):
        iden = f'{self.pdo.pdo_id}.'
        pos = self.pdo.subpdo.count() + 1
        val = f'PDO {iden}{pos}'
        return val

    def __str__(self):
        return self.subpdo_id()

    def baseline_year(self):
        return self.baseline_year_field.date.strftime('%Y')

