"""
Test health check API
"""

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'healthy': True})
