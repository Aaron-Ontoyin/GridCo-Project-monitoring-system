from django.contrib import admin
from .models import Collection, CollectionFrequency, CustomUser, Pdo, Project, ProjectYear, SubPDO

admin.site.register(Collection)
admin.site.register(CollectionFrequency)
admin.site.register(CustomUser)
admin.site.register(Pdo)
admin.site.register(Project)
admin.site.register(ProjectYear)
admin.site.register(SubPDO)
