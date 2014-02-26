#!/usr/bin/env python
'''
This is an example of a local DIM daemon check.

This check runs forever and every 10 seconds spits out a status telling
the DIM agent that we're doing A-OK.

Note that we actually give it multiple status updates, since local checks
are not limited to doing one thing.
'''

import json
import sys
import time


def main():
    print json.dumps({
        'check': 'potato_farm_yield',
        'status': 'warning',
        'output': 'Many potatoes this year, buy more trucks',
    })

    print json.dumps({
        'check': 'my_healthiness',
        'status': 'ok',
    })


if __name__ == '__main__':
    while True:
        main()
        time.sleep(10)
    sys.exit(0)
