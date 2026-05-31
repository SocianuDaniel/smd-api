"""
Django command to wait for the database to be available
"""
from django.core.management.base import BaseCommand
import time
from psycopg import OperationalError as PsycopgError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to ait for the database"""

    def handle(self, *args, **options):
        """Entryport for command"""
        self.stdout.write("Waiting for the database ....")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (PsycopgError, OperationalError):
                self.stdout.write("Database unvailable, wainting 1 second ..")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available'))
