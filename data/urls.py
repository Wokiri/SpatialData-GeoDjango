from django.urls import path

from .views import (
    HomePageView,
    ReadParcelsPageView,
    WriteParcelsPageView,
)

app_name = 'data'


urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path('read-parcels/', ReadParcelsPageView.as_view(), name='read_parcels_page'),
    path('write-parcels/', WriteParcelsPageView.as_view(), name='write_parcels_page'),
]