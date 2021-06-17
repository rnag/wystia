=================
Wistia API Helper
=================


.. image:: https://img.shields.io/pypi/v/wystia.svg
        :target: https://pypi.org/project/wystia/

.. image:: https://img.shields.io/pypi/l/wystia.svg
        :target: https://pypi.org/project/wystia/

.. image:: https://img.shields.io/pypi/pyversions/wystia.svg
        :target: https://pypi.org/project/wystia

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

Sample usage with the `Data API <https://wistia.com/support/developers/data-api>`_:

.. code-block:: python3

    from wystia import WistiaDataApi
    from wystia.models import SortBy, LanguageCode, VideoData

    # Retrieve a list of all projects in the Wistia account,
    # sorted A-Z and in ascending order.
    projects = WistiaDataApi.list_all_projects(SortBy.NAME)
    project_ids = [p['hashedId'] for p in projects]

    # Retrieve a list of videos for a Wistia project.
    # Note: If you don't require asset info (such as ADs) on each
    #   video, I suggest calling `list_project` instead.
    videos = WistiaDataApi.list_videos('project-id')

    # Retrieve info on a particular video
    video_dict = WistiaDataApi.get_video('video-id')
    vd = VideoData(**video_dict)
    print(vd)

    # Update attributes on a media (video), or set a custom thumbnail on the video.
    WistiaDataApi.update_video(
        'video-id', thumbnail_media_id='uploaded-thumbnail-id')

    # Get aggregated stats for a video, such as view count
    stats = WistiaDataApi.get_stats_for_video('video-id')

    # Retrieve the customization data for a video
    customizations = WistiaDataApi.get_customizations('video-id')

    # Update only specific customizations for a video
    # Note the embed options are documented here:
    #   https://wistia.com/support/developers/embed-options
    WistiaDataApi.update_customizations('video-id',
                                        {'playerColor': '#e7fad1',
                                         # Hide comments on the media page
                                         'private': {'show_comments': 'false'}})

    # Get the Spanish captions on a video
    WistiaDataApi.get_captions('video-id', LanguageCode.SPANISH)

    # Add (or replace) the English captions on a video
    WistiaDataApi.update_captions('video-id', LanguageCode.ENGLISH,
                                  srt_file='path/to/file.srt')


... or to upload media via the `Upload API <https://wistia.com/support/developers/upload-api>`_:

.. code-block:: python3

    from wystia import WistiaUploadApi

    # Upload a file to a (default) project on Wistia
    r = WistiaUploadApi.upload_file('path/to/my-file.mp4')
    # Check if the video was successfully uploaded
    # assert r.created
    # assert r.name == 'my-file.mp4'

    # Uploads with a public link to a video, such as
    # an S3 pre-signed url.
    r = WistiaUploadApi.upload_link('my-s3-link',
                                    title='My Video Name',
                                    description='My Description')

... you can alternatively retrieve asset info via the public Media Embed link:

.. code-block:: python3

    from wystia import WistiaEmbedApi

    # Get the media embed data
    embed_data = WistiaEmbedApi.get_data('video-id')

    # Retrieve the source URL of the original media
    source_url = WistiaEmbedApi.asset_url(media_data=embed_data)

... when using the *Data API*, the ``WistiaHelper`` can help to further simplify some calls:

.. code-block:: python3

    from wystia import WistiaHelper

    # Check if the video exists in your Wistia account
    assert WistiaHelper.video_exists('abc1234567')

    # Check if a video's name indicates the video is an archived copy of an
    # existing video, as discussed in the below article on replacing a media:
    #   https://wistia.com/learn/product-updates/improved-library-management-tools
    assert WistiaHelper.is_archived_video(
        'My Title [Archived on August 13, 2015]')

    # Update the player color on a video
    WistiaHelper.customize_video_on_wistia('video-id', 'ffffcc')

    # Individually enable captions / AD in the player for a video
    WistiaHelper.enable_ad('video-id')
    WistiaHelper.enable_captions('video-id', on_by_default=False)

    # Disable captions / AD in the player for a video
    if WistiaHelper.has_captions_enabled('video-id'):
        print('Disabling captions and AD for the video')
        WistiaHelper.disable_captions_and_ad('video-id')


Installing Wystia and Supported Versions
----------------------------------------
The Wystia (Wistia helper) library is available on PyPI:

.. code-block:: shell

    $ python -m pip install wystia

The ``wystia`` library officially supports **Python 3.7** or higher.


Getting Started
---------------

Using the methods on the API classes assume your Wistia API token
has previously been configured, for example via the environment. The API token will
then be used globally by all the API classes when making requests to the Wistia API.

You can set the following environment variable with your API token:

* ``WISTIA_API_TOKEN``

Another option is to use the global ``configure`` method as shown below:

.. code-block:: python3

    WistiaDataApi.configure('MY-API-TOKEN')


Data API
--------

The wrapper class ``WistiaDataApi`` interacts with the Wistia Data API (docs below):

- https://wistia.com/support/developers/data-api


It fully implements the following sections in the API documentation:

    - Paging and Sorting Responses
    - Projects
    - Medias
    - Customizations
    - Captions

The following sections in the API have *not* been implemented (mainly as I haven't used them before):

    - Project Sharings
    - Account


Tips
~~~~

If you need to retrieve info on videos in a project and you
don't need complete info such as a list of assets for the video,
I recommend using ``list_project`` instead of ``list_videos``. This is because
the `Projects#show <https://wistia.com/support/developers/data-api#projects_show>`_
API returns up to 500 results per request, whereas the ``Medias#list``
only returns the default 100 results per page.

Assuming a project in your Wistia account has a total of about 250 media, here is the number of API
calls you might expect from each individual approach:

.. code-block:: python3

    from wystia import WistiaDataApi

    videos = WistiaDataApi.list_videos('project-id')
    assert WistiaDataApi.request_count() == 3

    # Resets request count for the next call
    WistiaDataApi.reset_request_count()

    videos = WistiaDataApi.list_project('project-id')
    assert WistiaDataApi.request_count() == 1


Thread Safety
-------------

The Wistia API classes are completely thread safe, since ``requests.Session``
objects are not re-used between API calls.

This means that if you have two (un-related) API operations to perform,
such as updating a video's title and adding captions on the video,
then you can certainly run those calls in parallel so that
they complete a bit faster.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
