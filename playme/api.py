"""
This is an utility module that provides a raw playMe web API interface.

It helps to hide :py:class:`playme.core.Method` transforming:

>>> from playme.core import Method
>>> try:
...     albums = Method('artist').getAlbums(artistCode=421, country='us')
... except playme.core.Error, e:
...     pass

into:

>>> from playme.api import artist
>>> import playme.core
>>> try:
...     albums = artist.getAlbums(artistCode=421, country='us')
... except playme.core.Error, e:
...     pass

From this module can be imported :py:attr:`artist`, :py:attr:`album`, :py:attr:`track` and :py:attr:`genre`
"""
import playme
__license__, __author__ = playme.__license__, playme.__author__

from playme.core import Method

artist = Method('artist')
album = Method('album')
track = Method('track')
genre = Method('genre')
