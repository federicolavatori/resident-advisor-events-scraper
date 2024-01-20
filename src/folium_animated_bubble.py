import folium
from folium import plugins
from datetime import datetime, timedelta

# Create a Folium map centered at a specific location
latitude = 52.3643889
longitude= 4.8712701
map_center = [latitude, longitude]
my_map = folium.Map(location=map_center, zoom_start=12)

# Define the data for the animated CircleMarker with gradual increase
initial_radius = 1
final_radius = 50
num_steps = 10
fps = 2
time_interval = timedelta(seconds=1 / fps)

data = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [longitude, latitude],  # Same as map_center
            },
            'properties': {
                'time': '2024-01-20T00:00:00',  # Initial time
                'popup': 'CircleMarker Popup',
                'icon': 'circle',
                'iconstyle': {
                    'fillOpacity': 0.6,
                    'radius': initial_radius,
                    'color': 'red',
                },
            },
        },
    ],
}

current_time = datetime.strptime(data['features'][0]['properties']['time'], "%Y-%m-%dT%H:%M:%S")

for step in range(1, num_steps + 1):
    current_time += time_interval
    current_radius = initial_radius + (final_radius - initial_radius) * step / num_steps

    data['features'].append({
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [longitude, latitude],  # Same as map_center
        },
        'properties': {
            'time': current_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'popup': 'CircleMarker Popup',
            'icon': 'circle',
            'iconstyle': {
                'fillOpacity': 0.6,
                'radius': current_radius,
                'color': 'red',
            },
        },
    })

# Create a TimestampedGeoJson layer with the data
timestamped_geojson = plugins.TimestampedGeoJson(data)

# Add the TimestampedGeoJson layer to the map
timestamped_geojson.add_to(my_map)

# Display the map
my_map.show_in_browser()
