import json

from django.db.models import Q

from django.core.serializers import serialize

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import (
    FormView,
)

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon, Point, MultiPoint
from django.db import transaction
from django.contrib import messages

from django.views.generic import (
    TemplateView,
    ListView,
    DetailView
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)

from django.contrib.auth.views import (
    LoginView,
)


from .forms import (
    ParcelsShapefileForm,
    ControlsShapefileForm,
    ApproveShapefileForm,
    UserSignupModelForm,
    UserLoginForm,
    ExploreForm,
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
    ParcelBeacon,
    Zone37SBeacon,
    Zone37NBeacon,
    Zone36SBeacon,
    Zone36NBeacon,
    LandOwner,
)

def get_all_controls_geojson():

    if Zone37SBeacon.objects.exists() and ParcelBeacon.objects.exists():
        controls_with_geom = json.loads(serialize('geojson', Zone37SBeacon.objects.select_related('beacon')))
        controls_with_attrs = json.loads(serialize('json', ParcelBeacon.objects.all()))
        for control_geom in controls_with_geom['features']:
            control_geom_id = control_geom['properties']['beacon']
            for control_attr in controls_with_attrs:
                control_attr_id = control_attr['pk']

                if control_geom_id == control_attr_id:
                    control_geom['properties'].update(control_attr['fields'])
        
        controls_geojson = json.dumps(controls_with_geom)
        return controls_geojson


def get_all_parcels_geojson():

    if Zone37SParcel.objects.exists() and Parcel.objects.exists():
        parcels_with_geom = json.loads(serialize('geojson', Zone37SParcel.objects.select_related('parcel')))
        parcels_with_attrs = json.loads(serialize('json', Parcel.objects.all()))
        for parcel_geom in parcels_with_geom['features']:
            parcel_geom_id = parcel_geom['properties']['parcel']
            for parcel_attr in parcels_with_attrs:
                parcel_attr_id = parcel_attr['pk']

                if parcel_geom_id == parcel_attr_id:
                    parcel_geom['properties'].update(parcel_attr['fields'])
        
        parcels_geojson = json.dumps(parcels_with_geom)
        return parcels_geojson


class HomeView(TemplateView):
    template_name = 'data/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title':'HOME',
        })
        return context


class ReadParcelsView(FormView):
    template_name = 'data/parcels_write.html'
    form_class = ParcelsShapefileForm
    success_url = reverse_lazy('data:home_page')

    # from ContextMixin via FormMixin
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['parcels_upload_form'] = data.get('form')
        data['existing_parcels_geojson'] = get_all_parcels_geojson()
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
                shapefile_gdf.set_index('parcel_num', inplace=True)
                
                
                with transaction.atomic():

                    written_parcels = []

                    for parcel_number in shapefile_gdf.index.values.tolist():

                        try:
                            geom = GEOSGeometry(shapefile_gdf.at[parcel_number, 'geometry'].wkt, srid=request.session.get('crs'))
                        except Exception:
                            continue
                        
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

                        if crs == 21037:
                            geom_parcel,_ = Zone37SParcel.objects.update_or_create(
                                parcel=parcel,
                                defaults={'geom':geom}
                            )
                            written_parcels.append(str(geom_parcel.id))
                        elif crs == 21096:
                            geom_parcel,_ = Zone37NParcel.objects.update_or_create(
                                parcel=parcel,
                                defaults={'geom':geom}
                            )
                            written_parcels.append(str(geom_parcel.id))
                        elif crs == 21097:
                            geom_parcel,_ = Zone36SParcel.objects.update_or_create(
                                parcel=parcel,
                                defaults={'geom':geom}
                            )
                            written_parcels.append(str(geom_parcel.id))
                        elif crs == 21036:
                            geom_parcel,_ = Zone36NParcel.objects.update_or_create(
                                parcel=parcel,
                                defaults={'geom':geom}
                            )
                            written_parcels.append(str(geom_parcel.id))

                    request.session.update({'created_parcels':written_parcels})
                    messages.info(request, 'Parcels saved successfully')
                    return redirect('data:writen_parcels_page')
                            

        return self.form_invalid(form)


