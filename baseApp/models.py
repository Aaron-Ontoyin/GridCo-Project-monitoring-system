from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date, timedelta


RESULT_LEVEL_CHOICES = [('1',1), ('2',2)]
INDICATOR_CHOICES = [('1',1), ('2',2)]
CLASSIFICATION_CHOICES = [('1',1), ('2',2)]
MEASUREMENT_UNIT_CHOICES = [('1',1), ('2',2)]
MONTH_CHOICES = [(1,1), (2,2)]


class CollectionFrequency(models.Model):
    name = models.CharField(max_length=150)
    prefix = models.CharField(max_length=50)
    value = models.IntegerField()


class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=7)
    is_admin = models.BooleanField(default=False)
    created_projects = models.ForeignKey('Project', related_name='creator', 
    null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.username


class Collection(models.Model):
    name = models.CharField(max_length=50)
    start_month = models.CharField(max_length=25)


class ProjectYear(models.Model):
    year_id = models.IntegerField(unique=True)
    start_date = models.DateField()
    str_start_date = models.CharField(max_length=150, null=True, blank=True)
    actual_to_date = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    target = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    perc_complete = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    collections = models.ForeignKey(Collection, related_name='project_year',  on_delete=models.CASCADE)
    created = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.str_start_date = self.start_date.strftime('%b %Y')

            # Create collections with respect to self.project.collection_freq
            num_collections = self.project.collection_freq.value
            name = self.project.collection_freq.prefix
            sdate = self.start_date.strftime('%b %Y')
            for _ in range(num_collections):                
                edate = self.start_date.date + timedelta(days=12 * 60 / num_collections)
                edate = edate.strftime('%b %Y')
                self.collections.add(Collections.objects.create(
                    name=f'{name} {num_collections}',                    
                    span=f'{sdate} - {edate}',                    
                    ))
                
            return super().save(*args, **kwargs)


class Project(models.Model):
    name = models.CharField(max_length=250)
    duration = models.IntegerField(default=1)
    genPDO = models.TextField(null=True, blank=True)
    pdos = models.ForeignKey('Pdo', related_name='project',
    default=None, on_delete=models.CASCADE)
    project_years = models.ForeignKey(ProjectYear, 
    default=None, on_delete=models.CASCADE, null=True, blank=True)
    collection_freq = models.ForeignKey(CollectionFrequency,
    default=None, on_delete=models.CASCADE)    
    reporters = models.ManyToManyField(CustomUser, related_name='editing_projects', blank=True)

    def perc_completed(self):
        pass

    def total_year_fills(self):
        return (self.collection_freq.value + 3) * self.duration

    def create_years(self):
        for _ in range(self.duration):
            py = ProjectYear.objects.create(
                year_id = self.project_years.count() + 1,
                start_date = self.start_date
                )
            self.project_years.add(py)

    def save(self, *args, **kwargs):
        create_years = True if not self.pk else False
        super().save(*args, *kwargs)
        # Create duration number of project years
        if create_years:
            self.create_years            

class Pdo(models.Model):
    name = models.CharField(max_length=250)
    pdo_id = models.IntegerField(unique=True)
    subpdos = models.ForeignKey('SubPDO', related_name='pdo', on_delete=models.CASCADE)


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
    baseline = models.IntegerField(default=1)
    baseline_year_field = models.DateField(auto_now_add=True)
    year_fills = [] # values corresponds to fields in the project years
    actual_to_date = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    end_target = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    perc_complete = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    detailed_data_src = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def subpdo_id():
        val = None
        if self.pdo:
            iden = f'{self.pdo.pdo_id}.'
            pos = self.pdo.subpdo.count() + 1
            val = f'{iden}{pos}'
        return val
            

    def baseline_year(self):
        return self.baseline_year_field.date.strftime('%Y')

