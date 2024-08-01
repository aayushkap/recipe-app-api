"""
Test the custom Django management commands.
"""

from unittest.mock import patch # Patch is used to replace objects in a test with mock objects.
from psycopg2 import OperationalError as Psycopg2Error # Error when the database is not available
from django.core.management import call_command # Simulate Calling the command
from django.db.utils import OperationalError # Error when the database is not available
from django.test import SimpleTestCase # Base class for testing Django applications


@patch('core.management.commands.wait_for_db.Command.check') # Command.check is provided by the BaseCommand class, which allows us to check if the database is available
class CommandTests(SimpleTestCase):
    """
    Test custom Django  commands.
    """

    # Patched_check is a mock object that replaces the check method in the wait_for_db command.
    def test_wait_for_db_ready(self, patched_check):
        """
        This unit test verifies the behavior of the wait_for_db custom Django management command. 
        It mocks the database check to simulate scenarios where the database is available (patched_check.return_value = True) 
        and checks if the command correctly interacts with the database check mechanism (patched_check.assert_called_once_with(database='default'))
        """
        patched_check.return_value = True # When we call the check method, we want to return True value.

        call_command('wait_for_db') # Call the wait_for_db command in "core/management/commands/wait_for_db.py"

        patched_check.assert_called_once_with(databases=['default']) # Check if the check method was called with the default database


    # Mock the time.sleep method
    # Order of the arguments is important. The patched_sleep argument must come before the patched_check argument.
    @patch('time.sleep')
    def test_wait_for_db_error(self, patched_sleep,patched_check):
        """
        This unit test verifies the behavior of the wait_for_db custom Django management command. 
        It mocks the database check to simulate scenarios where the database is not available (patched_check.return_value = False) 
        and checks if the command correctly interacts with the database check mechanism (patched_check.assert_called_once_with(database='default'))
        """

        # We want to simulate the database being unavailable for 5 attempts before it becomes available.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        
        call_command('wait_for_db')

        # Check if the check method was called with the default database
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])

