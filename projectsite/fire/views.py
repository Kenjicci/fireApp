#querying
from typing import Any
from django.db.models.query import QuerySet
from django.db.models.query import Q
#views
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation,  Firefighters, FireTruck, WeatherConditions
from fire.forms import LocationsForm, IncidentForm, FireStationForm, FirefightersForm, FireTruckForm, WeatherConditionsForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Locations, Incident, FireStation

#charts
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from geopy.distance import geodesic


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = ''' 
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # constructs the dictionary with severity_level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}
    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    
    result = {month: 0 for month in range(1, 13) }

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    #counting the number of incidents per month 
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    #if you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
        7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec' 
    }

    result_with_month_names = {month_names[int(month)]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)
 
def MultilineIncidentTop3Country(request): 
 
    query = ''' 
        SELECT  
        fl.country, 
        strftime('%m', fi.date_time) AS month, 
        COUNT(fi.id) AS incident_count 
    FROM  
        fire_incident fi 
    JOIN  
        fire_locations fl ON fi.location_id = fl.id 
    WHERE  
        fl.country IN ( 
            SELECT  
                fl_top.country 
            FROM  
                fire_incident fi_top 
            JOIN  
                fire_locations fl_top ON fi_top.location_id = fl_top.id 
            WHERE  
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now') 
            GROUP BY  
                fl_top.country 
            ORDER BY  
                COUNT(fi_top.id) DESC 
            LIMIT 3 
        ) 
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now') 
    GROUP BY  
        fl.country, month 
    ORDER BY  
        fl.country, month; 
    ''' 
 
    with connection.cursor() as cursor: 
        cursor.execute(query) 
        rows = cursor.fetchall() 
 
    # Initialize a dictionary to store the result 
    result = {} 
 
    # Initialize a set of months from January to December 
    months = set(str(i).zfill(2) for i in range(1, 13)) 
 
    # Loop through the query results 
    for row in rows: 
        country = row[0] 
        month = row[1] 
        total_incidents = row[2] 
 
        # If the country is not in the result dictionary, initialize it with all months set to zero 
        if country not in result: 
            result[country] = {month: 0 for month in months} 
 
        # Update the incident count for the corresponding month 
        result[country][month] = total_incidents 
 
    # Ensure there are always 3 countries in the result 
    while len(result) < 3: 
        # Placeholder name for missing countries 
        missing_country = f"Country {len(result) + 1}" 
        result[missing_country] = {month: 0 for month in months} 
 
    for country in result: 
        result[country] = dict(sorted(result[country].items())) 
 
    return JsonResponse(result) 


 
def multipleBarbySeverity(request): 
    query = ''' 
    SELECT  
        fi.severity_level, 
        strftime('%m', fi.date_time) AS month, 
        COUNT(fi.id) AS incident_count 
    FROM  
        fire_incident fi 
    GROUP BY fi.severity_level, month 
    ''' 
 
    with connection.cursor() as cursor: 
        cursor.execute(query) 
        rows = cursor.fetchall() 
 
    result = {} 
    months = set(str(i).zfill(2) for i in range(1, 13)) 
 
    for row in rows: 
        level = str(row[0])  # Ensure the severity level is a string 
        month = row[1] 
        total_incidents = row[2] 
 
        if level not in result: 
            result[level] = {month: 0 for month in months} 
 
        result[level][month] = total_incidents 
 
    # Sort months within each severity level 
    for level in result: 
        result[level] = dict(sorted(result[level].items())) 
 
    return JsonResponse(result) 

def map_station(request):
     fireStations = FireStation.objects.values('name', 'latitude', 'longitude') 
 
     for fs in fireStations: 
         fs['latitude'] = float(fs['latitude']) 
         fs['longitude'] = float(fs['longitude']) 

     fireStations_list = list(fireStations) 
 
     context = { 
         'fireStations': fireStations_list, 
     } 
 
     return render(request, 'map_station.html', context)
 
def MapIncidentView(request):
    incidents = Incident.objects.select_related('location').all().values(
        'location__latitude', 'location__longitude', 'severity_level', 'location__name', 'location__city'
    )
    cities = Locations.objects.values('city').distinct()
    for incident in incidents:
        incident['location__latitude'] = float(incident['location__latitude'])
        incident['location__longitude'] = float(incident['location__longitude'])
    incidents_list = list(incidents)
    return render(request, 'map_incident.html', {
        'incidents': incidents_list,
        'cities': cities,
    })


# LOCATION

class LocationListView(ListView):
    model = Locations
    context_object_name = 'location'
    template_name = "Locations/location_list.html"
    paginate_by = 5
    
    def get_queryset(self, *args, **kwargs):
        qs = super(LocationListView, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(Q(name__icontains=query) |
                           Q(latitude__icontains=query) |
                           Q(longitude__icontains=query) |
                           Q(address__icontains=query) |
                           Q(city__icontains=query) |
                           Q(country__icontains=query))
        return qs
    
class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'Locations/location_add.html'
    success_url = reverse_lazy('location-list')
    
    def form_valid(self, form):
        location_name = form.instance.name
        messages.success(self.request, f'{location_name} has been added')
        
        return super().form_valid(form)
    
class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'Locations/location_del.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        messages.success(self.request, 'Deleted successfully. ')
        return super().form_valid(form)
    
    
class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'Locations/location_edit.html'
    success_url = reverse_lazy('location-list')
    
    def form_valid(self, form):
        location_name = form.instance.name
        messages.success(self.request, f'{location_name} has been updated')

        return super().form_valid(form)
    
    
# INCIDENT
class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = "Incident/incident_list.html"
    paginate_by = 5


    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get("q")
            qs = qs.filter(
                Q(Location__location__icontains=query) |
                Q(date_time__icontains=query) |
                Q(severity_level__icontains=query) |
                Q(description__icontains=query)
            )
        
        return qs
    
class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'Incident/incident_add.html'
    success_url = reverse_lazy('incident-list')
    
    def form_valid(self, form):
        incident_location_name = form.instance.location.name
        messages.success(self.request, f'{incident_location_name} has been added')
        
        return super().form_valid(form)
    
    
class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'Incident/incident_del.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        messages.success(self.request, 'Delete successfully. ')
        return super().form_valid(form)
    
    
class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'Incident/incident_edit.html'
    success_url = reverse_lazy('incident-list')
    
    def form_valid(self, form):
        incident_location_name = form.instance.location.name
        messages.success(self.request, f'{incident_location_name} has been updated')

        return super().form_valid(form)

    
# FIRE STATION

class FireStationListView(ListView):
    model = FireStation
    context_object_name = 'firestations' 
    template_name = 'Fire Station/firestation_list.html' 
    paginate_by = 5

    def get_queryset(self):
        queryset = FireStation.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
            
class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'Fire Station/firestation_add.html'
    success_url = reverse_lazy('firestation-list')
    
    def form_valid(self, form):
        firestation_name = form.instance.name
        messages.success(self.request, f'{firestation_name} has been added')
        
        return super().form_valid(form)
    
    
class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'Fire Station/firestation_del.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        messages.success(self.request, 'Delete successfully. ')
        return super().form_valid(form)
    
    
class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'Fire Station/firestation_edit.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        firestation_name = form.instance.name
        messages.success(self.request, f'{firestation_name} has been updated')

        return super().form_valid(form)
    
            
        
        
        
        
        
        
        
        
        
        
        
    
#FIREFIGHTERS
class FirefightersList(ListView):
     model =  Firefighters
     context_object_name = 'firefighters' 
     template_name = 'Firefighters/firefighters_list.html' 
     paginate_by = 5
     
     def get_queryset(self, *args, **kwargs):
         qs = super(FirefightersList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None: 
             query = self.request.GET.get('q') 
             qs = qs.filter(Q(name__icontains=query) |
                            Q(rank__icontains=query) |
                            Q(experience_level__icontains=query) |
                            Q(station__icontains=query))
         return qs
     
class FirefightersCreateView(CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'Firefighters/firefighters_add.html'
    success_url = reverse_lazy('firefighters-list')
    
    def form_valid(self, form):
        firefighter_name = form.instance.name
        messages.success(self.request, f'{firefighter_name} has been added. ')
        
        return super().form_valid(form)
    
class FirefightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'Firefighters/firefighters_edit.html'
    success_url = reverse_lazy('firefighters-list')
    
    def form_valid(self, form):
        firefighters_name = form.instance.name
        messages.success(self.request, f'{firefighters_name}\'s details have been updated. ')

        return super().form_valid(form)
    
class FirefightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'Firefighters/firefighters_del.html'
    success_url = reverse_lazy('firefighters-list')

    def form_valid(self, form):
        messages.success(self.request, 'Deleted successfully. ')
        return super().form_valid(form)
    
#FIRE TRUCKS
class FireTruckList(ListView):
     model =  FireTruck
     context_object_name = 'firetruck' 
     template_name = 'Firetruck/firetruck_list.html' 
     paginate_by = 5
     
     def get_queryset(self, *args, **kwargs):
         qs = super(FireTruckList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None: 
             query = self.request.GET.get('q') 
             qs = qs.filter(Q(truck_number__icontains=query) |
                            Q(model__icontains=query) |
                            Q(capacity=query) |
                            Q(station=query))
         return qs

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'Firetruck/firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')
    
    def form_valid(self, form):
        firetruck_number = form.instance.truck_number
        firetruck_station = form.instance.station
        messages.success(self.request, f'{firetruck_number} has been listed to {firetruck_station}. ')
        
        return super().form_valid(form)
    
class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'Firetruck/firetruck_edit.html'
    success_url = reverse_lazy('firetruck-list')
    
    def form_valid(self, form):
        firetruck_number = form.instance.truck_number
        messages.success(self.request, f'Truck Number {firetruck_number} has been updated. ')

        return super().form_valid(form)
    
class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'Firetruck/firetruck_del.html'
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        messages.success(self.request, 'Deleted successfully. ')
        return super().form_valid(form)
    
#Weather Condition
class WeatherConditionsList(ListView):
     model =  WeatherConditions
     context_object_name = 'weather_conditions' 
     template_name = 'WeatherCondition/weather_conditions_list.html' 
     paginate_by = 5
     
     def get_queryset(self, *args, **kwargs):
         qs = super(WeatherConditionsList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None: 
             query = self.request.GET.get('q') 
             qs = qs.filter(Q(incident__icontains=query) |
                            Q(temperature__icontains=query) |
                            Q(humidity=query) |
                            Q(wind_speed=query) |
                            Q(weather_description=query))
         return qs

class WeatherConditionsCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'WeatherConditions/weather_conditions_add.html'
    success_url = reverse_lazy('weather-conditions-list')

    def post(self, request, *args, **kwargs):
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        wind_speed = request.POST.get('wind_speed')

        errors = []
        for field_name, value in [('temperature', temperature), ('humidity', humidity), ('wind_speed', wind_speed)]:
            try:
                if float(value) <= 0:
                    errors.append(f"{field_name.capitalize()} must be greater than 0.")
            except (ValueError, TypeError):
                errors.append(f"{field_name.capitalize()} must be a valid number.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return self.form_invalid(self.get_form())

        return super().post(request, *args, **kwargs)

    
    def form_valid(self, form):
        incident = form.instance.incident
        messages.success(self.request, f'Weather condition for incident {incident} has been added.')
        
        return super().form_valid(form)
    
class WeatherConditionsUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'WeatherCondition/weather_conditions_edit.html'
    success_url = reverse_lazy('weather-conditions-list')

    def post(self, request, *args, **kwargs):
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        wind_speed = request.POST.get('wind_speed')

        errors = []
        for field_name, value in [('temperature', temperature), ('humidity', humidity), ('wind_speed', wind_speed)]:
            try:
                if float(value) <= 0:
                    errors.append(f"{field_name.capitalize()} must be greater than 0.")
            except (ValueError, TypeError):
                errors.append(f"{field_name.capitalize()} must be a valid number.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return self.form_invalid(self.get_form())

        return super().post(request, *args, **kwargs)

    
    def form_valid(self, form):
        incident = form.instance.incident
        messages.success(self.request, f'Weather condition for incident {incident} has been updated.')
        
        return super().form_valid(form)
    
class WeatherConditionsDeleteView(DeleteView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'WeatherCondition/weather_conditions_edit.html'
    success_url = reverse_lazy('weather-conditions-list')

    def form_valid(self, form):
        messages.success(self.request, 'Deleted successfully. ')
        return super().form_valid(form)
    