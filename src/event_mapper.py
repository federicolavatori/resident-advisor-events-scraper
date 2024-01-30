from folium import Element, Map, Marker, Icon
from folium.plugins import TimestampedGeoJson
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np

class EventMapper:
    """
    A class for mapping events using Folium, geopy, and pandas.

    Attributes:
        city (str): The city where events are located.
        lat (float): The latitude coordinate for the map center.
        lng (float): The longitude coordinate for the map center.
        map_type (str): The type of the map (e.g., 'roadmap').
        zoom (int): The initial zoom level of the map.
        base_URL (str): The base URL for event links.

    Methods:
        get_lat_lon(address, geolocator):
            Get latitude and longitude coordinates for a given address using a geolocation service.

        scaler(df, col, new_min, new_max):
            Scale the values in a specified column of a DataFrame to a new range.

        pre_process(df, geolocator):
            Pre-process the DataFrame by adding latitude, longitude, scaled guests, and timestamp columns.

        plot_static_markers(df):
            Plot static markers on the map with tooltip/popup.

        plot_animated_markers(df):
            Plot animated CircleMarkers with gradual increase in size based on guest attendance.

        show_map():
            Display the map in the default web browser.
    """

    def __init__(self, city, lat, lng, map_type, zoom, base_URL):
        """
        Initialize the EventMapper object.

        Parameters:
            city (str): The city where events are located.
            lat (float): The latitude coordinate for the map center.
            lng (float): The longitude coordinate for the map center.
            map_type (str): The type of the map (e.g., 'roadmap').
            zoom (int): The initial zoom level of the map.
            base_URL (str): The base URL for event links.
        """
        self.city = city
        self.lat = lat
        self.lng = lng
        self.map_type = map_type
        self.zoom = zoom
        self.base_URL = base_URL
        self.m = Map(location=[lat, lng], zoom_start=zoom)

    def get_lat_lon(self, address, geolocator):
        """
        Get latitude and longitude coordinates for a given address using a geolocation service.

        Parameters:
            address (str): The address for which to retrieve coordinates.
            geolocator: An instance of a geolocation service (e.g., geopy.Nominatim).

        Returns:
            Tuple(float, float) or Tuple(None, None): A tuple containing latitude and longitude if the address
            is successfully geocoded; otherwise, returns (None, None).
        """
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    def scaler(self, df, col, new_min, new_max):
        """
        Scale the values in a specified column of a DataFrame to a new range.

        Parameters:
            df (pd.DataFrame): The DataFrame containing the target column.
            col (str): The column to be scaled.
            new_min (int): The minimum value of the new range.
            new_max (int): The maximum value of the new range.

        Returns:
            pd.Series: A new column with scaled values within the specified range.
        """
        original_column = np.array(df[col])
        min_value = np.min(original_column)
        max_value = np.max(original_column)
        scaled_column = np.round(((original_column - min_value) / (max_value - min_value)) * (new_max - new_min) + new_min).astype(int)
        return scaled_column

    def pre_process(self, df, geolocator):
        """
        Pre-process the DataFrame by adding latitude, longitude, scaled guests, and timestamp columns.

        Parameters:
            df (pd.DataFrame): The DataFrame to be pre-processed.
            geolocator: An instance of a geolocation service (e.g., geopy.Nominatim).

        Returns:
            pd.DataFrame: The pre-processed DataFrame.
        """
        df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(lambda x: self.get_lat_lon(x, geolocator)))
        df['Guests_scaled'] = self.scaler(df, 'Guests_attending', 5, 50)
        df['Date'] = pd.to_datetime(datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
        return df

    def plot_static_markers(self, df):
        """
        Plot static markers on the map with tooltips/popup.

        Parameters:
            df (pd.DataFrame): The DataFrame containing event information.
        """
        for event in df.dropna().itertuples():
            Marker(
                location=[event.Latitude, event.Longitude],
                popup=f'<a href="{self.base_URL}{event.Event_URL}" target="_blank">{self.base_URL}{event.Event_URL}</a>',
                icon=Icon(icon="music", color="black", icon_color="white")
            ).add_to(self.m)

    def plot_animated_markers(self, df):
        """
        Plot animated CircleMarkers with gradual increase in size based on guest attendance.

        Parameters:
            df (pd.DataFrame): The DataFrame containing event information.
        """
        initial_radius = 1
        num_steps = 10
        time_interval = timedelta(seconds=1)
        current_time = datetime.now()

        data = {
            'type': 'FeatureCollection',
            'features': []
        }

        for _, row in df.dropna().iterrows():
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['Longitude'], row['Latitude']]
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
                        'coordinates': [row['Longitude'], row['Latitude']],
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

        timestamped_geojson.add_to(self.m)

    def show_map(self):
        self.m.get_root().html.add_child(Element(f"<h3 align='center'>RA Events in {self.city}</h3>"))
        self.m.show_in_browser()


if __name__ == "__main__":
    city = "Amsterdam"
    lat = 52.3643889
    lng = 4.8712701
    map_type = "roadmap"
    zoom = 12
    base_URL = "https://ra.co"

    event_mapper = EventMapper(city, lat, lng, map_type, zoom, base_URL)
    df = pd.read_csv("../data/events.csv")
    geolocator = Nominatim(user_agent="my_geocoder")

    # Process and plot
    df_processed = event_mapper.pre_process(df, geolocator)
    event_mapper.plot_static_markers(df_processed)
    event_mapper.plot_animated_markers(df_processed)
    event_mapper.show_map()