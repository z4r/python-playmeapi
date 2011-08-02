"""This module define the core API classes.
"""
import playme
__license__, __author__ = playme.__license__, playme.__author__

from urllib import urlencode
from urllib2 import urlopen, HTTPError
import json

class Error(Exception):
    """Base play.me API error.

    >>> import playme.core
    >>> try:
    ...     raise playme.core.Error(1,2,3)
    ... except playme.core.Error as e:
    ...     str(e)
    ...     repr(e)
    '1, 2, 3'
    'Error(1, 2, 3)'
    """
    def __str__(self):
        return ', '.join(map(str, self.args))

    def __repr__(self):
        name = self.__class__.__name__
        return '%s%r' % (name, self.args)


class ResponseError(Error):
    """Represents errors occurred while parsing the response messages."""


class ResponseStatus(int):
    """Represents response message status code. Casting a
    :py:class:`ResponseStatus` to :py:class:`str` returns the description
    associated with the status code:

    >>> from playme.core import ResponseStatus
    >>> str(ResponseStatus(200))
    'The request was successful'
    >>> str(ResponseStatus(14030))
    'Permission denied'

    The status code to description mapping is:

    +-------+----------------------------------------------------------+
    | Code  | Description                                              |
    +=======+==========================================================+
    |   200 | The request was successful                               |
    +-------+----------------------------------------------------------+
    |   402 | User not enabled to use this function                    |
    +-------+----------------------------------------------------------+
    | 10010 | Missing parameter                                        |
    +-------+----------------------------------------------------------+
    | 10020 | Invalid parameter                                        |
    +-------+----------------------------------------------------------+
    | 10040 | Too many parameters as primary key                       |
    +-------+----------------------------------------------------------+
    | 10050 | Too many mutual exclusive parameters                     |
    +-------+----------------------------------------------------------+
    | 10810 | Error while retrieving item data                         |
    +-------+----------------------------------------------------------+
    | 11000 | Authentication Failure                                   |
    +-------+----------------------------------------------------------+
    | 13000 | Item not found                                           |
    +-------+----------------------------------------------------------+
    | 13010 | Item already exists                                      |
    +-------+----------------------------------------------------------+
    | 13020 | User already unsubscribed                                |
    +-------+----------------------------------------------------------+
    | 13040 | Dependency item missing                                  |
    +-------+----------------------------------------------------------+
    | 13110 | Item not owned by the user associated to the UAT         |
    +-------+----------------------------------------------------------+
    | 14010 | Authorization failed                                     |
    +-------+----------------------------------------------------------+
    | 14011 | Missing user authentication token                        |
    |       | or authentication token not valid (possibly expired)     |
    +-------+----------------------------------------------------------+
    | 14030 | Permission denied                                        |
    +-------+----------------------------------------------------------+
    | 14031 | Invalid or missing apikey                                |
    +-------+----------------------------------------------------------+
    | 14032 | Blacklisted apikey                                       |
    +-------+----------------------------------------------------------+
    | 14033 | Unauthorized call                                        |
    +-------+----------------------------------------------------------+
    | 14034 | Temporarily blocked                                      |
    +-------+----------------------------------------------------------+
    | 14040 | API not found                                            |
    +-------+----------------------------------------------------------+
    | 16000 | Search engine error                                      |
    +-------+----------------------------------------------------------+
    | 20000 | DB error                                                 |
    +-------+----------------------------------------------------------+
    | 20010 | User already exists                                      |
    +-------+----------------------------------------------------------+
    | 21000 | Unable to assign credits                                 |
    +-------+----------------------------------------------------------+

    Casting a :py:class:`ResponseStatus` to :py:class:`bool` returns True
    if status code is 200, False otherwise:

    >>> from playme.core import ResponseStatus
    >>> bool(ResponseStatus(200))
    True
    >>> bool(ResponseStatus(14030))
    False
    """
    __status__ = {
        200 : 'The request was successful',
        402 : 'User not enabled to use this function',
        10010 : 'Missing parameter',
        10020 : 'Invalid parameter',
        10040 : 'Too many parameters as primary key',
        10050 : 'Too many mutual exclusive parameters',
        10810 : 'Error while retrieving item data',
        11000 : 'Authentication Failure',
        13000 : 'Item not found',
        13010 : 'Item already exists',
        13020 : 'User already unsubscribed',
        13040 : 'Dependency item missing',
        13110 : 'Item not owned by the user associated to the UAT',
        14010 : 'Authorization failed',
        14011 : 'Missing user authentication token or authentication token\
                  not valid (possibly expired)',
        14030 : 'Permission denied',
        14031 : 'Invalid or missing apikey',
        14032 : 'Blacklisted apikey',
        14033 : 'Unauthorized call',
        14034 : 'Temporarily blocked',
        14040 : 'API not found',
        16000 : 'Search engine error',
        20000 : 'DB error',
        20010 : 'User already exists',
        21000 : 'Unable to assign credits',
    }
    def __str__(self):
        return self.__status__.get(self, 'Unknown status code %i!' % self)

    def __repr__(self):
        return 'ResponseStatus(%i)' % self

    def __nonzero__(self):
        return self == 200

    @classmethod
    def success(cls):
        """Build a 'success' :py:class:`ResponseStatus`:

        >>> ResponseStatus.success()
        ResponseStatus(200)
        """
        return cls(200)

