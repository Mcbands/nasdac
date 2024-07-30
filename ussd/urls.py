from django.urls import path
from .views import ussd_view

urlpatterns = [
    path('', ussd_view, name='ussd_view'),  # Route the root URL of this app to the ussd_view function
]
