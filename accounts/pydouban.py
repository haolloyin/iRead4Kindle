#-*- coding: utf-8 -*-
"""
pydouban

A lightweight douban api library.

Basic Usage:
    >>> import pydouban
    >>> key = 'your douban oauth consumer key'
    >>> secret = 'your douban oauth consumer secret'
    >>> auth = pydouban.Auth(key, secret)
    >>> dic = auth.login()
    >>> print dic['url']
    ...
    >>> token_qs = auth.get_acs_token(dic['oauth_token'],dic['oauth_token_secret'])

    >>> api = pydouban.Api()
    >>> print api.search_people('ahbei')
    >>> api.set_qs_oauth(key, secret, qs)
    >>> print api.get_profile()
"""

'''
The BSD License

Copyright (c) 2010, Marvour <marvour@gmail.com>
All rights reserved.

Modified by mitnk <whgking@gmail.com>
Copyright (c) 2011 mitnk
'''

__version__ = '1.0.0'
__author__ = 'Marvour <marvour@gmail.com>'
__website__ = 'http://i.shiao.org/a/pydouban'

import hmac
import urllib
import httplib
from hashlib import sha1
from random import getrandbits
from time import time
from cgi import escape

try:
    import json # Python >= 2.6
except ImportError:
    try:
        import simplejson as json # Python < 2.6
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError

AUTH_URL = 'http://www.douban.com/service/auth'
API_URL = 'http://api.douban.com'

class Auth(object):
    """
    Easy OAuth for Douban.
    >>> auth = pydouban.Auth(key, secret)
    >>> print auth.login()

    more information on http://www.douban.com/service/apidoc/auth
    """
    _token = ''
    _token_secret = ''
    def __init__(self, key='', secret=''):
        if key:
            self._key = key
        if secret:
            self._secret = secret

    def set_consumer(self, key, secret):
        self._key = key
        self._secret = secret

    def set_token(self, token, token_secret):
        self._token = token
        self._token_secret = token_secret

    def set_qs_token(self, qs):
        dic = _qs2dict(qs)
        self._token = dic['oauth_token']
        self._token_secret = dic['oauth_token_secret']

    def get_oauth_params(self, url, params, method='GET'):
        assert hasattr(self, '_key'), "need consumer key."
        assert hasattr(self, '_secret'), "need consumer secret."
        oauth_params = {
            'oauth_consumer_key': self._key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': int(time()),
            'oauth_nonce': getrandbits(64),
            'oauth_version': '1.0'}
        if self._token:
            oauth_params['oauth_token'] = self._token

        # Add other params
        params.update(oauth_params)

        # Sort and concat
        s = ''
        for k in sorted(params):
            s += _quote(k) + '=' + _quote(params[k]) + '&'
            msg = method + '&' + _quote(url) + '&' + _quote(s[:-1])
        # Maybe token_secret is empty
        key = self._secret + '&' + self._token_secret

        digest = hmac.new(key, msg, sha1).digest()
        params['oauth_signature'] = digest.encode('base64')[:-1]

        return params
    
    def login(self, callback=None):
        req_token_url = AUTH_URL + '/request_token'
        params = self.get_oauth_params(req_token_url, {}) 
        res = urllib.urlopen(url=req_token_url + '?' + _dict2qs(params))
        if 200 != res.code:
            raise Exception('OAuth Request Token Error: ' + res.read())
        dic = _qs2dict(res.read())
        self._token = dic['oauth_token']
        self._token_secret = dic['oauth_token_secret']
        sig_params = {'oauth_signature': params['oauth_signature']}
        dic['params'] = _dict2qs(self.get_oauth_params(req_token_url,sig_params))
        dic['url'] = AUTH_URL + '/authorize?' + dic['params']
        if callback:
            dic['url'] += '&' + _dict2qs({'oauth_callback':callback})
        return dic

    def get_acs_token(self, req_token, req_token_secret):
        acs_token_url = AUTH_URL + '/access_token'

        self._token = req_token
        self._token_secret = req_token_secret

        params = self.get_oauth_params(acs_token_url, {})
        res = urllib.urlopen(url=acs_token_url + '?' + _dict2qs(params))
        if 200 != res.code:
            raise Exception('OAuth Access Token Error: ' + res.read())
        return res.read() # qs

