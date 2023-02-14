from django.contrib import admin
from django.forms import inlineformset_factory
from .models import CollectionFrequency, CustomUser, Pdo, Project, SubPDO, ProjectYear
from django.db.models import Q

SubPDOFormSet = inlineformset_factory(Pdo, SubPDO,
fields=["result_level", "indicator", "classification", "measurement_unit", "baseline", "baselineyear"]
)
PDOFormset = inlineformset_factory(Project, Pdo, fields=["name", "pdo_num"])

class SubPDOInline(admin.TabularInline):
    fields = fields=["result_level", "indicator", "classification", "measurement_unit", "baseline", "baselineyear"]
    model = SubPDO
    formset = SubPDOFormSet
    extra = 0

class PDOInline(admin.TabularInline):
    model = Pdo
    inlines = [SubPDOInline]
    formset = PDOFormset
    extra = 0


class PDOAdmin(admin.ModelAdmin):
    inlines = [SubPDOInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.pdo = form.instance
            instance.save()
        formset.save_m2m()


class ProjectAdmin(admin.ModelAdmin):
    inlines = [PDOInline]
    exclude = ["creator", "project_years"]

    # Save pdos
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.project = form.instance
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        obj = form.instance
        year_num_list = range(1, obj.duration+1)
        collection_freq = obj.collection_freq
        project_years = ProjectYear.objects.filter(
            Q(year_num__in=year_num_list) & Q(collection_freq=collection_freq)
            )        
        obj.project_years.set(project_years)


admin.site.register(CustomUser)
admin.site.register(Pdo, PDOAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(CollectionFrequency)
