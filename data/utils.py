import zipfile, tempfile
from pathlib import Path

from django.contrib.gis.gdal import (
    DataSource, OGRGeometry, SpatialReference, CoordTransform
)

from django.utils.translation import gettext_lazy as _


from django.contrib.gis.db import models

class COUNTIES(models.TextChoices):
    MOMBASA = 'Mombasa', _('Mombasa')
    NAIROBI = 'Nairobi', _('Nairobi')
    KISUMU = 'Kisumu', _('Kisumu')
    MACHAKOS = 'Machakos', _('Machakos')


class HOLDTYPE(models.TextChoices):
    FREEHOLD = 'FREEHOLD', _('Free Hold')
    LEASEHOLD = 'LEASEHOLD', _('Lease Hold')
    COMMUNITY = 'COMMUNITY', _('Community Land')


class LANDUSE(models.TextChoices):
    SUBSISTENCE_AGRICULTURE = 'SUBSISTENCE-AGRICULTURE', _('Subsistence Agricultural Use')
    COMMERCIAL_AGRICULTURE = 'COMMERCIAL-AGRICULTURE', _('Commercial Agricultural Use')
    COMMERCIAL = 'COMMERCIAL', _('Commercial Use')


class PROJECTION(models.TextChoices):
    ZONE37S = 'EPSG:21037', _('Zone 37 South')
    ZONE37N = 'EPSG:21097', _('Zone 37 North')
    ZONE36S = 'EPSG:21036', _('Zone 36 South')
    ZONE36N = 'EPSG:21096', _('Zone 36 North')



def validate_shapefile(*, file, geom_type):

    response_data = {}
    
    required_columns = [
        'parcel_num',
        'fr_datum',
        'county',
        'sub_county',
        'hold_type',
        'land_use',
    ]
    

    expected_shapes = []
    if geom_type == 'Polygon':
        expected_shapes = ['Polygon', 'MultiPolygon', 'Polygon25D', 'MultiPolygon25D']
    elif geom_type == 'Point':
        expected_shapes = ['Point', 'MultiPoint', 'Point25D', 'MultiPoint25D']

    if not expected_shapes:
        response_data.update({
            'is_data_valid': False,
            'message': 'Specify parcel geometry',
            'code': 'bad_file',
        })
        return response_data
    

    with tempfile.TemporaryDirectory() as temporary_dir:
        with zipfile.ZipFile(file, 'r') as shp_zip_obj:
            error = shp_zip_obj.testzip()
            
            if error:
                response_data.update({
                    'is_data_valid': False,
                    'message': 'There is a bad file in the zip',
                    'code': 'bad_file',
                })
                return response_data
                

            file_exts = [Path(file).suffix for file in shp_zip_obj.namelist()]
            
            if not '.shp' in file_exts:
                response_data.update({
                    'is_data_valid': False,
                    'message': 'There is no .shp extension in the zip',
                    'code': 'bad_file',
                })
                return response_data

            if not '.shx' in file_exts:
                response_data.update({
                    'is_data_valid': False,
                    'message': 'There is no .shx extension in the zip',
                    'code': 'bad_file',
                })
                return response_data

            if not '.dbf' in file_exts:
                response_data.update({
                    'is_data_valid': False,
                    'message': 'There is no .dbf extension in the zip',
                    'code': 'bad_file',
                })
                return response_data

            if not '.prj' in file_exts:
                response_data.update({
                    'is_data_valid': False,
                    'message': 'There is no .prj extension in the zip',
                    'code': 'bad_file',
                })
                return response_data

            shp_zip_obj.extractall(path=temporary_dir)

        shp_to_read = ''
        for child in Path(temporary_dir).iterdir():
            if child.suffix == '.shp':
                shp_to_read = child
                
        dataSource = DataSource(shp_to_read)
        
        if not dataSource:
            response_data.update({
                'is_data_valid': False,
                'message': 'Could not open %s' %(Path(shp_to_read).name),
                'code': 'bad_file',
            })
            return response_data
            
        if dataSource.layer_count < 1:
            response_data.update({
                'is_data_valid': False,
                'message': 'There is no layer in the submitted data!',
                'code': 'bad_file',
            })
            return response_data
        
        layer = dataSource[0]

        if layer.num_feat < 1:
            response_data.update({
                'is_data_valid': False,
                'message': 'There\'s no feature in the submitted data!',
                'code': 'bad_file',
            })
            return response_data
            
        if not layer.geom_type.name in expected_shapes:
            response_data.update({
                'is_data_valid': False,
                'message': f'Submited data is not a {geom_type}',
                'code': 'bad_file',
            })
            return response_data
            
        for field in required_columns:
            if field not in layer.fields:
                response_data.update({
                    'is_data_valid': False,
                    'message': f"'{field}' column is expected in the shapefile",
                    'code': 'bad_file',
                })
                return response_data
                

        shapefile_data = {
            'parcel_num': layer.get_fields('parcel_num'),
            'fr_datum': layer.get_fields('fr_datum'),
            'county': layer.get_fields('county'),
            'sub_county': layer.get_fields('sub_county'),
            'hold_type': layer.get_fields('hold_type'),
            'land_use': layer.get_fields('land_use'),
            'geometry': [feat_geom.wkt for feat_geom in layer.get_geoms()]
        }
        
        response_data.update({
            'is_data_valid': True,
            'crs':int(layer.srs.srid),
            'shapefile_data': shapefile_data
        })

        return response_data



