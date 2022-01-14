=====
Usage
=====

To use Wistia API Helper in a project::

    from wystia import <API helper class>

Using the methods on the API classes assume your Wistia API token
has previously been configured, for example via the environment variable
``WISTIA_API_TOKEN``. The API token is then used globally by all the API classes when making requests to the Wistia API.

Another option is to use the global ``configure`` method as shown below:

.. code-block:: python3

    WistiaDataApi.configure('MY-API-TOKEN')

Sample usage with the `Data API <https://wistia.com/support/developers/data-api>`_:

.. code-block:: python3

    from wystia import WistiaApi
    from wystia.models import SortBy, LanguageCode, Customizations, Private


    # Retrieve a list of all projects in the Wistia account,
    # sorted A-Z and in ascending order.
    projects = WistiaApi.list_all_projects(SortBy.NAME)
    project_ids = [p.hashed_id for p in projects]
    # Print the project data as a prettified JSON string
    print(projects.prettify())

    # Retrieve a list of videos for a Wistia project.
    # Note: If you don't require asset info (such as ADs) on each
    #   video, I suggest calling `list_project` instead.
    videos = WistiaApi.list_videos('project-id')

    # Retrieve info on a particular video
    vd = WistiaApi.get_video('video-id')
    # If the video has captions, that won't be included in the `Medias#show`
    # response by default, so we'll need a separate API call as below.
    # vd.process_captions(
    #     WistiaApi.list_captions(real_video_id))
    print(vd)

    # Update attributes on a media (video), or set a custom thumbnail on the video.
    WistiaApi.update_video(
        'video-id',
        thumbnail_media_id='uploaded-thumbnail-id'
    )

    # Get aggregated stats for a video, such as view count
    stats = WistiaApi.get_stats_for_video('video-id')

    # Retrieve the customization data for a video
    customizations = WistiaApi.get_customizations('video-id')

    # Update only specific customizations for a video
    # Note the embed options are documented here:
    #   https://wistia.com/support/developers/embed-options
    sample_embed_options = Customizations(
        player_color='#e7fad1',
        # Hide comments on the media page
        private=Private(show_comments=False)
    )
    WistiaApi.update_customizations('video-id', sample_embed_options)

    # Get the Spanish captions on a video
    captions = WistiaApi.get_captions('video-id', LanguageCode.SPANISH)

    # Add (or replace) the English captions on a video
    WistiaApi.update_captions(
        'video-id',
        LanguageCode.ENGLISH,
        srt_file='path/to/file.srt'
    )


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