class WritenParcelsView(FormView):
    
    template_name = 'data/written_parcels.html'
    form_class = ApproveShapefileForm
    success_url = reverse_lazy('data:home_page')
    

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['approve_parcels_form'] = self.get_form()
        return data
        
    def get(self, request, *args, **kwargs):

        if not request.session.get('created_parcels'):
            return redirect('data:home_page')

        context = self.get_context_data()
        zone_parcels_data = []

        created_parcels = Zone37SParcel.objects.filter(Q(id__in=request.session.get('created_parcels')))
        if created_parcels:
            for parcel in created_parcels:
                parcel_obj = Parcel.objects.filter(Q(zone_37s_parcel=parcel))
                zone_parcel_data = json.loads(serialize('json', parcel_obj))
                zone_parcels_data.append(zone_parcel_data[0])

        if not created_parcels:
            created_parcels = Zone37NParcel.objects.filter(Q(id__in=request.session.get('created_parcels')))
            if created_parcels:
                for parcel in created_parcels:
                    parcel_obj = Parcel.objects.filter(Q(zone_37n_parcel=parcel))
                    zone_parcel_data = json.loads(serialize('json', parcel_obj))
                    zone_parcels_data.append(zone_parcel_data[0])

        if not created_parcels:
            created_parcels = Zone36SParcel.objects.filter(Q(id__in=request.session.get('created_parcels')))
            if created_parcels:
                for parcel in created_parcels:
                    parcel_obj = Parcel.objects.filter(Q(zone_36s_parcel=parcel))
                    zone_parcel_data = json.loads(serialize('json', parcel_obj))
                    zone_parcels_data.append(zone_parcel_data[0])

        if not created_parcels:
            created_parcels = Zone36NParcel.objects.filter(Q(id__in=request.session.get('created_parcels')))
            if created_parcels:
                for parcel in created_parcels:
                    parcel_obj = Parcel.objects.filter(Q(zone_36n_parcel=parcel))
                    zone_parcel_data = json.loads(serialize('json', parcel_obj))
                    zone_parcels_data.append(zone_parcel_data[0])


        if created_parcels and zone_parcels_data:
            parcels_data = json.loads(serialize('geojson', created_parcels))
            for parcel in parcels_data['features']:
                parcel_id = parcel['properties']['parcel']
                for zone_parcel in zone_parcels_data:
                    zone_parcel_id = zone_parcel['pk']

                    if parcel_id == zone_parcel_id:
                        parcel['properties'].update(zone_parcel['fields'])


            context.update({
                'parcels_geojson':json.dumps(parcels_data)
            })
            del request.session['created_parcels']
            
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            value = form.cleaned_data.get('approve')
            if value == 'Discard':
                pass
            
            return self.form_valid(form)
            
        return self.form_invalid(form)

    


