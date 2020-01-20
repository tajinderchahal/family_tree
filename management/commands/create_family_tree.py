from django.core.management import BaseCommand

family_tree_data = [

]

class Command(BaseCommand):
    help = "This will create a data for family tree"

    def handle(self, *args, **options):
