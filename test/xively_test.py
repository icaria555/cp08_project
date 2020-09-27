#!/usr/bin/env python
import xively
import datetime
import sys
import time

XIVELY_API_KEY = "76Y451NhEYmDvWo87dOpkGJeS48cLP206mcN5VOeWqyYQoTR"
XIVELY_FEED_ID = 711362136

def main(*args):
    print args
    api = xively.XivelyAPIClient(XIVELY_API_KEY)
    feed = api.feeds.get(XIVELY_FEED_ID)
    now = datetime.datetime.utcnow()
    
    feed.datastreams = [
            xively.Datastream(id='Heart_rate_1', current_value=args[0], at=now),
            xively.Datastream(id='Spo2_1', current_value=args[1], at=now),
    ]
    feed.update()
              
if __name__ == '__main__':
    try:
        tmp = 0
        watts = 0
        while(True):
            main(tmp , watts)
            tmp += 1 if tmp < 50 else -20
            watts += 1 if watts < 50 else -20
    except KeyboardInterrupt:
        pass