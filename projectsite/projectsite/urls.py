from django.contrib import admin
from django.urls import include, path
from fire import views

from fire.views import (
    HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity,
    LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView, 
    IncidentListView, IncidentCreateView, IncidentUpdateView, IncidentDeleteView,
    FireStationListView, FireStationCreateView, FireStationDeleteView, FireStationUpdateView,
    FirefightersList, FirefightersCreateView, FirefightersUpdateView, FirefightersDeleteView,
    FireTruckList, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView,
    WeatherConditionsList, WeatherConditionsCreateView, WeatherConditionsUpdateView, WeatherConditionsDeleteView
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name="dashboard-chart"),
    path('chart/', PieCountbySeverity, name="chart"),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multipleBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('map_incident/', views.MapIncidentView, name='map-incident'),
    
    #locations
    path('location-list', LocationListView.as_view(), name='location-list'),
    path('location-list/add/', LocationCreateView.as_view(), name='location-add'),
    path('location-list/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
    path('location-list/<int:pk>/', LocationUpdateView.as_view(), name='location-update'),
    
    #Incident
    path('incident-list/', IncidentListView.as_view(), name='incident-list'),
    path('incident-list/add/', IncidentCreateView.as_view(), name='incident-add'),
    path('incident-list/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),
    path('incident-list/<int:pk>/', IncidentUpdateView.as_view(), name='incident-update'),

    #FireStation
    path('firestation-list/', FireStationListView.as_view(), name='firestation-list'),
    path('firestation-list/add/', FireStationCreateView.as_view(), name='firestation-add'),
    path('firestation-list/<int:pk>/delete/', FireStationDeleteView.as_view(), name='firestation-delete'),
    path('firestation-list/<int:pk>/', FireStationUpdateView.as_view(), name='firestation-update'),

    #firefighters
    path('firefighters-list/', FirefightersList.as_view(), name='firefighters-list'),
    path('firefighters-list/add/', FirefightersCreateView.as_view(), name='firefighters-add'),
    path('firefighters-list/<pk>/', FirefightersUpdateView.as_view(), name='firefighters-update'),
    path('firefighters-list/<pk>/delete/', FirefightersDeleteView.as_view(), name='firefighters-delete'),

    #fire trucks
    path('firetruck-list/', FireTruckList.as_view(), name='firetruck-list'),
    path('firetruck-list/add', FireTruckCreateView.as_view(), name='firetruck-add'),
    path('firetruck-list/<pk>/', FireTruckUpdateView.as_view(), name='firetruck-update'),
    path('firetruck/<pk>/delete', FireTruckDeleteView.as_view(), name='firetruck-delete'),

    #weather conditions
    path('weather-conditions-list/', WeatherConditionsList.as_view(), name='weather-conditions-list'),
    path('weather-conditions-list/add', WeatherConditionsCreateView.as_view(), name='weather-conditions-add'),
    path('weather-conditions-list/<pk>/', WeatherConditionsUpdateView.as_view(), name='weather-conditions-update'),
    path('weather-conditions/<pk>/delete', WeatherConditionsDeleteView.as_view(), name='weather-conditions-delete'),
]