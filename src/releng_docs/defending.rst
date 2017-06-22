Defending Release Engineering Services Design
=============================================

Why everything in one repository?
---------------------------------

In an environment where there are many small and similar services it makes
sense to benefit the cost of maintaining and supporting these services.

Another reason is to improve developers discoverability of services
across the *Release Engineering Team*.

In longer term, once more services are migrated to ``mozilla-releng/services``,
a better overview of what is running, and how is it running, will be provided for
the management team to make better decisions going forward.


Why OpenAPI (Swagger) is used to declare JSON api?
--------------------------------------------------

The OpenAPI_ standard provides several immediate benefits to the project. Specifying the JSON API with Swagger enables
the use of the server-side Flask extension Connexion_. Connexion provides automatic verification and validation of
endpoints, ensuring the specification is indeed implemented correctly. Connexion also auto-generates the OpenAPI
interactive user interface for experimenting with the API, enabling greater discovery of service capabilities for new contributors
and faster iteration of errors when building client applications to interact with the services. Finally, OpenAPI
provides automatic client library generation tools. This means a new contributor who may be skilled in a language other
than Python can quickly generate a library and interact with the services smoothly.

.. _OpenAPI: http://swagger.io/specification/
.. _Connexion: https://github.com/zalando/connexion


Why Elm is used instead of any other Javascript frameworks? 
-----------------------------------------------------------

TODO

Why Nix is used as a building tool?
-----------------------------------

TODO
