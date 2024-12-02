from django.contrib import admin
from django.urls import include, path

from fire.views import (
    HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity,
    LocationList, LocationCreateView, LocationUpdateView, LocationDeleteView,
    FirefightersList, FirefightersCreateView, FirefightersUpdateView, FirefightersDeleteView,
)
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name="dashboard-chart"),
    path('chart/', PieCountbySeverity, name="chart"),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('map_incident/', views.MapIncidentView, name='map-incident'),
    
    path('location_list', LocationList.as_view(), name='location-list'),
    path('location_list/add/', LocationCreateView.as_view(), name='location-add'),
    path('location-list/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
    path('location-list/<int:pk>/', LocationUpdateView.as_view(), name='location-update'),

    #firefighters
    path('firefighters-list/', FirefightersList.as_view(), name='firefighters-list'),
    path('firefighters-list/add/', FirefightersCreateView.as_view(), name='firefighters-add'),
    path('firefighters-list/<pk>/', FirefightersUpdateView.as_view(), name='firefighters-update'),
    path('firefighters-list/<pk>/delete', FirefightersDeleteView.as_view(), name='firefighters-delete'),

]