from Database import DBTools as db


def init_from_csv(file_location):
	fo = open(file_location, 'r')
	for line in fo:
		print line
	fo.close()

