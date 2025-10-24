import requests
from typing import Optional, Tuple
from django.conf import settings


def geocode_address(
    street_address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    country: str = "USA"
) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an address using Google Geocoding API.

    Returns a tuple of (latitude, longitude) or (None, None) if geocoding fails.

    Args:
        street_address: Street address
        city: City name
        state: State/Province
        zip_code: ZIP/Postal code
        country: Country name

    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    api_key = settings.GOOGLE_MAPS_API_KEY

    if not api_key:
        print("Warning: GOOGLE_MAPS_API_KEY not set in environment variables")
        return None, None

    # Build the full address string from components
    address_parts = [
        part.strip()
        for part in [street_address, city, state, zip_code, country]
        if part and part.strip()
    ]

    if not address_parts:
        return None, None

    full_address = ", ".join(address_parts)

    # Use Google Geocoding API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": full_address,
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            print(f"Geocoded '{full_address}' to ({latitude}, {longitude})")
            return latitude, longitude
        else:
            print(f"Geocoding failed for '{full_address}': {data.get('status')}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error geocoding address: {e}")
        return None, None
