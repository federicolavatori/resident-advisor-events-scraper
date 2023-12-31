from bokeh.plotting import gmap, output_file, save
from geopy.geocoders import Nominatim
from bokeh.models import ColumnDataSource, GMapOptions,HoverTool
from bokeh.io import show
import pandas as pd
import numpy as np
import configparser

def get_lat_lon(address, geolocator):
    """
    Get latitude and longitude coordinates for a given address using a geolocation service.

    Parameters:
    - address (str): The address for which to retrieve coordinates.
    - geolocator: An instance of a geolocation service (e.g., geopy.Nominatim).

    Returns:
    Tuple(float, float) or Tuple(None, None): A tuple containing latitude and longitude if the address
    is successfully geocoded; otherwise, returns (None, None).
    """
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def scaler(df, col, new_min, new_max):
    """
    Scale the values in a specified column of a DataFrame to a new range.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the target column.
    - col (str): The column to be scaled.
    - new_min (int): The minimum value of the new range.
    - new_max (int): The maximum value of the new range.

    Returns:
    pd.Series: A new column with scaled values within the specified range.
    """
    original_column = np.array(df[col])
    min_value = np.min(original_column)
    max_value = np.max(original_column)
    scaled_column = np.round(((original_column - min_value) / (max_value - min_value)) * (new_max - new_min) + new_min).astype(int)
    return scaled_column


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
google_api_key = config['DEFAULT']['google_api_key']

title = city
google_map = gmap(google_api_key,
                  google_map_options,
                  title=title)

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv("data/events.csv")

# Initialize the geolocator
geolocator = Nominatim(user_agent="my_geocoder")

# Apply the geocoding function to each row
df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(lambda x: get_lat_lon(x, geolocator)))

#Apply the scaling the attending guests column
df['Number of guests scaled'] = scaler(df,'Number of guests attending', 1, 100)


# the coordinates of the glyphs
source = ColumnDataSource(
    data=dict(lat = df['Latitude'],
              lon = df['Longitude'],
              event_name = df['Event name'],
              venue_name = df['Venue'],
              guests = df['Number of guests attending'],
              scaled_guests = df['Number of guests scaled']))


# Set tooltips
TOOLTIPS = [
    ("Event", "@event_name"),
    ("Venue", "@venue_name"),
    ("Guests", "@guests"),
    ("Scaled Guests", "@scaled_guests")

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
output_file('data/event_mapper.html', mode='inline')
save(google_map)

# displaying the model
show(google_map)

