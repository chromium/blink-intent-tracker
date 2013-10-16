import logging
import re
import urllib
import webapp2
from xml.etree import ElementTree
from google.appengine.api import mail
from google.appengine.api import urlfetch


# Constants
BLINK_DEV_RSS_URL = 'https://groups.google.com/a/chromium.org/forum/feed/blink-dev/topics/rss.xml?num=15'
APPS_SCRIPT_ENDPOINT = 'https://script.google.com/macros/s/AKfycbxC7WYOYdLxY40wvP3DwNfK9OAT_fYXRHZzavn1_BzJQqU4akc/exec'
OWNERS = ["abarth", "darin", "dglazkov", "eseidel", "jochen", "ojan", "tkent"]


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class ProcessNewMessage(webapp2.RequestHandler):

    # Returns true if the thread is an "Intent to *".
    def isIntent(subject):
        # Regexp should not match "Re:..."
        return re.match(r"^[^:]*[iI]ntent to .*", message.subject.encode('utf-8'))
    
    # Find the link to this intent in the rss feed.
    def getThreadPermalink(subject):
        result = urllib.urlopen(BLINK_DEV_RSS_URL).read()
        tree = ElementTree.fromstring(result)
        logging.info(tree.attrib)
        for elem in tree.iter('item'):
            if str(message.subject) == str(elem.find('title').text):
                return str(elem.find('link').text)
        return ''

    def sendUpdateToAppsScript(message):
        link = getThreadPermalink(subject)
        raw_data = { 'sender'  : message.sender.encode('utf-8'),
                     'subject' : message.subject.encode('utf-8'),
                     'link'    : link.encode('utf-8')}
        form_data = urllib.urlencode(raw_data)
        result = urlfetch.fetch(url=APPS_SCRIPT_ENDPOINT,
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def logEmailMessage(message):
        logging.info('----- message.sender:\n')
        logging.info(message.sender)
        logging.info('----- message.subject:\n')
        logging.info(message.subject)
        logging.info('----- message.bodies:\n')
        bodies = message.bodies('text/plain')
        for content_type, body in bodies:
            logging.info(body.decode())

    def post(self):
    	message = mail.InboundEmailMessage(self.request.body)
        if isIntent(message.subject):
            sendUpdateToAppsScript(message)

            
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/_ah/mail/blink-update@blink-intent-tracker\.appspotmail\.com', ProcessNewMessage),
    # Google account pswrd: blink-updat (no 'e')
], debug=True)
