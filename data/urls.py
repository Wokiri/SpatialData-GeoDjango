from django.urls import path

from .views import (
    HomeView,
    
    ReadParcelsView,
    WritenParcelsView,

    ReadControlsView,
    WritenControlsView,

    SignUpView,
    UserProfileView,
)

app_name = 'data'


urlpatterns = [
    path('', HomeView.as_view(), name='home_page'),
    
    path('read-parcels/', ReadParcelsView.as_view(), name='read_parcels_page'),
    path('writen-parcels/', WritenParcelsView.as_view(), name='writen_parcels_page'),

    path('read-controls/', ReadControlsView.as_view(), name='read_controls_page'),
    path('writen-controls/', WritenControlsView.as_view(), name='writen_controls_page'),

    path('sign-up/', SignUpView.as_view(), name='user_signup_page'),
    path('profile/', UserProfileView.as_view(), name='user_profile_page'),
]