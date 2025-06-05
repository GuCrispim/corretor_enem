from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('redacao/', include('app_redacao.urls')),
    path('', include('app_redacao.urls')), 
]