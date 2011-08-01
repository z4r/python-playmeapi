========
Api Core
========

.. automodule:: playme.core
   :undoc-members:

Request Builder
===============

.. autoclass:: Request
    :members: response

.. autoclass:: Method
    :show-inheritance:

.. autoclass:: QueryString
    :members: __iter__, items, keys, values

Response
========

.. autoclass:: Response
    :members: status

.. autoclass:: ResponseStatus
    :show-inheritance:
    :members: success

Errors
======

.. autoexception:: Error
    :show-inheritance:

.. autoexception:: ResponseError
    :show-inheritance: