#!/usr/bin/env python
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

import json
import base64
import hashlib
import dateutil.parser
import requests

from datetime import datetime
from dateutil.tz import tzlocal

try:
    from html import unescape  # python 3.4+
except ImportError:
    try:
        from html.parser import HTMLParser  # python 3.x (<3.4)
    except ImportError:
        from HTMLParser import HTMLParser  # python 2.x
    unescape = HTMLParser().unescape

class EbkClient:

    H_EBAYK_CLIENT_APP = '13a6dde3-935d-4cd8-9992-db8a8c4b6c0f1456515662228'
    H_EBAYK_CLIENT_VERSION = '5423'
    H_EBAYK_CLIENT_TYPE = 'ebayk-android-app-6.9.3'
    H_EBAYK_CLIENT_UA = 'Dalvik/2.1.0'

    URL_PREFIX = 'https://api.ebay-kleinanzeigen.de/api'

    username = None

    def __init__(self, app_username, app_password, user_username, user_password):

        try:
            import requests.packages.urllib3
            requests.packages.urllib3.disable_warnings()
        except:
            pass

        self.username = user_username
        app_auth = base64.b64encode('{}:{}'.format(app_username, app_password).encode('ascii')).decode("utf-8")
        
        hashed_user_password = base64.b64encode(hashlib.sha1(user_password.encode('ascii')).digest()).decode("utf-8")
        user_auth = 'email="{}",password="{}"'.format(user_username, hashed_user_password)

        header = {
            'X-EBAYK-APP': self.H_EBAYK_CLIENT_APP,
            'X-ECG-USER-VERSION': self.H_EBAYK_CLIENT_VERSION,
            'X-ECG-USER-AGENT': self.H_EBAYK_CLIENT_TYPE,
            'Authorization': 'Basic {}'.format(app_auth),
            'X-ECG-Authorization-User': user_auth,
            'User-Agent': self.H_EBAYK_CLIENT_UA,
            }

        self._session = requests.session()
        self._session.headers.update(header)

    def _validate_http_response(self, r):
        if r.status_code == 401:
            raise Exception('Access Denied (e.g. wrong app credentials or user credentials)')
        elif r.status_code == 404:
            raise Exception('Not found')
        elif r.status_code == 500:
            raise Exception('Internal Server Error (e.g. wrong request)')

    def _http_get(self, url_suffix):
        response = self._session.get( self.URL_PREFIX + url_suffix )
        self._validate_http_response(response)
        return response

    def _http_post(self, url_suffix, post_data = ''):
        response = self._session.post( self.URL_PREFIX + url_suffix, data=post_data, headers={'Content-Type': 'application/xml'} )
        print(response.content)
        self._validate_http_response(response)
        return response

    def _http_put(self, url_suffix, post_data = ''):
        response = self._session.put( self.URL_PREFIX + url_suffix, data=post_data, headers={'Content-Type': 'application/xml'} )
        self._validate_http_response(response)
        return response

    def _http_delete(self, url_suffix):
        response = self._session.delete( self.URL_PREFIX + url_suffix )
        self._validate_http_response(response)
        return response

    def get_my_ads(self):
        url = "/users/{}/ads.json?_in=id,title,start-date-time,ad-status".format(self.username)
        response = self._http_get(url)
        response_json = json.loads(response.content.decode('utf-8'))
        my_ads = response_json.get('{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads', {}).get('value', {}).get('ad', None)

        return my_ads

    def change_ad_status(self, ad_id, status):
        if status not in ['active', 'paused']:
            raise Exception('Wrong ad status')

        url = "/users/{}/ads/{}/{}.json".format(self.username, status, ad_id)
        response = self._http_put(url)

        if response.status_code == 204:
            return True
        else:
            return False

    def activate_ad(self, ad_id):
        return change_ad_status(ad_id, 'active')

    def deactivate_ad(self, ad_id):
        return change_ad_status(ad_id, 'paused')

    def delete_ad(self, ad_id):
        url = "/users/{}/ads/{}".format(self.username, ad_id)
        response = self._http_delete(url)

        if response.status_code == 204:
            return True
        else:
            return False

    def create_ad(self, xml):
        url = "/users/{}/ads.json".format(self.username)
        response = self._http_post(url, xml)
        return response
        
    def get_categories(self, cat_id = None):
        if cat_id is not None:
            url = "/categories/{}.json".format(cat_id)
            schema_uri = '{http://www.ebayclassifiedsgroup.com/schema/category/v1}category'
        else:
            url = "/categories.json"
            schema_uri = '{http://www.ebayclassifiedsgroup.com/schema/category/v1}categories'

        response = self._http_get(url)
        response_json = json.loads(response.content.decode('utf-8'))
        categories = response_json.get(schema_uri, {}).get('value', {}).get('category', None)

        return categories

    def get_category_attributes(self, cat_id = None):

        url = "/attributes/metadata/{}.json".format(cat_id)
        schema_uri = '{http://www.ebayclassifiedsgroup.com/schema/attribute/v1}attributes'

        response = self._http_get(url)
        response_json = json.loads(response.content.decode('utf-8'))
        cat_attr = response_json.get(schema_uri, {}).get('value', {}).get('attribute', None)

        return cat_attr

    def get_locations(self, url_suffix, depth = None, include_parent_path = False):
        url = "/locations.json?{}".format(url_suffix)
        if depth is not None:
            url += '&depth={}'.format(depth)

        if include_parent_path is True:
            url += '&includeParentPath=true'

        schema_uri = '{http://www.ebayclassifiedsgroup.com/schema/location/v1}locations'

        response = self._http_get(url)
        response_json = json.loads(response.content.decode('utf-8'))
        categories = response_json.get(schema_uri, {}).get('value', {}).get('location', None)

        return categories

    def get_location_by_name(self, location_name, depth = None, include_parent_path = False):
        url_suffix = "q={}".format(location_name)
        locations = self.get_locations(url_suffix, depth, include_parent_path)
        return locations

    def get_location_by_coordinates(self, latitude, longitude, depth = None, include_parent_path = False):
        url_suffix = "latitude={}&longitude={}".format(latitude,longitude)
        locations = self.get_locations(url_suffix, depth, include_parent_path)
        return locations

    def html_unescape(self, data):
        return unescape(data)

