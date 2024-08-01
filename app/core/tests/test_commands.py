# noqa

"""
Test the custom Django management commands.
"""
# Patch is used to replace objects in a test with mock objects.
from unittest.mock import patch
# OperationalError is used to simulate the error when the database is not available. # noqa
from psycopg2 import OperationalError as Psycopg2Error
# Call_command is used to simulate calling the command.
from django.core.management import call_command
# OperationalError is used to simulate the error when the database is not available. # noqa
from django.db.utils import OperationalError
# BaseCommand is used to create custom Django management commands.
from django.test import SimpleTestCase


# Command.check is provided by the BaseCommand class, which allows us to check if the database is available # noqa
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """
    Test custom Django  commands.
    """

    # Patched_check is a mock object that replaces the check method in the wait_for_db command. # noqa
    def test_wait_for_db_ready(self, patched_check):
        """
        This unit test verifies the behavior of the wait_for_db custom Django management command. # noqa
        It mocks the database check to simulate scenarios where the database is available (patched_check.return_value = True) # noqa
        and checks if the command correctly interacts with the database check mechanism (patched_check.assert_called_once_with(database='default')) # noqa
        """

        # When we call the check method, we want to return True value.
        patched_check.return_value = True

        # Call the wait_for_db command in "core/management/commands/wait_for_db.py" # noqa
        call_command('wait_for_db')

        # Check if the check method was called with the default database
        patched_check.assert_called_once_with(databases=['default'])

    # Mock the time.sleep method
    # Order of the arguments is important. The patched_sleep argument must come before the patched_check argument. # noqa
    @patch('time.sleep')
    def test_wait_for_db_error(self, patched_sleep, patched_check):
        """
        This unit test verifies the behavior of the wait_for_db custom Django management command. # noqa
        It mocks the database check to simulate scenarios where the database is not available (patched_check.return_value = False) # noqa
        and checks if the command correctly interacts with the database check mechanism (patched_check.assert_called_once_with(database='default')) # noqa
        """

        # We want to simulate the database being unavailable for 5 attempts before it becomes available. # noqa
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # Check if the check method was called with the default database
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
