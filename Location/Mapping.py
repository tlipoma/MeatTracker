import os
import sys
import googlemaps

# Build google maps access
GOOGLE_API_KEY = os.environ['GOOG_MAPS_KEY']
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


def address_to_geo(address_string):

	# Get first location response (the best response)
	try:
		response = gmaps.geocode(address_string)
		location_data = response[0]['geometry']['location']
	except:
		print address_string
		print response
		input("Error in Mapping.address_to_geo: Press any key to cont...")
	return location_data['lat'], location_data['lng']



if __name__ == '__main__':
	address_string = sys.argv[1]
	lat, lng = address_to_geo(address_string)
	print str(lat) + " : " + str(lng)
	print('done')