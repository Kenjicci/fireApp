from django.contrib import admin
from django.urls import path

from fire.views import (
    HomePageView, 
    ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity,
    FirefightersList
)

from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name="dashboard-chart"),
    path('firefighters-list/', FirefightersList.as_view(), name='firefighters-list'),
    path('chart/', PieCountbySeverity, name="chart"),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('map_incident/', views.MapIncidentView, name='map-incident'),
]