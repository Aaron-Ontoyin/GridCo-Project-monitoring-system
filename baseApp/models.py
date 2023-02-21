from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date, timedelta
from itertools import zip_longest

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
    duration = models.PositiveIntegerField()
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
    value = models.DecimalField(max_digits=9, decimal_places=1, default=0, null=True, blank=True)
    subpdo = models.ForeignKey('SubPDO', on_delete=models.CASCADE, related_name='entries')
    index = models.IntegerField()

    def get_year_entry(self):
        year = self.subpdo.pdo.project.project_years.first()
        collection_freq = year.collection_freq
        year_entries = [f"{collection_freq.prefix} {i}" for i in range(1, collection_freq.num_entries+1)]        
        # starts with last entry: idx and year_entry_index are the same but opposite signs
        idx = -1 # Index of current entry in negation
        year_entry_at = collection_freq.num_entries # Index of current entry in positive

        for _  in year_entries: # got through number of year entries times            
            if self.index % year_entry_at == 0: # if the index of self is divisible by current entry psoition
                return year_entries[idx]
            year_entry_at -= 1 # we move 1 step towards the first entry
            idx -= 1 # we move 1 step towards the first entry

    def __str__(self):
        if self.value is None:
            return f"{self.subpdo.pdo}: {self.subpdo} --"
        return f"{self.subpdo.pdo}: {self.subpdo} {self.value}"

    class Meta:
        verbose_name_plural = "Entries"


class YearlyTarget(models.Model):
    subpdo = models.ForeignKey('SubPDO', on_delete=models.CASCADE, related_name='targets')
    yrly_target_index = models.PositiveIntegerField()
    value = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.subpdo} Target for yr {self.yrly_target_index}"


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
    end_target = models.DecimalField(decimal_places=1, max_digits=10, null=True)
    detailed_data_src = models.CharField(max_length=1000, null=True, blank=True)
    comments = models.CharField(max_length=1000, null=True, blank=True)
    subpdo_id = models.CharField(max_length=25, null=True, blank=True)

    def get_perc_comp(self):
        """Calculates and returns percentage of project years completed"""
        
        yearly_targets = list(self.targets.all())        
        entries_into_years = self.get_entries_in_bages()
        
        # Add targets to the entries
        entries_with_targets = []
        idx = 0
        for i in entries_into_years:
            entries_with_targets.append([i] + [yearly_targets[idx]])
            idx += 1
        
        perc_completed_list = []
        for i in entries_with_targets: # Comes with target
            yearly_target_value = i[-1].value
            total = 0
            for entry in i[:-2]: # Gets target off                
                total += entry.value
            per_c = total * 100 / yearly_target_value
            perc_completed_list.append(round(per_c, 2))

    def save(self, *args, **kwargs):
        if not self.pk:            
            iden = f'{self.pdo.pdo_num}'
            pos = self.pdo.subpdos.count() + 1
            self.subpdo_id = f'PDO {iden}.{pos}'

            super().save(*args, **kwargs)

            project = self.pdo.project
            total_entries =  project.collection_freq.num_entries * project.project_years.count()
            entry_index = 1
            yrly_target_index = 1
            for i in range(1, total_entries+1):
                Entry.objects.create(subpdo=self, index=entry_index)
                entry_index += 1
                
                # If we've created all entries for a year, then create a yearly target
                if i % project.project_years.first().collection_freq.num_entries == 0:
                    YearlyTarget.objects.create(subpdo=self, yrly_target_index=yrly_target_index)
                    yrly_target_index += 1
        else:
            super().save(*args, **kwargs)

    def get_entries_in_bages(self):
        """Returns a list of list of entries. Returned entries are grouped according to year"""
        num_per_yr = self.pdo.project.collection_freq.num_entries
        iterator = self.entries.all().iterator()
        chunks = zip_longest(*([iterator] * num_per_yr))

        entries_in_bages = []
        for chunk in chunks:
            chunk_filtered = filter(lambda x: x is not None, chunk)
            chunk_filtered = list(chunk_filtered)
            if chunk_filtered:
                entries_in_bages.append(self.entries.filter(pk__in=[item.pk for item in chunk_filtered]))

        return entries_in_bages
    
    def get_entries_in_bages_with_targets(self):
        """Returns the entry groups from get_entries_in_bages() but paired with their years"""        
        entries_in_year_bages = self.get_entries_in_bages()        
        entries_in_year_bages = list(entries_in_year_bages) # change to a list
        
        # Create a new entries_in_year_bages that has targets
        entries_in_year_bages_with_targets = []
        for i, target in enumerate(self.targets.all()):
            if i < len(entries_in_year_bages):
                entries_bage = entries_in_year_bages[i]
                entries_bage = list(entries_bage) # Change to a list so we can append obj of diff model
                # Append yrly target value to the end of each year entries                
                entries_bage.append(target.value)
                entries_in_year_bages_with_targets.append(entries_bage)
        
        return entries_in_year_bages_with_targets

    def get_entries_in_bages_with_targets_and_atd(self):
        """ Takes entries with targets and adds appropriate target actual to date """
        entries_in_bages_with_targets = self.get_entries_in_bages_with_targets()
        entries_in_bages_with_targets_and_atd = []
        for i in entries_in_bages_with_targets:
            atd = 0
            entries = i[:-1] # remove targets
            if self.classification == "Cummulative":
                for el in entries[::-1]: # So we can loop starting from the last
                    if el.value > 0:
                        atd = el.value
                        break # Take most last non 0 number; remain 0 if none
            else: # Number and percentage are the same
                entries = i[:-1]
                for el in entries:
                    atd += el.value # Add all entries
            entries_in_bages_with_targets_and_atd.append(i + [atd])            
        
        return entries_in_bages_with_targets_and_atd;

    def get_entries_in_bages_with_targets_atd_and_pc(self):
        """ Add percentage completed to each list[grouped into yearly]"""
        entries_in_bages_with_targets_and_atd = self.get_entries_in_bages_with_targets_and_atd()
        entries_in_bages_with_targets_atd_and_pc = []

        # Add the percentage completed to each list
        for i in entries_in_bages_with_targets_and_atd:            
            # Get the target which is the second but last in each list
            target_val = i[-2]
            # Get the sum of all entries in each list. Last two in the list aren't part
            # because they are the yt and atd
            total_entries_val = 0
            if self.classification == "Cummulative":
                # Take the last non 0 entry. If no non 0, then continue to be 0
                entries = i[:-2]
                for el in entries[::-1]: # So we can loop starting from the last
                    if el.value > 0:
                        total_entries_val = el.value
                        break
            else: # Percentage and number works the same
                for entry in i[:-2]:
                    total_entries_val += entry.value
                                
            perc_comp = float(total_entries_val) * 100 / target_val
            perc_comp = round(perc_comp, 1)            
            # Add zero infront if num is less than 10
            if perc_comp < 10.0:
                perc_comp = f"0{perc_comp}"
            entries_in_bages_with_targets_atd_and_pc.append(i + [perc_comp])

        return entries_in_bages_with_targets_atd_and_pc

    def get_all_yrs_with_values(self):
        """ 
        Returns all years with all values in each year in a list 
        including yt, atd, pc all indexed correctly 
        """        
        return self.get_entries_in_bages_with_targets_atd_and_pc()

    def __str__(self):
        return f"{self.subpdo_id}"
