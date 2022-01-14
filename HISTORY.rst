=======
History
=======

1.0.0 (2022-01-14)
------------------

**Breaking Changes**

* Wystia has officially dropped support for Python versions 3.5 and 3.6.
  The support for 3.6 needed to be dropped primarily because of the
  ``from __future__ import annotations`` usage in the code.
* Refactored all API helper classes to return model class objects as a result,
  rather than Python ``dict`` objects. In the case of any `list`- related API responses,
  we now return a ``Container`` object so that it can be easier to print or display
  the result for debugging purposes.
* All inputs to the API helper methods that previously accepted a ``dict`` object,
  have in general been refactored to accept a model dataclass instance as an input instead.
* Renamed some error classes; for example, ``NoSuchMedia`` instead of ``NoSuchVideo``.
* Renamed some model classes; for example, ``MediaStatus`` instead of ``VideoStatus``.

**Features and Improvements**

* Added ``WistiaApi`` to the list of public exports, which is aliased to the
  ``WistiaDataApi`` helper class.
* Added new methods to the ``WistiaDataApi`` class for more explicitly
  interacting with *medias* instead of *videos*. For example, a ``list_medias``
  method is added as an alternative to calling ``list_videos``.
* Refactored the CI process to use GitHub Workflows instead of Travis CI.
* Added *3.10* to the list of supported Python versions.
* Updated the project status from *Beta* to *Production/Stable*.
* Added an ``examples/`` folder in the project repo on GitHub, which
  contains Python scripts to demonstrate sample usage.
* Updated docs and added a new *Quickstart* section.

0.3.0 (2021-07-21)
------------------

**Features and Improvements**

* Add compatibility changes to extend support to Python 3.5 and 3.6
* WistiaHelper: Add method ``project_details`` to retrieve info on a particular Wistia project
* WistiaEmbedApi: Update to parse the ``.json`` response rather than the ``.jsonp`` version
* Makefile: Add new command ``init``, which can be used to install Dev dependencies for the project

  * Ensure the new command is compatible with Python 3.5, which has dependencies on separate
    package versions; here we should use ``requirements-py35-dev.txt`` instead.
* Makefile: Update ``coverage`` command to run unit tests by default

**Bugfixes**

* models.VideoData: The parameter to the ``process_captions`` method is now
  correctly type-annotated to accept a ``List`` of ``Dict``

0.2.1 (2021-06-17)
------------------

* WistiaHelper: Add method ``enable_captions_and_ad``
* Remove ``.format`` usage in log statements
* Remove an unnecessary method ``ad_needed`` from ``VideoData``
* Update readme and Sphinx ``docs/``

0.2.0 (2021-06-16)
------------------

* Fully implement all sections in the Wistia Data API
* Add more methods to the ``WistiaHelper`` class
* Request Count and API Token should now be globally shared by all API sub-classes
* Lot of code refactoring
* Exclude ``.mp4`` files from dist, to reduce total package size
* Add more test cases
* Update docs with better examples

0.1.0 (2021-06-12)
------------------

* First release on PyPI.