class Api(object):
    """
    Douban API Service
    Documentation on http://i.shiao.org/a/pydouban

    more information on http://www.douban.com/service/apidoc/reference/
    """
    def __init__(self, alt='json', start_index=1, max_results=10, skip_read=True):
        if alt in ('atom', 'xml'):
            self._alt = 'atom'
        else:
            self._alt = 'json'
        self._start = start_index
        self._max = max_results
        self._skip = skip_read

    def set_var(self, start_index, max_results):
        self._start = start_index
        self._max = max_results

    def set_key(self, key):
        self._key = key

    def set_oauth(self, key, secret, acs_token, acs_token_secret):
        self._oauth = Auth(key, secret)
        self._oauth.set_token(acs_token, acs_token_secret)

    def set_qs_oauth(self, key, secret, qs):
        self._oauth = Auth(key, secret)
        self._oauth.set_qs_token(qs)
    
    #{{{ method

    def _post(self, path, body, params={}):
        assert hasattr(self, '_oauth'), "need be authed."
        res_url = API_URL + path
        dic = self._oauth.get_oauth_params(res_url, params, 'POST')
        headers = _dict2header(dic)
        headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        
        con = httplib.HTTPConnection('api.douban.com', 80)
        con.request('POST', path, body, headers)
        res = con.getresponse()
        if 201 != res.status:
            raise Exception('Douban Post Error : ' + str(res.status))
        if self._skip:
            return True
        return res.read()

    def _put(self, path, body, params={}):
        assert hasattr(self, '_oauth'), "need be authed."
        res_url = API_URL + path
        dic = self._oauth.get_oauth_params(res_url, params, 'PUT')
        headers = _dict2header(dic)
        headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        
        con = httplib.HTTPConnection('api.douban.com', 80)
        con.request('PUT', path, body, headers)
        res = con.getresponse()
        if 202 != res.status:
            raise Exception('Douban Put Error : ' + str(res.status))
        if self._skip:
            return True
        return res.read()

    def _del(self, path, params={}):
        assert hasattr(self, '_oauth'), "need be authed."
        res_url = API_URL + path
        dic = self._oauth.get_oauth_params(res_url, params, 'DELETE')
        headers = _dict2header(dic)

        con = httplib.HTTPConnection('api.douban.com', 80, timeout=5)
        con.request('DELETE', path, None, headers)
        res = con.getresponse()
        if 200 != res.status:
            raise Exception('Douban Delete Error : ' + str(res.status))
        if self._skip:
            return True
        return res.read()
    
    def _get_open(self, url):
        res = urllib.urlopen(url)
        if 200 != res.code:
            raise Exception('Douban Get Error : ' + str(res.code))
        if 'json' == self._alt:
            return _FormateData.render(res.read())
        return res.read()

    def _get(self, path, params={}):
        assert hasattr(self, '_oauth'), "need be authed."
        res_url = API_URL + path
        params.update({'alt': self._alt})
        dic = self._oauth.get_oauth_params(res_url, params, 'GET')
        url=res_url + '?' + _dict2qs(dic)
        return self._get_open(url)

    def _get_public(self, path, params={}):
        path += '?alt=' + self._alt
        if params:
            path += '&' + _dict2qs(params)
        if hasattr(self, '_key'):
            path += '&apikey=' + self._key
        url=API_URL+path
        return self._get_open(url)

    #}}}
    
    #{{{ public method, no need for oauth

    def get_people(self, userID):
        path = '/people/%s?alt=%s' % (userID, self._alt)
        if hasattr(self, '_key'):
            path = '/people/%s?alt=%s&apikey=%s' % (userID, self._alt, self._key)
        return self._get_open(API_URL+path)

    def _sq(self, q, tag=None, var='movie'):
        q = _escape(q)
        path = '/%s/subjects' % var
        dic = {'q':q, 'alt':self._alt,'start':self._start,'max':self._max}
        s = '?q=%(q)s&alt=%(alt)s&start-index=%(start)s&max-results=%(max)s'\
                % dic
        if tag:
            s += '&tag=' + tag
        if hasattr(self, '_key'):
            s += '&apikey=' + self._key
        return self._get_open(API_URL + path + s)
    def search_book(self, q, tag=None):
        return self._sq(q, tag, var='book')

    #}}}

    #{{{ resource (public and oauth)

    def get_book_byid(self, subjectID):
        path = '/book/subject/%s' % subjectID
        if hasattr(self, '_oauth'):
            return self._get(path)
        return self._get_public(path)
    def get_book_byisbn(self, isbnID):
        path = '/book/subject/isbn/%s' % isbnID
        if hasattr(self, '_oauth'):
            return self._get(path)
        return self._get_public(path)

    def get_book_tags(self, subjectID):
        path = '/book/subject/%s/tags' % subjectID
        params = {'start-index': self._start, 'max-results': self._max}
        return self._get_public(path, params)
    
    #}}}
    
    #{{{ user info

    def get_profile(self):
        """ get authed user's information"""
        path = '/people/%40me'
        return self._get(path)

    def get_friends(self):
        """ get authed user's friends"""
        path = '/people/%40me/friends'
        params = {'start-index': self._start, 'max-results': self._max}
        return self._get(path, params)

    def get_contacts(self):
        ''' get authed user's contacts'''
        path = '/people/%40me/contacts'
        params = {'start-index': self._start, 'max-results': self._max}
        return self._get(path, params)

    #}}}

    #{{{ collection
    # http://www.douban.com/service/apidoc/reference/collection

    def get_collections(self, cat, status=None, tag=None):
        if cat not in ('book','movie','music'):
            cat = 'book'
        path = '/people/%40me/collection'
        params = {'cat': cat, 'start-index': self._start, 'max-results': self._max}
        if tag:
            params.update({'tag':tag})
        if status:
            params.update({'status':status})
        return self._get(path, params)

    def get_collection(self, collectionID):
        path = '/collection/%s' % collectionID
        return self._get(path)

    def _collection_atom(self, sourceURL, status, rating, tags, comment, privacy):
        if int(rating) > 5:
            rating = 5
        elif int(rating) < 0:
            rating = 0
        if not isinstance(tags, list):
            raise TypeError
        if privacy not in ('public', 'private'):
            privacy = 'public'
        atom = _atom_db_header
        atom += '<db:status>' + status + '</db:status>'
        for tag in tags:
            atom += '<db:tag name="%s" />' % _escape(tag)
        atom += '<gd:rating xmlns:gd="http://schemas.google.com/g/2005" value="%s" />' % rating
        atom += '<content>%s</content>' % _escape(comment)
        atom += '<db:subject><id>%s</id></db:subject>' % sourceURL
        atom += '<db:attribute name="privacy">%s</db:attribute></entry>' % privacy
        return atom

    #}}}

    #{{{ review
    # http://www.douban.com/service/apidoc/reference/review

    def get_review(self, reviewID):
        path = '/review/%s' % reviewID
        if hasattr(self, '_oauth'):
            return self._get(path)
        return self._get_public(path)
    def _get_subject_reviews(self, path):
        params = {'start-index': self._start, 'max-results': self._max}
        if hasattr(self, '_oauth'):
            return self._get(path, params)
        return self._get_public(path, params)
    def get_book_reviews_byid(self, subjectID):
        path = '/book/subject/%s/reviews' % subjectID
        return self._get_subject_reviews(path)

    def post_review(self, sourceURL, title, rating, content):
        path = '/reviews'
        if int(rating) > 5:
            rating = 5
        elif int(rating) < 0:
            rating = 0
        atom = _atom_db_header
        atom += '<db:subject xmlns:db="http://www.douban.com/xmlns/"><id>%s</id></db:subject>' % sourceURL
        atom += '<content>%s</content>' % _escape(content)
        atom += '<gd:rating xmlns:gd="http://schemas.google.com/g/2005" value="%s" />' % rating
        atom += '<title>%s</title></entry>' % _escape(title)
        return self._post(path, atom)
    def update_review(self, reviewID, sourceURL, title, rating, content):
        path = '/review/%s' % reviewID
        if int(rating) > 5:
            rating = 5
        elif int(rating) < 0:
            rating = 0
        atom = _atom_db_header
        atom += '<db:subject xmlns:db="http://www.douban.com/xmlns/"><id>%s</id></db:subject>' % sourceURL
        atom += '<content>%s</content>' % _escape(content)
        atom += '<gd:rating xmlns:gd="http://schemas.google.com/g/2005" value="%s" />' % rating
        atom += '<title>%s</title></entry>' % _escape(title)
        return self._put(path, atom)
    def del_review(self, reviewID):
        path = '/review/%s' % reviewID
        return self._del(path)
    #}}}