class ReadControlsView(FormView):
    template_name = 'data/controls_write.html'
    form_class = ControlsShapefileForm
    success_url = reverse_lazy('data:home_page')

    # from ContextMixin via FormMixin
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['controls_upload_form'] = data.get('form')
        data['existing_controls_geojson'] = get_all_controls_geojson()
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
                shapefile_gdf.set_index('name', inplace=True)
                
                with transaction.atomic():

                    written_controls = []

                    for name in shapefile_gdf.index.values.tolist():
                        
                        try:
                            geom = GEOSGeometry(shapefile_gdf.at[name, 'geometry'].wkt, srid=request.session.get('crs'))
                        except Exception:
                            continue

                        if isinstance(geom, Point):
                            geom = MultiPoint(geom)

                        control,_ = ParcelBeacon.objects.update_or_create(
                            name=name,
                            defaults={
                                'name': name,
                            }
                        )

                        if crs == 21037:
                            geom_control, created = Zone37SBeacon.objects.update_or_create(
                                beacon=control,
                                defaults={'geom':geom}
                            )
                            if created:
                                intersecting_parcels = Zone37SParcel.objects.select_related('parcel').filter(geom__intersects=geom)
                                for parcel in intersecting_parcels:
                                    parcel_obj = Parcel.objects.get(parcel_number=parcel)
                                    control.parcel.add(parcel_obj)

                            written_controls.append(str(geom_control.id))
                        elif crs == 21096:
                            geom_control, created = Zone37NBeacon.objects.update_or_create(
                                beacon=control,
                                defaults={'geom':geom}
                            )
                            if created:
                                intersecting_parcels = Zone37NParcel.objects.select_related('parcel').filter(geom__intersects=geom)
                                for parcel in intersecting_parcels:
                                    parcel_obj = Parcel.objects.get(parcel_number=parcel)
                                    control.parcel.add(parcel_obj)

                            written_controls.append(str(geom_control.id))
                        elif crs == 21097:
                            geom_control, created = Zone36SBeacon.objects.update_or_create(
                                beacon=control,
                                defaults={'geom':geom}
                            )
                            if created:
                                intersecting_parcels = Zone36SParcel.objects.select_related('parcel').filter(geom__intersects=geom)
                                for parcel in intersecting_parcels:
                                    parcel_obj = Parcel.objects.get(parcel_number=parcel)
                                    control.parcel.add(parcel_obj)

                            written_controls.append(str(geom_control.id))
                        elif crs == 21036:
                            geom_control, created = Zone36NBeacon.objects.update_or_create(
                                beacon=control,
                                defaults={'geom':geom}
                            )
                            if created:
                                intersecting_parcels = Zone36NParcel.objects.select_related('parcel').filter(geom__intersects=geom)
                                for parcel in intersecting_parcels:
                                    parcel_obj = Parcel.objects.get(parcel_number=parcel)
                                    control.parcel.add(parcel_obj)

                            written_controls.append(str(geom_control.id))

                    request.session.update({'created_controls':written_controls})
                    messages.info(request, 'Controls saved successfully')
                    return redirect('data:writen_controls_page')
                            

        return self.form_invalid(form)


class WritenControlsView(FormView):
    
    template_name = 'data/written_controls.html'
    form_class = ApproveShapefileForm
    success_url = reverse_lazy('data:home_page')
    

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['approve_controls_form'] = self.get_form()
        return data
        
    def get(self, request, *args, **kwargs):

        if not request.session.get('created_controls'):
            return redirect('data:home_page')

        context = self.get_context_data()
        zone_controls_data = []

        created_controls = Zone37SBeacon.objects.filter(Q(id__in=request.session.get('created_controls')))
        if created_controls:
            for control in created_controls:
                control_obj = ParcelBeacon.objects.filter(Q(zone_37s_beacon=control))
                zone_control_data = json.loads(serialize('json', control_obj))
                zone_controls_data.append(zone_control_data[0])

        if not created_controls:
            created_controls = Zone37NBeacon.objects.filter(Q(id__in=request.session.get('created_controls')))
            if created_controls:
                for control in created_controls:
                    control_obj = ParcelBeacon.objects.filter(Q(zone_37n_beacon=control))
                    zone_control_data = json.loads(serialize('json', control_obj))
                    zone_controls_data.append(zone_control_data[0])

        if not created_controls:
            created_controls = Zone36SBeacon.objects.filter(Q(id__in=request.session.get('created_controls')))
            if created_controls:
                for control in created_controls:
                    control_obj = ParcelBeacon.objects.filter(Q(zone_36s_beacon=control))
                    zone_control_data = json.loads(serialize('json', control_obj))
                    zone_controls_data.append(zone_control_data[0])

        if not created_controls:
            created_controls = Zone36NBeacon.objects.filter(Q(id__in=request.session.get('created_controls')))
            if created_controls:
                for control in created_controls:
                    control_obj = ParcelBeacon.objects.filter(Q(zone_36n_beacon=control))
                    zone_control_data = json.loads(serialize('json', control_obj))
                    zone_controls_data.append(zone_control_data[0])


        if created_controls and zone_controls_data:
            controls_data = json.loads(serialize('geojson', created_controls))
            for control in controls_data['features']:
                control_id = control['properties']['beacon']
                for zone_beacon in zone_controls_data:
                    zone_beacon_id = zone_beacon['pk']

                    if zone_beacon_id == control_id:
                        control['properties'].update(zone_beacon['fields'])


            context.update({
                'controls_geojson':json.dumps(controls_data)
            })
            del request.session['created_controls']
            
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            value = form.cleaned_data.get('approve')
            if value == 'Discard':
                pass
            
            return self.form_valid(form)
            
        return self.form_invalid(form)


