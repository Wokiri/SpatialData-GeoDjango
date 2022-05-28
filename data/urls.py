from django.urls import path

from .views import (
    HomeView,
    
    ReadParcelsView,
    WritenParcelsView,

    ReadControlsView,
    WritenControlsView,

    SignUpView,
    UserProfileView,

    OwnersListView,

    SearchView,

    ParcelDetailView,
    # ControlDetailView,

)

app_name = 'data'


urlpatterns = [
    path('', HomeView.as_view(), name='home_page'),
    
    path('parcels/', ReadParcelsView.as_view(), name='read_parcels_page'),
    path('writen-parcels/', WritenParcelsView.as_view(), name='writen_parcels_page'),

    path('controls/', ReadControlsView.as_view(), name='read_controls_page'),
    path('writen-controls/', WritenControlsView.as_view(), name='writen_controls_page'),

    path('parcel-owners/', OwnersListView.as_view(), name='owners_page'),

    path('sign-up/', SignUpView.as_view(), name='user_signup_page'),
    path('profile/', UserProfileView.as_view(), name='user_profile_page'),

    path('search', SearchView.as_view(), name='search_page'),

    path('parcel/<str:pk>/', ParcelDetailView.as_view(), name='parcel_page')
    # path('control/<int:pk>/', ControlDetailView.as_view(), name='control_page'),
]