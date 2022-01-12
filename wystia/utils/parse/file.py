from __future__ import annotations

__all__ = ['resolve_contents']

from ...errors import ContentIsEmpty


def resolve_contents(
    file_path: str | None = None,
    contents: str | None = None,
    raise_=True
) -> str:
    """
    Resolves file contents, given two optional parameters.

    :param file_path: An optional path to the file to read.
    :param contents: The optional contents of a file.
    :param raise_: Whether to raise an error if the file contents are empty.
    :return: The resolved file contents.
    :raises ContentIsEmpty: If both `file_path` and `contents` are empty, and
      the `raise_` flag is enabled.
    """
    if file_path:
        with open(file_path, 'r') as f:
            contents = f.read()

    if not contents and raise_:
        raise ContentIsEmpty()

    return contents
