"""
    Sample test file
"""

from django.test import SimpleTestCase

from app import calc

from rest_framework.test import APIClient

class CalcTest(SimpleTestCase):
    """
        Sample test class
    """

    def test_add(self):
        """
            Sample test method
        """
        self.assertEqual(calc.add(1, 2), 3)

    def test_subtract(self):
        """
            Sample test method
        """
        self.assertEqual(calc.subtract(5, 11), 6)

    def test_multiply(self):
        """
            Sample test method
        """
        self.assertEqual(calc.multiply(3, 7), 21)

    def test_divide(self):
        """
            Sample test method
        """
        self.assertEqual(calc.divide(10, 2), 5)