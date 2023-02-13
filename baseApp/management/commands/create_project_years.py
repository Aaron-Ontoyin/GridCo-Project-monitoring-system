from django.core.management.base import BaseCommand
from baseApp.models import CollectionFrequency, ProjectYear

class Command(BaseCommand):
    help = 'Create project years'
    global lower
    global upper

    def add_arguments(self, parser):
        parser.add_argument('from', type=int, help='Lower year number to create')
        parser.add_argument('to', type=int, help='Upper year number to create')
    
    def handle(self, *args, **options):
        lower = options['from']
        upper = options['to']
        
        while ProjectYear.objects.filter(year_num=lower):
            lower += 1

        for i in range(lower, upper+1):
            for freq in CollectionFrequency.objects.all():                
                py = ProjectYear.objects.create(year_num=i, collection_freq=freq)

        self.stdout.write(self.style.SUCCESS(f'Project years in range {lower} to {upper} created successfully'))
