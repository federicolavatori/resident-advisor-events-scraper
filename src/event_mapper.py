from folium import CircleMarker, Map, Element, Marker, Popup, Icon
from folium.plugins import AntPath, LocateControl, MarkerCluster, TimestampedGeoJson
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import pandas as pd
from src.utils import get_lat_lon, scaler

# Configuring the  map
city = "Amsterdam"
lat = 52.3643889
lng = 4.8712701
map_type = "roadmap"
zoom = 12
base_URL = "https://ra.co"

# Initialize the map
m = Map(location=[lat, lng], zoom_start=zoom)

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv("./data/events.csv")

# Initialize the geolocator
geolocator = Nominatim(user_agent="my_geocoder")

# Apply the geocoding function to each row
df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(lambda x: get_lat_lon(x, geolocator)))

# Apply the scaling to the attending guests column
df['Guests_scaled'] = scaler(df,'Guests_attending', 5, 50)

# Add timestamp column
df['Date'] = pd.to_datetime(datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")

# Plot static markers with tooltip/popup
for event in df.dropna().itertuples():
    Marker(
        location=[event.Latitude, event.Longitude],
        popup=f'<a href="{base_URL}{event.Event_URL}" target="_blank">{base_URL}{event.Event_URL}</a>',
        icon=Icon(icon="music",
                  color="black",
                  icon_color="white")
    ).add_to(m)

# Locate the user
LocateControl(auto_start=False, initialZoomLevel = zoom).add_to(m)

# Define the data for the animated CircleMarker with gradual increase
initial_radius = 1
num_steps = 10
time_interval = timedelta(seconds=1)
features = []
current_time = datetime.now()

current_time = datetime.strptime('2024-01-20T00:00:00', "%Y-%m-%dT%H:%M:%S")
data = {
    'type': 'FeatureCollection',
    'features': []
}

for _, row in df.dropna().iterrows():
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [row['Longitude'],row['Latitude']]
        },
        'properties': {
            'time': current_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'icon': 'circle',
            'iconstyle': {
                'fillOpacity': 0.6,
                'radius': initial_radius,
                'color': '#53c688',
            },
        },
    }
    data['features'].append(feature)
    current_time_ = current_time
    for step in range(1, num_steps + 1):
        current_time_ += time_interval
        current_radius = initial_radius + (row['Guests_scaled'] - initial_radius) * step / num_steps

        data['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['Longitude'],row['Latitude']],
            },
            'properties': {
                'time': current_time_.strftime("%Y-%m-%dT%H:%M:%S"),
                'icon': 'circle',
                'iconstyle': {
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': current_radius,
                    'color': '#69b3a2',
                },
            },
        })

timestamped_geojson = TimestampedGeoJson(data['features'],
                                         period='PT1S',
                                         duration='PT1H',
                                         transition_time=100,
                                         auto_play=True)

# Add the TimestampedGeoJson layer to the map
timestamped_geojson.add_to(m)

# Add title to the map
m.get_root().html.add_child(Element(f"<h3 align='center'>RA Events in {city}</h3>"))

# Show map
m.show_in_browser()

