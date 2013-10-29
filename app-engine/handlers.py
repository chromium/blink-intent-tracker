# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

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

class ProcessRssTopic(webapp2.RequestHandler):

    def post(self):
        logging.info(self.request.body)


class ProcessNewMessage(webapp2.RequestHandler):

    # Returns true if the thread is an "Intent to *".
    def isIntent(self, subject):
        # Regexp should not match "Re:..."
        return re.match(r"^[^:]*[iI]ntent to .*", subject.encode('utf-8'))
    
    # Find the link to this intent in the RSS feed.
    # TODO(meh): Fix race condition with RSS feed.  Often the RSS feed hasn't been updated by the time
    # this code receives the email.  Alternatives:
    # - Sleep for 1hr.  Might prevent the server from handlying other inputs sent in that timefram.
    # - Subscribe to the RSS feed and:
    #   - Send another request to the trix apps script with the link.
    #   - Store the email information here locally until the RSS link comes in.  Then send the request to Apps Script with everything.
    # - Multithreading?
    def getThreadPermalink(self, subject):
        result = urllib.urlopen(BLINK_DEV_RSS_URL).read()
        tree = ElementTree.fromstring(result)
        logging.info(tree.attrib)
        for elem in tree.iter('item'):
            if subject.encode('utf-8') == '[blink-dev] ' + elem.find('title').text:
                return elem.find('link').text
        return 'No link found'

    def sendUpdateToAppsScript(self, message):
        link = self.getThreadPermalink(message.subject)
        raw_data = { 'sender': message.sender.encode('utf-8'),
                     'subject': message.subject.encode('utf-8'),
                     'link': link.encode('utf-8')}
        form_data = urllib.urlencode(raw_data)
        logging.info(form_data)
        urlfetch.fetch(url=APPS_SCRIPT_ENDPOINT,
                       payload=form_data,
                       method=urlfetch.POST,
                       headers={'Content-Type': 'application/x-www-form-urlencoded'})

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
            self.sendUpdateToAppsScript(message)
        # Next up: elif self.isIntentReplyFromOwner(message.subject):


            
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rss-handler', ProcessRssUpdate),
#    ('/_ah/mail/blink-update@blink-intent-tracker\.appspotmail\.com', ProcessNewMessage),
    # Google account pswrd: blink-updat (no 'e')
], debug=True)
