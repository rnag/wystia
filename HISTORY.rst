=======
History
=======

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
