import os
import googlemaps

# Build google maps access
GOOGLE_API_KEY = os.environ['GOOG_MAPS_KEY']
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
