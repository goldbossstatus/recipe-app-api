import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    '''
    Django command to pause execution until database is available
    '''
    # we are going to put the function in a handle function
    # a handle function is what is ran whenever we run this managament Command
    def handle(self, *args, **options):
        '''
        Check and see if the db is available, and once it's available,
        we are going to clean and exit
        '''
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database not ready, wait for 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('The Database is ready!'))
