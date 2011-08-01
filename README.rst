Python interface to playMe API
==============================

This package provides a module to interface with the playMe_  API.

It's inspired to `musiXmatch API`_ developed by `Luca De Vitis`_ .
[Thx to share your code.]

.. _playMe: http://www.dada.it
.. _`musiXmatch API`: https://github.com/monkeython/musixmatch/tree/master/python-musixmatch
.. _`Luca De Vitis`: https://github.com/monkeython

Let's playMe!
=============

1. This documentation is not able to go beyond http://lab.playme.com/api_overview .
2. You'll need an api key, so keep one at http://lab.playme.com/user/register .
3. Install the package
4. Open a shell and type

>>> import playme
>>> apikey = '<your-apikey>'
>>> country= '<coutry-catalogue>'
>>> try:
...     #a = playme.api.artist.searchByName(apikey=apikey,country=country,query='Metallica')
...     a = playme.api.artist.get(apikey=apikey,country=country,artistCode=1073)
... except playme.core.Error as e:
...     pass


Building / Installing
=====================

You can just use setup.py to build and install python-playme::

   prompt $ python setup.py bdist_egg

Once built, you can use easy_install on the python egg.

Documentation
=============
Generate your own local copy using `Sphinx`_ trough the setup.py::

   prompt $ python setup.py build_sphinx

.. _Sphinx: http://sphinx.pocoo.org