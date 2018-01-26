# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import logging
import re
import urllib
import webapp2
from google.appengine.api import urlfetch


APPS_SCRIPT_ENDPOINT = 'https://script.google.com/a/chromium.org/macros/s/AKfycby-kGgowUQ0Ol_KxgL9VyWSRrz7ZrwsuoyM8JwPxvhG4x7VAlQy/exec'

RSS_FEED = 'https://groups.google.com/a/chromium.org/forum/feed/blink-dev/topics/rss.xml?num=15'


def sendUpdateToAppsScript(sender, subject, link):
    raw_data = {'sender': sender.encode('utf-8'),
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
        subject = subject.encode('utf-8').lower()
        return re.match(r'.*intent to .*:.*$', subject) and not re.match(r'.*(was|re):.*', subject)

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

    def get(self):
        if self.request.GET['hub.topic'] != RSS_FEED:
            self.error(400)
            return

        if self.request.GET['hub.mode'] != 'subscribe':
            self.error(400)
            return

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request.GET['hub.challenge'])
        return 

    # TODO(meh): Test if API owners LGTMed in their replies.


application = webapp2.WSGIApplication([
    ('/rss-handler', ProcessRssTopic)
], debug=True)
