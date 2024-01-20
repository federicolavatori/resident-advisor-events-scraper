import numpy as np
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