from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ussd/', include('ussd.urls')),  # Direct requests starting with /ussd/ to your app's urls.py
]
