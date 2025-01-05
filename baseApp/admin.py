from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.forms import inlineformset_factory
from django.forms import BaseInlineFormSet
from .models import CollectionFrequency, CustomUser, Pdo, Project, SubPDO, ProjectYear, Entry, YearlyTarget
from django.db.models import Q


class CustomUserChangeForm(UserChangeForm):    

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        exclude = None


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm


class DeletableModelInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['DELETE'].widget.attrs['class'] = 'delete-checkbox'

    def save(self, commit=True):
        # Call the superclass's save() method first
        result = super().save(commit=commit)

        # Delete objects that have been marked for deletion
        for form in self.deleted_forms:
            form.instance.delete()

        return result

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        for form in self.forms:
            if form.cleaned_data.get('DELETE') and not form.instance.pk:
                self.errors.append('Cannot delete a new object.')


SubPDOFormSet = inlineformset_factory(Pdo, SubPDO, formset=DeletableModelInlineFormset, can_delete=True,
exclude = ["subpdo_id", "detailed_data_src", "comments"]
)
PDOFormset = inlineformset_factory(Project, Pdo, fields=["name", "pdo_num"],
formset=DeletableModelInlineFormset, can_delete=True
)

class YearlyTargetInline(admin.TabularInline):
    model = YearlyTarget
    
    # def has_add_permission(self, request, obj):
    #     return False

    def get_extra(self, request, obj=None, **kwargs):
        extra = super().get_extra(request, obj, **kwargs)        
        if obj:
            # Get the number of forms that are already associated with the parent object.
            existing_forms = self.get_queryset(request).filter(subpdo=obj).count()
            # Calculate the number of extra forms needed to reach the desired total.            
            extra = obj.pdo.project.duration - existing_forms            
        return extra


class SubPDOInline(admin.TabularInline):
    exclude = ["subpdo_id", "detailed_data_src", "comments"]
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

    def has_add_permission(self, request):
        return False

    # Save subpdos
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        count = 1
        for instance in instances:
            instance.pdo = form.instance            
            instance.save()
        formset.save_m2m()


class SubPDOAdmin(admin.ModelAdmin):
    inlines = [YearlyTargetInline]

    def has_add_permission(self, request):
        return False

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        obj = form.instance
        # Create Entries
        if not obj.entries.all():
            for i in range(1, obj.get_num_entries()+1):        
                Entry.objects.create(subpdo=obj, index=i)

    
class ProjectAdmin(admin.ModelAdmin):
    inlines = [PDOInline]
    exclude = ["creator", "project_years", "collection_freq"]

    # Save indicators
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


class CollectionFrequencyAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # creat project 100 years
        for i in range(1, 101):
            ProjectYear.objects.create(year_num=i, collection_freq=obj)


admin.site.site_header = "GridCo Project Monitoring System Admin"
admin.site.site_title = "GridCo Project Monitoring System Admin"
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CollectionFrequency, CollectionFrequencyAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Pdo, PDOAdmin)
admin.site.register(SubPDO, SubPDOAdmin)
admin.site.register(Entry)
