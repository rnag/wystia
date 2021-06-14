=================
Wistia API Helper
=================


.. image:: https://img.shields.io/pypi/v/wystia.svg
        :target: https://pypi.python.org/pypi/wystia

.. image:: https://img.shields.io/travis/rnag/wystia.svg
        :target: https://travis-ci.com/rnag/wystia

.. image:: https://readthedocs.org/projects/wystia/badge/?version=latest
        :target: https://wystia.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/rnag/wystia/shield.svg
     :target: https://pyup.io/repos/github/rnag/wystia/
     :alt: Updates



A Python wrapper library for the Wistia API


* Free software: MIT license
* Documentation: https://wystia.readthedocs.io.
* Wistia Developer Docs: https://wistia.com/support/developers.


Usage
-----

Some example usage below; more complete docs upcoming.


.. code-block:: python3

    from wystia import WistiaDataApi, WistiaUploadApi, WistiaEmbedApi
    from wystia.models import VideoData

    # Assuming you haven't set this via the environment variable
    for cls in WistiaDataApi, WistiaUploadApi:
        cls.configure('MY-API-TOKEN')
    # List videos in a project (allows up to 500 results per request)
    videos = WistiaDataApi.list_project('my-project-id')
    # List details on a Wistia video
    video_dict = WistiaDataApi.get_video('my-video-id')
    vd = VideoData(**video_dict)
    print(vd)
    # Upload a file to a (default) project on Wistia
    WistiaUploadApi.upload_file('path/to/path')
    # Uploads with a public link to a video, such as
    # an S3 pre-signed url.
    WistiaUploadApi.upload_link('my-s3-link')

Installing Wystia and Supported Versions
----------------------------------------
The Wystia (Wistia helper) library is available on PyPI:

.. code-block:: shell

    $ python -m pip install wystia

The ``wystia`` library officially supports **Python 3.7** or higher.

About
-----

I recommend reading the documentation in the source code
for important HOW-TO's and info on what each helper function is doing.

I'll need to write some kind of documentation eventually, but that's still pending for now.

At a minimum I recommend setting this environment variable:

* ``WISTIA_API_TOKEN`` - API Token to use for requests to the Wistia API


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
