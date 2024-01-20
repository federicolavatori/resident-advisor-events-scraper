from bokeh.plotting import gmap, output_file, save
from geopy.geocoders import Nominatim
from bokeh.models import ColumnDataSource, GMapOptions,HoverTool
from bokeh.io import show
import pandas as pd
import configparser
from src.utils import get_lat_lon, scaler


# configuring the Google map
city = 'Amsterdam'
lat = 52.3643889
lng = 4.8712701
map_type = "roadmap"
zoom = 12
google_map_options = GMapOptions(lat=lat,
                                 lng=lng,
                                 map_type=map_type,
                                 zoom=zoom)

# generating the Google map
config = configparser.ConfigParser()
config.read('config.ini')
google_api_key = config['google.maps']['api_key']

title = city
google_map = gmap(google_api_key,
                  google_map_options,
                  title=title)

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv("../data/events.csv")

# Initialize the geolocator
geolocator = Nominatim(user_agent="my_geocoder")

# Apply the geocoding function to each row
df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(lambda x: get_lat_lon(x, geolocator)))

#Apply the scaling the attending guests column
df['Guests_scaled'] = scaler(df,'Guests_attending', 1, 100)


# the coordinates of the glyphs
source = ColumnDataSource(
    data=dict(lat = df['Latitude'],
              lon = df['Longitude'],
              event_name = df['Event_name'],
              venue_name = df['Venue_name'],
              guests = df['Guests_attending'],
              scaled_guests = df['Guests_scaled']))


# Set tooltips
TOOLTIPS = [
    ("Event", "@event_name"),
    ("Venue", "@venue_name"),
    ("Guests", "@guests"),
    ("Guests Scaled", "@scaled_guests")

]

google_map.add_tools( HoverTool(tooltips=TOOLTIPS))

# generating the glyphs on the Google map
x = "lon"
y = "lat"
size = "scaled_guests"
fill_color = "blue"
fill_alpha = 1
google_map.circle_dot(x=x,
                      y=y,
                      size=size,
                      fill_color=fill_color,
                      fill_alpha=fill_alpha,
                      source=source)

# saving
output_file('../data/event_mapper.html', mode='inline')
save(google_map)

# displaying the model
show(google_map)

