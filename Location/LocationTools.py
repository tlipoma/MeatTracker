

# Use to verify and format zipcodes
# Usualy for fixing errors on leading zeros
def fix_zipcode(zipCode):
	# Convert to 'str'
	if type(zipCode) == int:
		zipCode = str(zipCode)

	# Check for missing leading 0
	if len(zipCode) < 5:
		for i in range(5 - len(zipCode)):
			zipCode = '0' + zipCode

	return zipCode