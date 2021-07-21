import sys


if sys.version_info < (3, 7):   # pragma: no cover
    # compatibility with Python versions 3.5 and 3.6
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

# TODO Remove below logic to import from `models_py35` once we drop support
#  for Python 3.5
#
try:
    from dataclasses import dataclass    # noqa
except ImportError:    # pragma: no cover
    # Python 3.5 doesn't support dataclasses
    from .models_py35 import *    # noqa
else:
    # We are running Python 3.6+
    from .models_default import *    # noqa
