import Mandrill as m

def send_delivery_email(to_email_list):
	success = m.send_delivery_confirmation(to_email_list)
	return success