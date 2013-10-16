import logging
import re
import urllib
import webapp2

from xml.etree import ElementTree

from google.appengine.api import mail
from google.appengine.api import urlfetch


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class ProcessNewMessage(webapp2.RequestHandler):

    def post(self):
    	message = mail.InboundEmailMessage(self.request.body)
        
        # Debug info
        '''
        logging.info('----- message.sender:\n')
        logging.info(message.sender)
        logging.info('----- message.subject:\n')
        logging.info(message.subject)
        logging.info('----- message.bodies:\n')
        bodies = message.bodies('text/plain')
        for content_type, body in bodies:
            logging.info(body.decode())
        '''

        OWNERS = ["abarth", "darin", "dglazkov", "eseidel", "jochen", "ojan", "tkent"]
        # See if this is an intent thread.
        if re.match(r"^[^:]*[iI]ntent to .*", message.subject.encode('utf-8')): # Regexp should not match "Re: Intent to Implement"
            logging.info('It is an intent!\n')

            link = ''

            # Find the link to this intent in the rss feed.
            result = urllib.urlopen('https://groups.google.com/a/chromium.org/forum/feed/blink-dev/topics/rss.xml?num=15').read()
            tree = ElementTree.fromstring(result)
            logging.info(tree.attrib)
            for elem in tree.iter('item'):
                if str(message.subject) == str(elem.find('title').text):
                    link = str(elem.find('link').text)
                    break

            logging.info(link)

            # Endpoint for the Google Apps script that handles Blink intents.
            url = 'https://script.google.com/macros/s/AKfycbxC7WYOYdLxY40wvP3DwNfK9OAT_fYXRHZzavn1_BzJQqU4akc/exec'

            # Construct response.
            raw_data = { 'sender'  : message.sender.encode('utf-8'),
                         'subject' : message.subject.encode('utf-8'),
                         'link'    : link.encode('utf-8')}
            form_data = urllib.urlencode(raw_data)

            # Send post request to script.
            result = urlfetch.fetch(url=url,
                                    payload=form_data,
                                    method=urlfetch.POST,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/_ah/mail/blink-update@blink-intent-tracker\.appspotmail\.com', ProcessNewMessage),
    # Google account pswrd: blink-updat (no 'e')
], debug=True)
