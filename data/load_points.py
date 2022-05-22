from django.contrib.gis.utils import LayerMapping
from .models import ParcelBeacon
from pathlib import Path

data_shp = Path.home().joinpath('Desktop/gis_data/points.shp')

# Auto-generated `LayerMapping` dictionary for ParcelBeacon model
parcelbeacon_mapping = {
    'parcel_name': 'parcel_num',
    'geom': 'POINT',
}



def run():
    lm = LayerMapping(
        ParcelBeacon, data_shp, parcelbeacon_mapping, source_srs=21037, transform=False
    )

    lm.save(verbose=True)