"""
Django command to wait for database to be available.
"""

import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Default entry point for the command"""

        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                # If DB is not available, it will raise an exception
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2Error, OperationalError) as e:
                print(e)
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