class Response(dict):
    """A :py:class:`dict` subclass to expose the json structure contained in
    the response message. It parses the json response message and build a
    proper python :py:class:`dict` containing the information retrived.
    Also, setup a :py:class:`ResponseStatus` by querying the :py:class:`dict`
    for the *['error']* item.

    >>> r = Response('''{"response" :{
    ... "api" : { "version" : "1.0.0" },
    ... "country" : { "available" : ["us"],"default" : ["us"]},
    ... "format" : { "available" : ["json", "xml"], "default" : ["xml"]}}
    ... }''')
    >>> r.status
    ResponseStatus(200)
    >>> r = Response('''{"response": {
    ... "error": { "code": "14030", "description": "Permission denied" }}
    ... }''')
    >>> r.status
    ResponseStatus(14030)
    >>> Response('spam')
    Traceback (most recent call last):
        ...
    ResponseError: Invalid Json response message.
    """
    def __init__(self, response):
        try:
            self.update(json.loads(response)['response'])
        except (ValueError, KeyError, TypeError):
            raise ResponseError(u'Invalid Json response message.')

    def __str__(self):
        s = json.dumps({ 'response': self }, sort_keys=True, indent=4)
        return '\n'.join([l.rstrip() for l in  s.splitlines()])

    @property
    def status(self):
        """It's the :py:class:`ResponseStatus` object representing the
        message status code."""
        try:
            error = self['error']
            return ResponseStatus(int(error['code']))
        except KeyError:
            return ResponseStatus.success()

    def __repr__(self):
        return '{0}(...)'.format(type(self).__name__)


class QueryString(dict):
    """A class representing the keyword arguments to be used in HTTP requests
    as query string. Takes a :py:class:`dict` of keywords, and encode values
    using utf-8. Also, the query string is sorted by keyword name, so that its
    string representation is always the same, thus can be used in hashes.

    Casting a :py:class:`QueryString` to :py:class:`str` returns the urlencoded
    query string:

    >>> from playme.core import QueryString
    >>> str(QueryString({ 'country': 'it', 'albumCode': 1 }))
    'albumCode=1&country=it'
    >>> str(QueryString(country='it', albumCode=1))
    'albumCode=1&country=it'

    Using :py:func:`repr` on :py:class:`QueryString` returns an evaluable
    representation of the current instance, excluding apikey value:

    >>> from playme.core import QueryString
    >>> repr(QueryString({ 'country': 'it', 'albumCode': 1, 'apikey': 'k'}))
    "QueryString({'country': 'it', 'albumCode': '1'})"
    >>> repr(QueryString(country='it', albumCode=1, apikey='k'))
    "QueryString({'country': 'it', 'albumCode': '1'})"
    """
    def __init__(self, items=None, **kwargs):
        items = items or dict()
        super(QueryString, self).__init__(items, **kwargs)
        for k in self:
            self[k] = str(self[k]).encode('utf-8')

    def __str__(self):
        return urlencode(self)

    def __repr__(self):
        query = self.copy()
        if 'apikey' in query: del query['apikey']
        return 'QueryString(%r)' % query

    def __iter__(self):
        """Returns an iterator method which will yield keys sorted by name.
        Sorting allow the query strings to be used (reasonably) as caching key.
        """
        keys = super(QueryString, self).keys()
        keys.sort()
        for key in keys:
            yield key

    def values(self):
        """Overloads :py:meth:`dict.values` using :py:meth:`__iter__`:

        >>> q = QueryString({ 'country': 'it', 'albumCode': 1, 'apikey': 'k'})
        >>> q.values()
        ('1', 'k', 'it')
        """
        return tuple(self[k] for k in self)

    def keys(self):
        """Overloads :py:meth:`dict.keys` using :py:meth:`__iter__`:

        >>> q = QueryString({ 'country': 'it', 'albumCode': 1, 'apikey': 'k'})
        >>> q.keys()
        ('albumCode', 'apikey', 'country')
        """
        return tuple(k for k in self)

    def items(self):
        """Overloads :py:meth:`dict.item` using :py:meth:`__iter__`:
        
        >>> q = QueryString({ 'country': 'it', 'albumCode': 1, 'apikey': 'k'})
        >>> q.items()
        (('albumCode', '1'), ('apikey', 'k'), ('country', 'it'))
        """
        return tuple((k, self[k]) for k in self)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))


