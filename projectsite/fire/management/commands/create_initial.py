from django.core.management.base import BaseCommand
from faker import Faker
import random
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        self.populate_locations(20)
        self.populate_fire_stations(20)
        self.populate_incidents(20)
        self.populate_firefighters(20)
        self.populate_fire_trucks(20)
        self.populate_weather_conditions(20)

    def populate_locations(self, count):
        fake = Faker()
        for _ in range(count):
            Locations.objects.create(
                name=fake.city(),  # Use city names for realistic location names
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
                city=fake.city(),
                country=fake.country(),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} Locations created successfully.'))


    def populate_fire_stations(self, count):
        fake = Faker()
        for _ in range(count):
            # Generate realistic fire station names
            station_name = f"{random.choice(['Central', 'East Side', 'West Side', 'North', 'South', 'Downtown', 'City', 'Riverside'])} Fire Station"
            
            FireStation.objects.create(
                name=station_name,
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
                city=fake.city(),
                country=fake.country(),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} FireStations created successfully.'))


    def populate_incidents(self, count):
        fake = Faker()
        locations = list(Locations.objects.all())
        for _ in range(count):
            Incident.objects.create(
                location=random.choice(locations),
                date_time=fake.date_time_this_year(),
                severity_level=random.choice(['Minor Fire', 'Moderate Fire', 'Major Fire']),
                description=fake.text(max_nb_chars=200),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} Incidents created successfully.'))

    def populate_firefighters(self, count):
        fake = Faker()
        xp_choices = [
            'Probationary Firefighter', 'Firefighter I', 'Firefighter II',
            'Firefighter III', 'Driver', 'Captain', 'Battalion Chief'
        ]
        for _ in range(count):
            Firefighters.objects.create(
                name=fake.name(),
                rank=random.choice(['Trainee', 'Senior', 'Commander']),
                experience_level=random.choice(xp_choices),
                station=random.choice(xp_choices),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} Firefighters created successfully.'))

    def populate_fire_trucks(self, count):
        fake = Faker()
        fire_stations = list(FireStation.objects.all())
        for _ in range(count):
            FireTruck.objects.create(
                truck_number=fake.bothify(text='TRK-####'),
                model=fake.word(),
                capacity=f"{random.randint(1000, 5000)} gallons",
                station=random.choice(fire_stations),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} FireTrucks created successfully.'))

    def populate_weather_conditions(self, count):
        fake = Faker()
        incidents = list(Incident.objects.all())
        for _ in range(count):
            WeatherConditions.objects.create(
                incident=random.choice(incidents),
                temperature=round(random.uniform(-10.0, 40.0), 2),
                humidity=round(random.uniform(10.0, 100.0), 2),
                wind_speed=round(random.uniform(0.0, 20.0), 2),
                weather_description=fake.sentence(),
            )
        self.stdout.write(self.style.SUCCESS(f'{count} WeatherConditions created successfully.'))