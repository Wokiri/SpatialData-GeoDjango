import uuid

from .utils import HOLDTYPE, LANDUSE
from .manager import CustomUserManager

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=125, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True) # saved automatically when creating an object
    date_updated = models.DateTimeField(auto_now=True) # updated automatically when saving an object
    thumbnail_img  = models.ImageField(
        upload_to='users_logos',
        default='default_avatar.png' # Img in media
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    username = None
    first_name = None
    last_name = None

    objects = CustomUserManager()

    def __str__(self):
        return (f'{self.full_name}')
        

class LandOwner(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    user = models.OneToOneField(User, related_name='land_owner_user', on_delete=models.CASCADE)



class LandUse(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    name = models.CharField(_('type of land use'), unique=True, max_length=125, choices=LANDUSE.choices)
    land_rent = models.FloatField(default=0)
    description = models.CharField(_('decription of landuse type'), max_length=225)

    def __str__(self):
        return self.name



# Parcel model.
class Parcel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel_number = models.CharField(max_length=50, unique=True)
    fr_datum = models.CharField(max_length=50, null=True, blank=True)
    county = models.CharField(max_length=125)
    sub_county = models.CharField(max_length=125)
    owners = models.ManyToManyField(LandOwner, related_name='owner_parcels', verbose_name=_('the people to which the parcel belong'))
    land_use = models.ForeignKey(LandUse, related_name='landuse_parcels', on_delete=models.CASCADE, null=True, blank=True)
    hold_type = models.CharField(max_length=125, choices=HOLDTYPE.choices, default=HOLDTYPE.FREEHOLD)
    
    def __str__(self):
        return self.parcel_number
    


# Zone37SParcel model.
class Zone37SParcel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel = models.OneToOneField(Parcel, related_name='zone_37s_parcel', on_delete=models.CASCADE)
    geom = models.MultiPolygonField(srid=21037)

    def __str__(self):
        return self.parcel.parcel_number


class Zone37NParcel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel = models.OneToOneField(Parcel, related_name='zone_37n_parcel', on_delete=models.CASCADE)
    geom = models.MultiPolygonField(srid=21096)
    

class Zone36SParcel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel = models.OneToOneField(Parcel, related_name='zone_36s_parcel', on_delete=models.CASCADE)
    geom = models.MultiPolygonField(srid=21097)


class Zone36NParcel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel = models.OneToOneField(Parcel, related_name='zone_36n_parcel', on_delete=models.CASCADE)
    geom = models.MultiPolygonField(srid=21036)


# Parcel Beacons model.
class ParcelBeacon(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    parcel = models.ForeignKey(Parcel, related_name='parcel_beacons', on_delete=models.CASCADE)
    station = models.CharField(_('station name'), max_length=20)
    parcel_name = models.CharField(_('parcel name'), max_length=20)
    

class Zone37SBeacon(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    beacon = models.OneToOneField(ParcelBeacon, related_name='zone_37s_beacon', on_delete=models.CASCADE)
    geom = models.PointField(srid=21037)


class Zone37NBeacon(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    beacon = models.OneToOneField(ParcelBeacon, related_name='zone_37n_beacon', on_delete=models.CASCADE)
    geom = models.PointField(srid=21096)
    

class Zone36SBeacon(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    beacon = models.OneToOneField(ParcelBeacon, related_name='zone_36s_beacon', on_delete=models.CASCADE)
    geom = models.PointField(srid=21097)
    

class Zone36NBeacon(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    beacon = models.OneToOneField(ParcelBeacon, related_name='zone_36n_beacon', on_delete=models.CASCADE)
    geom = models.PointField(srid=21036)

