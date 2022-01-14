# Examples

This directory contains sample scripts to demonstrate
the functionality and intended usage of the Wistia API wrapper in Python.

## Setup and Quickstart

First ensure that you've set up your virtual environment
for development already.

From the root of the project, activate your `venv`:

    $ virtualenv venv
    $ . venv/bin/activate

Now install the project's dev dependencies:

    $ make init

Now you'll need to configure your API key to pass to the
Wistia Data API.

There's actually two options you can choose to set this up:

1. Set the `WISTIA_API_TOKEN` env variable.

   For example, on a Mac/Linux environment:
   ````
   $ export WISTIA_API_TOKEN="MY-TOKEN"
   ````

2. Replace the value for `wistia_token` in the [config.py](./config.py)
   script with your wistia API key.

### Run an Example Script

Let's try to run a simple script which will print a list of all the projects
in your Wistia account, along with the details for each
project.

To test it out, first `cd` into the `examples/` directory, and then run the
following command:

    $ python data/list_all_projects.py

If all goes well, you should see an output being printed to the
terminal, that looks similar to the below:

```
Project Count: 11

Projects:
--
[Project(hashed_id='xyz7654321',
         id=12345,
         name="Vendor's first project",
         media_count=0,
         created=datetime.datetime(2017, 2, 25, 2, 8, 7, tzinfo=datetime.timezone.utc),
         updated=datetime.datetime(2017, 5, 2, 13, 57, 52, tzinfo=datetime.timezone.utc),
         anonymous_can_upload=False,
         anonymous_can_download=False,
         public=True,
         public_id='xyz7654321',
         description=None),
 ...
```

### Retrieve Info on a Video

For our next try, let's try to retrieve info on an existing video
in our Wistia account.

First, make a note of the video's hashed ID. This will generally be
the last trailing part at the end of the url in a browser.

Now, let's try passing the video ID as an argument to the script. Let's also print
the prettified JSON representation of the API response, rather than the Python object
representation, by passing the `-p/--pretty` flag, as shown below:

    $ python data/get_video_info.py -p abc1234567

If all goes well, we'd expect to see a formatted JSON response,
similar to below:

```
Video Data:
--
{
    "hashedId": "abc1234567",
    "id": 112233,
    "name": "My Video Title",
    "type": "Video",
    "created": "2020-10-02T17:17:21Z",
    "updated": "2021-02-15T21:07:34Z",
    "duration": 127.0,
    "status": "ready",
    ...
```
