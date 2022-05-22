
from django.contrib.gis import forms
from django.core.exceptions import ValidationError

from data.models import (
    Parcel,
    LandUse
)

from .utils import validate_shapefile

from .utils import COUNTIES, PROJECTION, LANDUSE, HOLDTYPE


class ParcelsShapefileForm(forms.Form):
    shapefile = forms.FileField(
        label='Zipped parcel shapefile',
        widget=forms.ClearableFileInput(
            attrs={
                'accept': '.zip',
                'class': "form-control"
            }
        )
    )

    def clean_shapefile(self):
        shapefile = self.cleaned_data['shapefile']
        result_object = validate_shapefile(file=shapefile, geom_type='Polygon')

        is_data_valid = result_object.get('is_data_valid', False)
        message = result_object.get('message', 'Unknown error occured, please try again')
        code = result_object.get('code', 'unknown_error')
        shapefile_data = result_object.get('shapefile_data', {})
        crs = result_object.get('crs')
        
        if not is_data_valid:
            raise ValidationError(message, code=code)

        return {
            'shapefile_data':shapefile_data,
            'crs':crs,
        }



class ParcelsInfoForm(forms.Form):
    parcels = forms.JSONField()