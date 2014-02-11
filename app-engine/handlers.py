# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import logging
import re
import urllib
import webapp2
from google.appengine.api import urlfetch


APPS_SCRIPT_ENDPOINT = 'https://script.google.com/macros/s/AKfycbxC7WYOYdLxY40wvP3DwNfK9OAT_fYXRHZzavn1_BzJQqU4akc/exec'
# OWNERS = ["abarth", "darin", "dglazkov", "eseidel", "jochen", "ojan", "tkent"]


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


class ProcessRssTopic(webapp2.RequestHandler):

    def isIntent(self, subject):
        return re.match(r"^[^:]*intent to .*", subject.encode('utf-8').lower())

    def post(self):
        rssUpdate = json.loads(self.request.body)

        logging.info(rssUpdate)

        for item in rssUpdate['items']:
            logging.info(item['permalinkUrl'])
            logging.info(item['title'])

            if (self.isIntent(rssUpdate['items'][0]['title'])):
                logging.info("It's an intent!")
                sendUpdateToAppsScript(
                    item['actor']['displayName'], 
                    item['title'], 
                    item['permalinkUrl'])

    # TODO(meh): Test if API owners LGTMed in their replies.
   

application = webapp2.WSGIApplication([
    ('/rss-handler', ProcessRssTopic)
], debug=True)
