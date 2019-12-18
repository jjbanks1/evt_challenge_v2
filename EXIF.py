import sys
import exifread
from geopy.geocoders import Nominatim
import json
import logging
import glob
import time

# Checks file header to determine if it is a valid JPEG file
def is_jpg(file):
    # Read Header
	data = file.read(11)

    # Read Header
	# See https://en.wikipedia.org/wiki/List_of_file_signatures and https://en.wikipedia.org/wiki/JPEG for reference
	signature = data[:4]
	file_format = data[6:]
	
	logging.info('File signature: "{}"'.format(str(signature)))
	logging.info('File Format: "{}"'.format(str(file_format)))

	# Valid JPEG indicators
	valid_signatures = [b'\xff\xd8\xff\xdb', b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xee']
	valid_file_formats = [b'JFIF\0', b'Exif\x00']

	# Check signature and file format of the file
	is_jpg = False
	if signature in valid_signatures and file_format in valid_file_formats:
		is_jpg = True

	return is_jpg

# Calculates either a latitude or longitude decimal value based on 
#   respective radian radios and direction indication originating from GPS tags of a JPEG file.
def convert_tagdms_to_decimal(gpstag, directiontag, precision=4):
    # Calculate radian component values from ratios
	degrees = gpstag.values[0].num / gpstag.values[0].den
	minutes = gpstag.values[1].num / gpstag.values[1].den
	seconds = gpstag.values[2].num / gpstag.values[2].den

	# Pull direction component for negativity indication
	direction = directiontag.values

	return convert_dms_to_decimal(degrees, minutes, seconds, direction, precision)

# Calculates either a latitude or longitude decimal value based on 
#   respective radian decimals (ie. Degrees Minutes Seconds / DMS) and a direction indication.
def convert_dms_to_decimal(degrees, minutes, seconds, direction, precision=4):
	dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
	if direction == 'S' or direction == 'W':
		dd *= -1
	dd = round(dd, precision)
	return dd

# Extracts a Lat Lon tuple from GPS Tag info originating from JPEG files
def extract_latlon(gps_tags):
	lat_lon = None
	if 'GPS GPSLatitude' in gps_tags: 
		gps_lat = gps_tags['GPS GPSLatitude']
		gps_lat_dir = gps_tags['GPS GPSLatitudeRef']
		gps_lat_val = convert_tagdms_to_decimal( gps_lat, gps_lat_dir )

		if 'GPS GPSLongitude' in gps_tags: 
			gps_lon = gps_tags['GPS GPSLongitude']
			gps_lon_dir = gps_tags['GPS GPSLongitudeRef']
			gps_lon_val = convert_tagdms_to_decimal( gps_lon, gps_lon_dir )
	
			lat_lon = (gps_lat_val,gps_lon_val)
	return lat_lon

# Utilizes GPS tags extracted from a JPEG file to perform a reverse lookup of a Geo Location Address
#   from a latitude and longitude combination
def reverse_lookup_zipcode( gps_tags, user_agent, location_cache=None ):
	lat_lon = extract_latlon( gps_tags )
	logging.info('Extracted Lat Lon of: "{}"'.format(lat_lon))

	zipcode = None
	if lat_lon is not None:
    	# Lookup location from cache
		loc_key = None
		if location_cache is not None:
			loc_key = str(lat_lon)
			if loc_key in location_cache:
				zipcode = location_cache[loc_key]

		# Do a reverse lookup of the address from the Lat Lon and extract the zipcode.
		if zipcode is None:
			reverse_lookup_data = "{},{}".format(lat_lon[0],lat_lon[1])
			logging.info('Doing reverse lookup on "{}"'.format(reverse_lookup_data))

    		# Do the reverse lookup
			for i in range(20):
				try:
					# Try up to 20 times if the account isn't working
					user_agent_id = user_agent + str(i)
					geolocator = Nominatim(user_agent=user_agent_id)
					location = geolocator.reverse( reverse_lookup_data )
					break
				except Exception as ex:
					logging.warning('Unable to reverse geo locate with current account.  Will retry with a different user agent.  Try #{}'.format(i+1))
					time.sleep(float(i))

			logging.info('Received reverse lookup results of: "{}"'.format(location))

			# Extract the Zip Code
			address_parts = location.address.split(',')
			zip_position = len(address_parts)-2
			if(zip_position >= 0):
				zipcode = address_parts[zip_position].strip()

		# Update location in cache
		if location_cache is not None:
			if loc_key not in location_cache:
				location_cache[loc_key] = zipcode

	return zipcode

# Extract GPS tags from JPEG file and do a reverse lookup using the GPS Tags to get a Zipcode
def determine_file_zipcode( file, user_agent, location_cache=None ):
	zipcode = None
	if file is not None:
    	# Read from beginning of the file
		file.seek(0,0)

		# Extract Exif tags from JPEG file
		tags = exifread.process_file(file)

		# Filterout non-gps tags
		for tag in tags.keys():
			if tag[:3] == 'GPS':
				logging.info('Extracting tag "{}" with value of "{}"'.format(tag, tags[tag]))
				gps_tags[tag] = tags[tag]
		
		# Reverse lookup zipcode from GPS tags
		zipcode = reverse_lookup_zipcode( gps_tags, user_agent, location_cache )
	return zipcode

# Load a json based cache from a file
def load_location_cache( filename ):
	logging.info('Loading location cache using filename "{}"'.format(filename))

	location_cache = {}
	f_cache = None
	try:
		f_cache = open( filename )
		location_cache = json.load(f_cache)	
	except IOError:
		logging.warning('Location cache file cannot be retrieved. Note this is expected the first time it is run, if cache file not included')
	finally:
		if f_cache is not None:
			f_cache.close()

	return location_cache

# Save the reverse lookup of zipcode results 
def save_location_cache( location_cache, filename ):    	
	try:
		logging.info('Saving location cache as filename "{}"'.format(filename))
		with open( filename, 'w' ) as f_cache:
			json.dump(location_cache, f_cache)			
	except IOError:
		logging.warning('Location Cache File cannot be written. Will occur if unable to write the cache to disk (ie. maybe readonly access).')
	finally:
		if f_cache is not None:
			f_cache.close()

# Load the application configuration
def load_config( config_name='config.json' ):
	config = {}
	f_config = None
	try:
		f_config = open( config_name )
		config = json.load( f_config )	
	except IOError:
		print("ERROR: Settings file cannot be retrieved!")
	finally:
		if f_config is not None:
			f_config.close()

	return config

def convert_to_loglevel(log_level):
	level = logging.NOTSET
	if log_level == 'INFO':
		level = logging.INFO
	elif log_level == 'DEBUG':
		level = logging.DEBUG
	elif log_level == 'WARNING':
		level = logging.WARNING
	elif log_level == 'CRITICAL':
		level = logging.CRITICAL
	elif log_level == 'ERROR':
		level = logging.ERROR
	return level

if __name__ == "__main__":
    # Initialization of configuration settings and logging
	config = load_config()
	log_filename = config['logging']['filename']
	log_level = convert_to_loglevel(config['logging']['level'])
	logging.basicConfig(filename=log_filename,level=log_level)

	logging.info('Started application')

	location_cache = load_location_cache( filename=config['cache']['filename'] )

	file = None
	path_name = None
	try:
		logging.info('Looping through file files to check')
		for i in range(1, len(sys.argv)):    
			valid_jpg = False
			has_geolocation = False
			zipcode = None
			try:
				if len(sys.argv) > i:
					path_name = sys.argv[i]

				logging.info('Opening image file')
				subfiles = []
				if '*' in path_name or '?' in path_name:
					subfiles = glob.glob(path_name)
				else:
					subfiles.append(path_name)
				
				for path_name in subfiles:
					try:
						file = open(path_name, 'rb')

						gps_tags = {}
						valid_jpg = is_jpg(file)
						if valid_jpg == True:
							# Open image file for reading (binary mode)
							zipcode = determine_file_zipcode( file, config['geocoding']['user_agent'], location_cache )
							if zipcode is not None:
								print('"{}", {}'.format(path_name, zipcode))
							else:
								print('"{}", {}'.format(path_name, config['tags']['no_geocode']))
						else:
							print('"{}", {}'.format(path_name, config['tags']['not_jpeg']))
						if file is not None:
							file.close()
					except FileNotFoundError:
						print('"{}", {}'.format(path_name, config['tags']['file_not_found']))
					except OSError as ex:
						print('"{}", {}'.format(path_name, config['tags']['internal_error']))
						logging.error( str(ex)  )
					except Exception as ex: # catch *all* exceptions
						#e = sys.exc_info()[0]
						print('"{}", {}'.format(path_name, config['tags']['internal_error']))
						logging.error( str(ex) )
						if file is not None:
							file.close()
					
			except Exception as ex: # catch *all* exceptions
				#e = sys.exc_info()[0]
				print('"{}", {}'.format(path_name, config['tags']['internal_error']))
				logging.error( str(ex) )
				if file is not None:
					file.close()
			file = None

		save_location_cache(location_cache, filename=config['cache']['filename'])

	except Exception as ex: # catch *all* exceptions
		#e = sys.exc_info()[0]
		logging.error( str(ex) )