class SignUpView(FormView):
    template_name = 'data/sign_up.html'

    form_class = UserSignupModelForm
    success_url = reverse_lazy('data:user_profile_page')

    def get_context_data(self, **kwargs):
        data = super(SignUpView, self).get_context_data(**kwargs)
        data['signup_form'] = data.get('form')
        return data

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('data:user_profile_page')

        context = self.get_context_data(**kwargs)
        context.update({
            'page_title':f'User Signup'
        })
        return self.render_to_response(context)
        
    
    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            new_user = form.save()
            if new_user:
                return self.form_valid(form)
        
        else:
            return self.form_invalid(form)




class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'data/user_profile.html'
    
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'page_title':f'{request.user.full_name} Profile'
        })
        return self.render_to_response(context)
        

class LoginUserView(LoginView):
    authentication_form = UserLoginForm


class OwnersListView(ListView):
    queryset = LandOwner.objects.all()
    context_object_name = 'ownners_list'
    template_name = 'data/ownners_list.html'

    def get_context_data(self, ** kwargs):
        context = super().get_context_data( ** kwargs)
        context.update({
            'page_title':'Parcels Owners',
            'num_owners':self.queryset.count(),
        })
        return context
       
       


class SearchView(TemplateView, FormView, ListView):
    template_name = 'data/search.html'
    form_class = ExploreForm
    context_object_name = 'search_results'
    paginate_by = 10


    def get_context_data(self, request, **kwargs):
        data = super().get_context_data(**kwargs)
        data['full_page_url'] = request.get_full_path()
        data['search_form'] = data.get('form')
        data['search_value'] = request.GET.get('search_value')
        data['category_value'] = request.GET.get('category')
        return data

    def get_queryset(self, request, **kwargs):
        if 'category' in request.GET and 'search_value' in request.GET:
            search_value = request.GET.get('search_value')
            category = request.GET.get('category')
            
            if category == 'parcels':
                queryset = Parcel.objects.filter(
                    Q(parcel_number__icontains=search_value) |
                    Q(fr_datum__icontains=search_value) |
                    Q(county__icontains=search_value) |
                    Q(sub_county__icontains=search_value) |
                    Q(hold_type__icontains=search_value)
                )
            elif category == 'beacons':
                queryset = ParcelBeacon.objects.filter(name__icontains=search_value)
            return queryset

        else:
            return []
            

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        context = self.get_context_data(request, **kwargs)
        return self.render_to_response(context)
        


class ParcelDetailView(DetailView):
    template_name = 'data/parcel_detail.html' # Also the default template
    model = Parcel
    context_object_name = 'parcel'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.get_object():
            parcels_with_geom = json.loads(serialize('geojson', Zone37SParcel.objects.select_related('parcel').filter(parcel=self.get_object())))
            parcels_with_attrs = json.loads(serialize('json', Parcel.objects.filter(id=self.get_object().id)))
            
            for parcel_geom in parcels_with_geom['features']:
                parcel_geom_id = parcel_geom['properties']['parcel']
                for parcel_attr in parcels_with_attrs:
                    parcel_attr_id = parcel_attr['pk']

                    if parcel_geom_id == parcel_attr_id:
                        parcel_geom['properties'].update(parcel_attr['fields'])
            
            parcels_geojson = json.dumps(parcels_with_geom)
        
        
        context.update({
            'page_title':self.get_object().parcel_number,
            "parcel_geojson":parcels_geojson
        })
        return self.render_to_response(context)

