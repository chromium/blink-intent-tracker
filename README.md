Automated Blink Intent Tracker
==============================

A set of services that automatically populate the ["Blink Intents" Google Spreadsheet](https://docs.google.com/a/chromium.org/spreadsheet/ccc?key=0AjGgk26K1Cc-dHJKNGtlLVlmSGRIYVR3LVRGYnVCRVE) with a list of the ["intent" emails](http://www.chromium.org/blink#TOC-Web-Platform-Changes:-Process) sent to the [blink-dev@chromium.org mailing list](https://groups.google.com/a/chromium.org/forum/#!forum/blink-dev).

Not everything is automated; [some work still needs to be done manually](https://docs.google.com/a/chromium.org/document/d/1p2g3hkjTGBIhGebn0ZvAwM88XksWIFD9tBb3hnefnOI/edit).

Overview
--------

* `jochen@chromium.org` has a [PuSH](https://pubsubhubbub.appspot.com/) Pubsubhubbub profile configured to send a POST request to `https://blink-intent-tracker-193211.appspot.com/rss-handler` whenever the [blink-dev 'topics' RSS feed](https://groups.google.com/a/chromium.org/forum/feed/blink-dev/topics/rss.xml?num=15) is updated.
* The blink-intent-tracker App Engine app (owned by `jochen@chromium.org`) processes the updates and sends a stripped down version to the [Apps Script web app](https://developers.google.com/apps-script/execution_web_apps) (also owned by `jochen@chromium.org`).
* The Apps Script web app adds the relevant content to the first empty row in the ["Blink Intents" Google Spreadsheet](https://docs.google.com/a/chromium.org/spreadsheet/ccc?key=0AjGgk26K1Cc-dHJKNGtlLVlmSGRIYVR3LVRGYnVCRVE).
