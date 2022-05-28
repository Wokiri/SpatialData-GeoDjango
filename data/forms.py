
from django.contrib.gis import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from data.models import (
    Parcel,
    LandUse
)

from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)

from .utils import validate_shapefile, COUNTIES, PROJECTION, LANDUSE, HOLDTYPE

from PIL import Image
from django.contrib.auth import get_user_model
User = get_user_model()

password_widget = forms.PasswordInput(
    attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }
)

SAVE_SHAPEFILE = [
    ('Yes', 'Save'),
    ('Discard', 'Discard'),
]


class ParcelsShapefileForm(forms.Form):
    shapefile = forms.FileField(
        label='Zipped parcels shapefile',
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




class ControlsShapefileForm(forms.Form):
    shapefile = forms.FileField(
        label='Zipped controls shapefile',
        widget=forms.ClearableFileInput(
            attrs={
                'accept': '.zip',
                'class': "form-control"
            }
        )
    )

    def clean_shapefile(self):
        shapefile = self.cleaned_data['shapefile']
        result_object = validate_shapefile(file=shapefile, geom_type='Point')

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






class ApproveShapefileForm(forms.Form):
    approve = forms.ChoiceField(
        label=False,
        widget=forms.Select(
            attrs={
                'class': "form-select",
            },
        ),
        choices=SAVE_SHAPEFILE,
    )


class UserSignupModelForm(UserCreationForm):

    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'email address'
            }
        )
    )
    full_name = forms.CharField(
        label=_('Full name'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'full name'
            }
        )
    )
    thumbnail_img = forms.ImageField(
        label=_('Optional image thumbnail'),
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': False,
                'accept': 'image/*',
                'class': "form-control"
            }
        )
    )
    password1 = forms.CharField(label=_('Password'), widget=password_widget)
    password2 = forms.CharField(
        label=_('Password confirmation'), widget=password_widget)

    def clean_thumbnail_img(self):
        file = self.cleaned_data['thumbnail_img']

        if file is not None:
            prof_pic = Image.open(file)

            if prof_pic.size[0] != prof_pic.size[1]:
                raise ValidationError("Please choose a square image")

            if file.size > 1000000:
                raise ValidationError(
                    "Submitted image must not exceed 1mb in size")

        return file

    class Meta:
        model = User
        fields = ('email', 'full_name', 'thumbnail_img',)



class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'email address',
                'autofocus': True
            }
        )
    )
    password = forms.CharField(label=_("Password"), widget=password_widget)




Category =(
    ("", "Make a Selection"),
    ("parcels", "Parcels"),
    ("beacons", "Beacons"),
)

class ExploreForm(forms.Form):

    category = forms.ChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': "form-select",
            },
        ),
        choices=Category,
    )

    search_value = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'search value'
            }
        )
    )