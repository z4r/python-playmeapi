""" This module contains tha base classes for the playMe API generated content:

* :py:class:`playme.artist.Artist`
* :py:class:`playme.album.Album`
* :py:class:`playme.track.Track`
"""
import playme
__license__, __author__ = playme.__license__, playme.__author__

from playme import core
from playme.api import artist, album, track

def str_keys(d):
    if not isinstance(d, dict):
        d = dict(d)
    return dict([(str(k),v) for k,v in d.items()])


class Item(dict):
    """ This is the base class for every entity in playMe package.
    >>> a = Item(a=1, b=2)
    >>> a
    Item(a = 1, b = 2)
    >>> b = Item(b=2, a=1)
    >>> a == b
    True
    """
    api_method = None
    label = None

    def __init__(self, **kwargs):
        if self.label in kwargs:
            kw = str_keys(kwargs[self.label])
            del kwargs[self.label]
            for k,v in kwargs.items():
                try:
                    kw[k] = LABEL2CLS[k](*v[LABEL2CLS[k].item_type.label])
                except KeyError:
                    pass
            kwargs = kw
        self.update(**kwargs)

    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join(['%s = %r' % (k, v) for k, v in self.iteritems()])
        )

    def __hash__(self):
        return hash(repr(self))

    @classmethod
    def request(cls, **kwargs):
        """
        >>> Item.request(a=1, b=2)
        Traceback (most recent call last):
            ...
        NotImplementedError: Item.api_method
        """
        try:
            response = cls.api_method(**kwargs)
        except TypeError:
            raise NotImplementedError(cls.__name__ + '.api_method')
        if not response.status:
            raise core.Error(str(response.status))
        return cls(**str_keys(response))


class ItemsCollection(tuple):
    """ This is the base class for collections of items, like search results, or
    playlist. It behaves like :py:class:`tuple`, but enforce new items to be
    instance of appropriate class checking against :py:attr:`item_type`.
    >>> ItemsCollection('a',1,[('a',1), ('b',2)], {u'a':3,u'b':4}, Item(a=5,b=6))
    ItemsCollection(Item(a = 1, b = 2), Item(a = 3, b = 4), Item(a = 5, b = 6))
    """
    item_type = Item
    label = None

    def __new__(cls, *args):
        casted = list()
        for item in args:
            if not isinstance(item, cls.item_type):
                try:
                    item = cls.item_type(**str_keys(item))
                except (ValueError, TypeError, AttributeError) as e:
                    item = None
            if item and item not in casted:
                casted.append(item)
        return tuple.__new__(cls, casted)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ', '.join(repr(i) for i in self))

    def __getslice__(self, i=0, j=-1):
        """ Return a Collection's slice
        >>> ic = ItemsCollection({'a':1,'b':2}, {'a':3,'b':4})
        >>> ic[1:]
        ItemsCollection(Item(a = 3, b = 4))
        """
        return type(self)(*self.__getitem__(slice(i,j)))

    def __getitem__(self, index):
        """ Return an item or a Collection's slice
        >>> ic = ItemsCollection({'a':1,'b':2}, {'a':3,'b':4})
        >>> ic[0]
        Item(a = 1, b = 2)
        >>> ic[slice(1,3)]
        ItemsCollection(Item(a = 3, b = 4))
        """
        if type(index) is int:
            return tuple.__getitem__(self, index)
        elif  type(index) is slice:
            return type(self)(*tuple.__getitem__(self, index))
        else:
            raise TypeError, type(index)

    @classmethod
    def request(cls, method, **kwargs):
        """ Returns an object instance after an API call
        """
        return cls.fromResponseMessage(method(**kwargs))

    @classmethod
    def fromResponseMessage(cls, response):
        """ Returns an object instance, built on a :py:class:`playme.core.Response`
        """
        if not response.status:
            raise core.Error(str(response.status))
        return cls(*[i for i in response[cls.label]])


class Artist(Item):
    api_method = artist.get
    label = 'artist'


class Artists(ItemsCollection):
    item_type = Artist
    label = 'artists'

    @classmethod
    def searchByName(cls, **kwargs):
        return cls.request(artist.searchByName, **kwargs)


class Album(Item):
    api_method = album.get
    label = 'album'


class Albums(ItemsCollection):
    item_type = Album
    label = 'albums'


class Track(Item):
    api_method = track.get
    label = 'track'


class Tracks(ItemsCollection):
    item_type = Track
    label = 'tracks'


ENTITIES = (Artist, Artists, Album, Albums, Track, Tracks)
CLS2LABEL = dict([(e, e.label) for e in ENTITIES])
LABEL2CLS = dict([(v,k) for k,v in CLS2LABEL.items()])


