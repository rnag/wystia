import examples
from datetime import timedelta
from time import time

from pathlib import Path

from wystia import WistiaUploadApi


file_path = str(
    Path(__file__).parent.parent.parent
    / 'tests' / 'testdata' / 'sample-video.mp4'
)
project_id = None
title = None
description = None

start = time()
r = WistiaUploadApi.upload_file(
    file_path,
    project_id=project_id,
    title=title,
    description=description
)
elapsed = timedelta(seconds=time()-start)

print(f'[{elapsed}] Uploaded sample video to Wistia successfully.')
print()

print('Response:', r)
print()

print('Video ID:', r.hashed_id)
