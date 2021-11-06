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

import base64
import hashlib
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


class EbkClient:
    H_EBAYK_CLIENT_APP = '13a6dde3-935d-4cd8-9992-db8a8c4b6c0f1456515662229'
    H_EBAYK_CLIENT_VERSION = '13.4.2'
    H_EBAYK_CLIENT_TYPE = 'ebayk-android-app-13.4.2'
    H_EBAYK_CLIENT_UA = 'Dalvik/2.2.0'
    H_EBAYK_WENKSE_SESSION_ID = 'asd'

    URL_PREFIX = 'https://api.ebay-kleinanzeigen.de/api'

    username = None

    def __init__(self, app_username, app_password, user_username, user_password):
        self.username = user_username
        app_auth = base64.b64encode(f'{app_username}:{app_password}'.encode('ascii')).decode("utf-8")

        hashed_user_password = base64.b64encode(hashlib.sha1(user_password.encode('ascii')).digest()).decode("utf-8")
        user_auth = f'email="{user_username}",password="{hashed_user_password}"'

        header = {
            'X-EBAYK-APP': self.H_EBAYK_CLIENT_APP,
            'X-ECG-USER-VERSION': self.H_EBAYK_CLIENT_VERSION,
            'X-ECG-USER-AGENT': self.H_EBAYK_CLIENT_TYPE,
            'Authorization': 'Basic {}'.format(app_auth),
            'X-ECG-Authorization-User': user_auth,
            'X-EBAYK-WENKSE-SESSION-ID': self.H_EBAYK_WENKSE_SESSION_ID,
            'User-Agent': self.H_EBAYK_CLIENT_UA,
        }

        self._session = requests.session()
        self._session.headers.update(header)
        
        session_token = self._http_get('/users/login').headers.get('X-EBAYK-TOKEN')
        user_auth_with_token = f'email="{user_username}",token="{session_token}"'
        header.update({
            'X-ECG-Authorization-User': user_auth_with_token,
        })
        self._session.headers.update(header)

    def _validate_http_response(self, r):
        if r.status_code < 400:
            return

        print("Error response body:\n" + r.content.decode('utf-8'))

        if r.status_code == 401:
            raise AttributeError(f'Access Denied {r.status_code}')
        elif r.status_code == 404:
            raise FileNotFoundError(f'Not found {r.status_code}')
        elif r.status_code >= 500:
            raise SystemError(f'Server Error {r.status_code}')

        raise AttributeError(f'Client error {r.status_code}')

    def _http_get(self, url_suffix):
        response = self._session.get(self.URL_PREFIX + url_suffix)
        self._validate_http_response(response)
        return response

    def _http_post(self, url_suffix, post_data='', **kwargs):
        response = self._session.post(self.URL_PREFIX + url_suffix, data=post_data,
                                      headers={'Content-Type': 'application/xml'},
                                      **kwargs)
        self._validate_http_response(response)
        return response

    def _http_post_files(self, url_suffix, files):
        response = self._session.post(self.URL_PREFIX + url_suffix, files=files)
        self._validate_http_response(response)
        return response

    def _http_put(self, url_suffix, post_data=''):
        response = self._session.put(self.URL_PREFIX + url_suffix, data=post_data,
                                     headers={'Content-Type': 'application/xml'})
        self._validate_http_response(response)
        return response

    def _http_delete(self, url_suffix):
        response = self._session.delete(self.URL_PREFIX + url_suffix)
        self._validate_http_response(response)
        return response

    def __http_get_body(self, url):
        return self._http_get(url).content.decode('utf-8')

    def __get_json_content(self, response, api_v2: bool = False):
        data = response.json()

        if not api_v2:
            schema_key = [k for k in data.keys() if k.startswith('{http')][0]
            data = data[schema_key]['value']

        return data

    def __http_get_json_content(self, url):
        api_v2 = url.startswith('/v2/')

        return self.__get_json_content(self._http_get(url), api_v2=api_v2)

    def __change_ad_status(self, ad_id, status):
        if status not in ['active', 'paused']:
            raise Exception('Wrong ad status')

        url = "/users/{}/ads/{}/{}.json".format(self.username, status, ad_id)
        response = self._http_put(url)

        if response.status_code == 204:
            return True
        else:
            return False

    def get_my_ads(self):
        url = f'/users/{self.username}/ads.json?_in=id,title,start-date-time,ad-status'
        return self.__http_get_json_content(url).get('ad', None)

    def get_ad(self, id):
        url = f'/ads/{id}.json'
        return self.__http_get_json_content(url)

    def get_ad_xml(self, id):
        url = f'/ads/{id}'
        return self.__http_get_body(url)

    def activate_ad(self, ad_id):
        return self.__change_ad_status(ad_id, 'active')

    def deactivate_ad(self, ad_id):
        return self.__change_ad_status(ad_id, 'paused')

    def delete_ad(self, ad_id):
        url = f'/users/{self.username}/ads/{ad_id}'
        response = self._http_delete(url)

        if response.status_code == 204:
            return True
        else:
            return False

    def create_ad(self, xml):
        url = f'/users/{self.username}/ads.json'
        return self._http_post(url, xml.encode('utf-8'))

    def get_categories(self, cat_id=None):
        if cat_id is not None:
            url = f'/categories/{cat_id}.json'
        else:
            url = '/categories.json'
        return self.__http_get_json_content(url).get('category', None)

    def get_category_attributes(self, cat_id=None):
        url = f'/attributes/metadata/{cat_id}.json'
        return self.__http_get_json_content(url).get('attribute', None)

    def get_category_metadata(self, cat_id=None):
        url = f'/ads/metadata/{cat_id}.json'
        return self.__http_get_json_content(url)

    def get_locations(self, url_suffix, depth=None, include_parent_path=False):
        url = f'/locations.json?{url_suffix}'
        if depth is not None:
            url += f'&depth={depth}'

        if include_parent_path is True:
            url += '&includeParentPath=true'

        return self.__http_get_json_content(url).get('location', None)

    def get_location_by_name(self, location_name, depth=None, include_parent_path=False):
        url_suffix = f'q={location_name}'
        return self.get_locations(url_suffix, depth, include_parent_path)

    def get_location_by_coordinates(self, latitude, longitude, depth=None, include_parent_path=False):
        url_suffix = f'latitude={latitude}&longitude={longitude}'
        return self.get_locations(url_suffix, depth, include_parent_path)

    def upload_picture(self, filename, data):
        return self.__get_json_content(self._http_post_files('/pictures.json', {'file': (filename, data)}))

    def get_view_count(self, id: int):
        """
        Retrieves the view count.

        :param id: Ad ID.
        :type id: int
        :return: How many impressions this add has.
        :rtype: int
        """
        url = f'/v2/counters/ads/vip/{id}.json'

        return self.__http_get_json_content(url)['value']

    def get_watchlist_count(self, id: int):
        """
        Retrieves the watchlist count.

        :param id: Ad ID.
        :type id: int
        :return: How many users have put this ad to their watchlist.
        :rtype: int
        """
        url = f'/v2/counters/ads/watchlist?adIds={id}'

        return self.__http_get_json_content(url)['counters'][0]['value']
