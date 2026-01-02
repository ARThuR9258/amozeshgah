from django.urls import path
from . import views
urlpatterns = [
    path('' , views.first_page, name= 'first_page'),
]