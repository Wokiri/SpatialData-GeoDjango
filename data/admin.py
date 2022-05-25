from django.contrib import admin
from .models import (
    User,
    Parcel,
    LandUse,
    LandOwner,
    Zone37SParcel,
    Zone37NParcel,
    Zone36SParcel,
    Zone36NParcel,
    ParcelBeacon,
    Zone37SBeacon,
    Zone37NBeacon,
    Zone36SBeacon,
    Zone36NBeacon,
)

# Register your models here.
admin.site.register(User)

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'parcel_number',
        'fr_datum',
        'county',
        'sub_county',
        'land_use',
        'hold_type',
        'date_created',
    ]
admin.site.register(LandUse)
admin.site.register(LandOwner)
admin.site.register(Zone37SParcel)
admin.site.register(Zone37NParcel)
admin.site.register(Zone36SParcel)
admin.site.register(Zone36NParcel)
admin.site.register(ParcelBeacon)
admin.site.register(Zone37SBeacon)
admin.site.register(Zone37NBeacon)
admin.site.register(Zone36SBeacon)
admin.site.register(Zone36NBeacon)