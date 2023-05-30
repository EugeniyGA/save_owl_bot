from geopy.geocoders import Nominatim
import ssl
import geopy.geocoders
import re
from dataclasses import dataclass

# Раскомментировать, если запускается на mac os
# ctx = ssl.create_default_context()
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE
# geopy.geocoders.options.default_ssl_context = ctx


@dataclass
class Geocode:
    latitude: float
    longitude: float


async def parse_address(address: str):
    if re.match(r'^geo:(-?\d+\.\d+):(-?\d+\.\d+)$', address):
        location = address.split(':')
        geodata = {'latitude': float(location[1]), 'longitude': float(location[2])}
        return Geocode(**geodata)
    else:
        return None


async def geocoder(geocode):
    if geocode:
        geodata = await parse_address(geocode)
        if geodata:
            geolocator = Nominatim(user_agent="telegram-bot")
            location = geolocator.reverse(f"{geodata.latitude},{geodata.longitude}")
            address = location.address
            return address
        else:
            return geocode
    else:
        return geocode
