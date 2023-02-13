from django.contrib import admin
from django.forms import inlineformset_factory
from .models import CollectionFrequency, CustomUser, Pdo, Project, SubPDO, ProjectYear
from django.db.models import Q

SubPDOFormSet = inlineformset_factory(Pdo, SubPDO,
fields=["result_level", "indicator", "classification", "measurement_unit", "baseline", "baselineyear"]
)
PDOFormset = inlineformset_factory(Project, Pdo, fields=["name", "pdo_id"])

class SubPDOInline(admin.TabularInline):
    model = SubPDO
    formset = SubPDOFormSet
    extra = 1

class PDOInline(admin.TabularInline):
    model = Pdo
    inlines = [SubPDOInline]
    formset = PDOFormset
    extra = 1


class PDOAdmin(admin.ModelAdmin):
    inlines = [SubPDOInline]
    exclude = ["creator"]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.pdo = form.instance
            instance.save()
        formset.save_m2m()


class ProjectAdmin(admin.ModelAdmin):
    inlines = [PDOInline]    

    # Save pdos
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.project = form.instance
            instance.save()
        formset.save_m2m()


    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.save()
            obj.creator = request.user
            year_num_list = range(1, obj.duration+1)
            collection_freq = obj.collection_freq
            project_years = ProjectYear.objects.filter(
                Q(year_num__in=year_num_list) & Q(collection_freq=collection_freq)
                )
            obj.years.set(project_years)
        
        obj.save()
            
        # Super.save_model() is currnetly trwoing error about receiving 6 args instead of 5
        # super().save_model(self, request, obj, form, change)


admin.site.register(CollectionFrequency)
admin.site.register(CustomUser)
admin.site.register(Pdo, PDOAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SubPDO)
admin.site.register(ProjectYear)
