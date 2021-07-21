=======
History
=======

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
