# -*- coding: utf-8 -*-

import re

try:
    import json
except ImportError:
    import simplejson as json

import logging
from urllib import unquote

import requests

logger = logging.getLogger(__name__)

API_URL = 'https://api.bitport.io/v2'

class Client(object):

    def __init__(self, access_token):
        # The url containing the access_token may be copied
        parts = access_token.split('?code=')
        access_token = unquote(parts[len(parts) - 1])

        self.session = requests.session()
        self.session.headers.update({
            'Authorization': 'Bearer ' + access_token,
            'Accept': 'application/json'
        })

        self.File = type('File', (_File,), {'client': self})
        self.Directory = type('Directory', (_Directory,), {'client': self})

    def request(self, path, raw=False, **kwargs):
        url = API_URL + path
        logger.debug('url: %s', url)
        r = self.session.request(method='GET', url=url, **kwargs)
        logger.debug('response: %s', r)
        logger.debug('content: %s', r.content)

        if raw:
            return r
        try:
            r = json.loads(r.content)['data'][0]
        except:
            raise Exception('Server didn\'t send valid JSON:\n%s\n%s' % (r, r.content))

        return r


class _BaseResource(object):

    def __init__(self, resource_dict):
        '''Construct the object from a dict'''

        self.__dict__.update(resource_dict)

    def __str__(self):
        return self.name.encode('utf-8')


class _File(_BaseResource):

    @property
    def id(self): return self.code

    @classmethod
    def list(cls, parent_id=None):
        if not parent_id:
            d = cls.client.request('/cloud')
        else:
            d = cls.client.request('/cloud/' + parent_id)

        return [cls.client.File(f) for f in d['files']]\
               + [cls.client.Directory(f) for f in d['folders']]

    @property
    def stream_url(self):
        r = self.client.request('/files/%s/stream' % self.id, raw=True, allow_redirects=False)
        return r.headers['location']

    @classmethod
    def get(cls, id):
        return cls(cls.client.request('/files/' + id))


class _Directory(_File): pass
