import mandrill
import os

# initialize mandrill client
try:
    MANDRILL_KEY = os.environ['MANDRILL_API_KEY']
    mandrill_client = mandrill.Mandrill(MANDRILL_KEY)
except mandrill.Error, e:
    print "Error setting up mandrill, either with connection or getting api key from env"
    print 'A mandrill error occurred: %s - %s' % (e.__class__, e)

'''
Simple sending functions
'''
def send_delivery_confirmation(email_address):
    try:
        template_content = [{}]
        message = {
            'to': [{'email': email_address}],
            'from_email' : 'members@waldenlocalmeat.com',
        }
        result = mandrill_client.messages.send_template(template_name='delivery-confirmation', template_content=template_content, message=message)
        if result[0]['reject_reason'] == None:
            return True
        else:
            return False
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
        # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'
        return False