#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ebk-client - eBay Kleinanzeigen/Classifieds API client in Python
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""
import pprint
import html
import dateutil.parser
from datetime import datetime
from dateutil.tz import tzlocal

from ebk_client import EbkClient

api = EbkClient('app-username', 'app-password', 'ebay-user-name', 'ebay-user-password')
my_ads = api.get_my_ads()

now = datetime.now(tzlocal())
print('My ads:')
for ad in my_ads:
    id = ad.get('id', 0)
    creation = ad.get('start-date-time', {}).get('value', '').encode('utf-8')
    d = dateutil.parser.parse(creation)
    age_in_h = (now - d).total_seconds() / 3600

    title = ad.get('title', {}).get('value', '')
    title_unescaped = html.unescape(title)
    print("{} ({}) -> {}... ".format(id, age_in_h, title_unescaped))

# categories = api.get_categories(80)
# print('Subcategories of cat 80:\n\r{}'.format(pprint.PrettyPrinter(indent=4).pformat(categories)))

# locations = api.get_location_by_name('22')
# print('Location by german postcode 22:\n\r{}'.format(pprint.PrettyPrinter(indent=4).pformat(locations)))

# locations = api.get_location_by_coordinates(53.553155, 10.006151)
# print('Location Latitude/Longitude:\n\r{}'.format(pprint.PrettyPrinter(indent=4).pformat(locations)))

# category_attributes = api.get_category_attributes(88)
# print('Category Attributes for cat 88:\n\r{}'.format(pprint.PrettyPrinter(indent=4).pformat(category_attributes)))
