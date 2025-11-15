import requests
from typing import Optional, Tuple
from django.conf import settings


def geocode_applicant_address(
    street_address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    country: str = "USA",
    use_exact: bool = True
) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an applicant's address using Google Geocoding API.

    If use_exact is False or street_address is empty, only geocodes city/state
    to provide approximate location for privacy.

    Returns a tuple of (latitude, longitude) or (None, None) if geocoding fails.

    Args:
        street_address: Street address (optional)
        city: City name
        state: State/Province
        zip_code: ZIP/Postal code
        country: Country name
        use_exact: If True, use street address for exact location;
                   If False, use only city/state for approximate location

    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    api_key = settings.GOOGLE_MAPS_API_KEY

    if not api_key:
        print("Warning: GOOGLE_MAPS_API_KEY not set in environment variables")
        return None, None

    # Build the address string based on privacy preference
    if use_exact and street_address and street_address.strip():
        # Use full address for exact location
        address_parts = [
            part.strip()
            for part in [street_address, city, state, zip_code, country]
            if part and part.strip()
        ]
    else:
        # Use only city/state for approximate location (privacy mode)
        address_parts = [
            part.strip()
            for part in [city, state, country]
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
            print(f"Geocoded applicant address '{full_address}' to ({latitude}, {longitude})")
            return latitude, longitude
        else:
            print(f"Geocoding failed for applicant address '{full_address}': {data.get('status')}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error geocoding applicant address: {e}")
        return None, None
