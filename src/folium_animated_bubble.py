from folium import Map, Popup, Marker, Icon
from folium.plugins import TimestampedGeoJson
from datetime import datetime, timedelta
import geojson
import json

# Create a Folium map centered at a specific location
latitude = 52.3643889
longitude= 4.8712701
map_center = [latitude, longitude]
my_map = Map(location=map_center, zoom_start=12)

# Define the data for the animated CircleMarker with gradual increase
initial_radius = 1
final_radius = 50
num_steps = 10
time_interval = timedelta(seconds=1)


# Create initial GeoJSON feature with a fixed popup
data = {
    'type': 'FeatureCollection',
    'features': [{
    'type': 'Feature',
    'geometry': {
        'type': 'Point',
        'coordinates': [longitude, latitude],
    },
    'properties': {
        'time': '2024-01-20T00:00:00',
        'popup': 'CircleMarker Popup',
        'icon': 'circle',
        'iconstyle': {
            'fillOpacity': 0.6,
            'radius': initial_radius,
            'color': '#53c688',
        },
    },
}
]
}

current_time = datetime.strptime(data['features'][0]['properties']['time'], "%Y-%m-%dT%H:%M:%S")

for step in range(1, num_steps + 1):
    current_time += time_interval
    current_radius = initial_radius + (final_radius - initial_radius) * step / num_steps

    data['features'].append({
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [longitude, latitude],
        },
        'properties': {
            'time': current_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'popup': 'CircleMarker Popup',
            'icon': 'circle',
            'iconstyle': {
                'fillOpacity': 0.8,
                'stroke': 'true',
                'radius': current_radius,
                'color': '#69b3a2',
            },
        },
    })

print(len(data['features']))
# Create a TimestampedGeoJson layer with the data
timestamped_geojson = TimestampedGeoJson(data,
                                         period='PT1S',
                                         duration='PT1H',
                                         transition_time=100,
                                         auto_play=True)

popup_content = 'CircleMarker Popup'
initial_marker = Marker(
    location=[latitude, longitude],
    popup=Popup(popup_content, sticky=True),
    icon=Icon(icon="music",
              color="black",
              icon_color="white")
)
my_map.add_child(initial_marker)

# Add the TimestampedGeoJson layer to the map
timestamped_geojson.add_to(my_map)

# Display the map
my_map.show_in_browser()
