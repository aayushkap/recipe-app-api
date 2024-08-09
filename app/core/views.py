"""
This file contains the views for the core app.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    """Return the status of the API"""
    return Response({'healthy': True})