class Request(object):
    """This is the main API class. Given a :py:class:`Method` or a method name,
    a :py:class:`QueryString` or a :py:class:`dict`, it can build the API query
    URL, performs the request and returns the :py:class:`Response`.

    If **method** is string, try to cast it into a :py:class:`Method`. If
    **query_string** is a :py:class:`dict`, try to cast it into a
    :py:class:`QueryString`. If **query_string** is not specified, try to
    use **kwargs** as a :py:class:`dict` and cast it into a
    :py:class:`QueryString`.

    >>> from playme.core import Request, Method, QueryString
    >>> method_name = 'album.get'
    >>> method = Method(method_name)
    >>> kwargs = {'country':'it', 'albumCode':'782378'}
    >>> query_string = QueryString(kwargs)
    >>> r1 = Request(method_name, kwargs)
    >>> r1
    Request(Method('album.get'), QueryString({'country': 'it', 'albumCode': '782378'}))
    >>> r2 = Request(method_name, **kwargs)
    >>> r3 = Request(method_name, query_string)
    >>> r4 = Request(method, kwargs)
    >>> r5 = Request(method, **kwargs)
    >>> r6 = Request(method, query_string)
    >>> r1 == r2 == r3 == r4 == r5 == r6
    True

    Turning the :py:class:`Request` into a :py:class:`str` returns the URL
    representing the API request:

    >>> str(Request('album.get', {'country':'it', 'albumCode':'782378'}))
    'http://api.playme.com/album.get?albumCode=782378&country=it'
    """
    def __init__ (self, api_method, query_string=None, **kwargs):
        query_string = query_string or dict()
        if not isinstance(query_string, QueryString):
            query_string = QueryString(query_string)
        if not isinstance(api_method, Method):
            api_method = Method(api_method)
        query_string.update(kwargs)
        self.method = api_method
        self.data = query_string
        self._response = None

    @property
    def response(self):
        """The :py:class:`Response`"""
        if not self._response:
            try:
                response = urlopen(str(self))
            except HTTPError as e:
                response = e
            self._response = Response(response.read())
        return self._response

    def __repr__(self):
        return 'Request(%r, %r)' % (self.method, self.data)

    def __str__(self):
        return 'http://api.playme.com/%s?%s' % (self.method, self.data)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))


class Method(str):
    """Utility class to build API methods name and call them as functions.

    :py:class:`Method` has custom attribute access to build method names like
    those specified in the API. Each attribute access builds a new Method with
    a new name.

    Calling a :py:class:`Method` as a function with positional arguments,
    builds a :py:class:`Request`, runs it and returns the result.
    It uses itself to determine the API method name and version, and the
    *kwargs* arguments for the query string.

    >>> import playme.core
    >>> album = playme.core.Method('album')
    >>> album.getTracks
    Method('album.getTracks')
    """
    def __getattribute__(self, name):
        if name.startswith('_'):
            return super(Method, self).__getattribute__(name)
        else:
            return Method('.'.join([self, name]))

    def __call__ (self, **query):
        query['format'] = 'json'
        return Request(self, query).response

    def __repr__(self):
        return "Method('%s')" % self