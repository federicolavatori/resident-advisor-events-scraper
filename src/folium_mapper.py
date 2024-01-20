from folium import CircleMarker, Map, Element
from folium.plugins import AntPath
from geopy.geocoders import Nominatim
import pandas as pd
from src.utils import get_lat_lon, scaler

# configuring the  map
city = 'Amsterdam'
lat = 52.3643889
lng = 4.8712701
map_type = "roadmap"
zoom = 12

# Initialize the map
m = Map(location=[lat, lng], zoom_start=zoom)

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv("./data/events.csv")

# Initialize the geolocator
geolocator = Nominatim(user_agent="my_geocoder")

# Apply the geocoding function to each row
df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(lambda x: get_lat_lon(x, geolocator)))

#Apply the scaling the attending guests column
df['Guests_scaled'] = scaler(df,'Guests_attending', 1, 100)

for event in df.dropna().itertuples():
    CircleMarker(
        location=[event.Latitude, event.Longitude],
        popup=[event.Venue_name, event.Guests_attending],
        radius=float(event.Guests_scaled),
        color='#69b3a2',
        fill=True,
        fill_color='#69b3a2'
   ).add_to(m)

# A title can be added to the map, if desired.
m.get_root().html.add_child(Element(f"<h3 align='center'>RA Events in {city}</h3>"))

m.show_in_browser()