def _escape(s):
    try: s = s.encode('utf-8')
    except UnicodeDecodeError: pass
    return escape(s)

def _quote(s):
    return urllib.quote(str(s), '~')

def _qs2dict(s):
    dic = {} 
    for param in s.split('&'):
        (key, value) = param.split('=')
        dic[key] = value
    return dic

def _dict2qs(dic):
    return '&'.join(['%s=%s' % (key, _quote(value)) for key, value in dic.iteritems()]) 

def _dict2header(dic):
    s = ', '.join(['%s="%s"' % (k, _quote(v)) for k, v in dic.iteritems() if k.startswith('oauth_')]) 
    auth_header = 'OAuth realm="", %s' % s
    return {'Authorization': auth_header}

_atom_db_header = '''
<?xml version="1.0" encoding="UTF-8"?><entry xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:db="http://www.douban.com/xmlns/">
'''
_atom_sq_header = '''
<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:db="http://www.douban.com/xmlns/" xmlns:gd="http://schemas.google.com/g/2005" xmlns:opensearch="http://a9.com/-/spec/opensearchrss/1.0/">
'''
class _FormateData(dict):
    """
    Copy from web.utils.Stroage
    """
    @classmethod
    def _json_dic(cls, dic):
        store = cls()
        for key in dic.keys():
            value = dic[key]
            if isinstance(value, dict):
                value = cls._json_dic(value)
            elif isinstance(dic[key], list):
                value = [cls._json_dic(subdic) for subdic in dic[key]]
            if key.startswith('db:'):
                key = key.replace('db:','')
            elif key.startswith('gd:'):
                key = key.replace('gd:','')
            elif key.startswith('opensearch:'):
                key = key.replace('opensearch:', '')
            elif key.startswith('openSearch:'):
                key = key.replace('openSearch:', '')
            elif key.startswith('$'):
                key = key.replace('$','')
            elif key.startswith('@'):
                key = key.replace('@','')
            store[key] = value
        return store

    @classmethod
    def render(cls, s):
        dic = json.loads(s)
        return cls._json_dic(dic)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return dict.__repr__(self)

