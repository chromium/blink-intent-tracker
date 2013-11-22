# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
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

def sendUpdateToAppsScript(sender, subject, link):
    raw_data = { 'sender': sender.encode('utf-8'),
                 'subject': subject.encode('utf-8'),
                 'link': link.encode('utf-8')}
    form_data = urllib.urlencode(raw_data)
    logging.info(form_data)
    urlfetch.fetch(url=APPS_SCRIPT_ENDPOINT,
                   payload=form_data,
                   method=urlfetch.POST,
                   headers={'Content-Type': 'application/x-www-form-urlencoded'})

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

# Process new RSS topics.
class ProcessRssTopic(webapp2.RequestHandler):

    # Returns true if the thread is an "Intent to *".
    def isIntent(self, subject):
        return re.match(r"^[^:]*[iI]ntent to .*", subject.encode('utf-8'))

    # items[0].permalinkUrl.
    # items[0].title
    def post(self):
        rssUpdate = json.loads(self.request.body)

        logging.info(rssUpdate)
        logging.info(rssUpdate['items'])
        logging.info(rssUpdate['items'][0])
        logging.info(rssUpdate['items'][0]['permalinkUrl'])
        logging.info(rssUpdate['items'][0]['title'])

        if (self.isIntent(rssUpdate['items'][0]['title'])):
            logging.info("It's an intent!")
            sendUpdateToAppsScript(
                rssUpdate['items'][0]['actor']['displayName'], 
                rssUpdate['items'][0]['title'], 
                rssUpdate['items'][0]['permalinkUrl'])

    # TODO(meh): extract subject, sender, and link from the RSS topic.  Load the thread in the web UI.
    # Parse the message to extract the chromestatus.com link and owp launch bug.
    # Send update to Apps Script.
    # You can reuse some code from below.

    # TODO(meh): Test if API owners LGTMed in their replies.

# Process new email messages from blink-dev.
class ProcessNewMessage(webapp2.RequestHandler):

    # Returns true if the thread is an "Intent to *".
    def isIntent(self, subject):
        # Regexp should not match "Re:..."
        return re.match(r"^[^:]*[iI]ntent to .*", subject.encode('utf-8'))

    def logEmailMessage(self, message):
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
        if self.isIntent(message.subject):
            logging.info('It is an intent!')
            link = self.getThreadPermalink(message.subject)
            sendUpdateToAppsScript(message.sender, message.subject, link)
        # Next up: elif self.isIntentReplyFromOwner(message.subject):


            
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rss-handler', ProcessRssTopic),
#    ('/_ah/mail/blink-update@blink-intent-tracker\.appspotmail\.com', ProcessNewMessage),
    # Google account pswrd: blink-updat (no 'e')
], debug=True)
