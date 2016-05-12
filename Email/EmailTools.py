import Mandrill as m

def send_delivery_email(to_email):
	success = m.send_delivery_confirmation(to_email)
	return success