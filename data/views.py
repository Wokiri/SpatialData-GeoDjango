from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import (
    FormView,
)

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.views.generic import TemplateView
from django.db import transaction

from .forms import (
    ParcelsShapefileForm,
    ParcelsInfoForm,
)

import pandas as pd
import geopandas as gpd

from shapely import wkt


from .models import (
    Parcel,
    Zone37SParcel,
    Zone37NParcel,
    Zone36SParcel,
    Zone36NParcel,
)


class HomePageView(TemplateView):
    template_name = 'data/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title':'HOME',
        })
        return context
        


class ReadParcelsPageView(FormView):
    template_name = 'data/parcels_write.html'
    form_class = ParcelsShapefileForm
    success_url = reverse_lazy('data:home_page')

    # from ContextMixin via FormMixin
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['parcels_upload_form'] = data.get('form')
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            shapefile_data = form.cleaned_data.get('shapefile')
            shapefile_attributes = shapefile_data.get('shapefile_data')
            crs = shapefile_data.get('crs')

            if shapefile_attributes and crs:
                shapefile_data_df = pd.DataFrame(data=shapefile_attributes)
                shapefile_data_df['geometry'] = shapefile_data_df['geometry'].apply(wkt.loads)

                shapefile_gdf = gpd.GeoDataFrame(shapefile_data_df, geometry='geometry')
                shapefile_gdf.set_crs(crs, allow_override=True, inplace=True)

                if 'preview' in request.POST:
                    context = self.get_context_data(**kwargs)
                    context.update({
                        'parcels_geojson':shapefile_gdf.to_crs("EPSG:4326").to_json(),
                    })
                    request.session.update({
                        'shapefile_json':shapefile_attributes,
                        'crs':crs,
                    })

                    return self.render_to_response(context)

        return self.form_invalid(form)


class WriteParcelsPageView(FormView):
    template_name = 'data/parcels_write.html'
    form_class = ParcelsInfoForm
    success_url = reverse_lazy('data:read_parcels_page')

    def get_initial(self, request):
        """Return the initial data to use for forms on this view."""
        return {
            'parcels':request.session.get('shapefile_json')
        }

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.get_initial(request))
        if form.is_valid():
            shapefile_data_df = pd.DataFrame(data=form.cleaned_data.get('parcels'))
            shapefile_data_df['geometry'] = shapefile_data_df['geometry'].apply(wkt.loads)
            shapefile_gdf = gpd.GeoDataFrame(shapefile_data_df, geometry='geometry')
            shapefile_gdf.set_crs(request.session.get('crs'), allow_override=True, inplace=True)
            shapefile_gdf.set_index('parcel_num', inplace=True)
            
            with transaction.atomic():
                for parcel_number in shapefile_gdf.index.values.tolist():
                    geom = GEOSGeometry(shapefile_gdf.at[parcel_number, 'geometry'].wkt, srid=request.session.get('crs'))
                    
                    if isinstance(geom, Polygon):
                        geom = MultiPolygon(geom)

                    parcel,_ = Parcel.objects.update_or_create(
                        parcel_number=parcel_number,
                        defaults={
                            'fr_datum': shapefile_gdf.at[parcel_number, 'fr_datum'],
                            'county': shapefile_gdf.at[parcel_number, 'county'],
                            'sub_county': shapefile_gdf.at[parcel_number, 'sub_county'],
                        },
                    )

                    if request.session.get('crs') == 21037:
                        Zone37SParcel.objects.update_or_create(
                            parcel=parcel,
                            defaults={'geom':geom}
                        )
                    elif request.session.get('crs') == 21096:
                        Zone37NParcel.objects.update_or_create(
                            parcel=parcel,
                            defaults={'geom':geom}
                        )
                    elif request.session.get('crs') == 21097:
                        Zone36SParcel.objects.update_or_create(
                            parcel=parcel,
                            defaults={'geom':geom}
                        )
                    elif request.session.get('crs') == 21036:
                        Zone36NParcel.objects.update_or_create(
                            parcel=parcel,
                            defaults={'geom':geom}
                        )
                  
            del(request.session['shapefile_json'])
            del(request.session['crs'])
            
            return self.form_valid(form)

        return self.form_invalid(form)
