from django.contrib.gis.utils import LayerMapping
from .models import Parcel
from pathlib import Path

data_shp = Path.home().joinpath('Desktop/gis_data/parcels.shp')

# Auto-generated `LayerMapping` dictionary for Parcel model
parcel_mapping = {
    'parcel_number': 'parcel_num',
    'fr_datum': 'fr_datum',
    'county': 'county',
    'sub_county': 'sub_county',
    'geom': 'MULTIPOLYGON',
}


def run():
    lm = LayerMapping(
        Parcel, data_shp, parcel_mapping, source_srs=21037, transform=False
    )

    lm.save(verbose=True)