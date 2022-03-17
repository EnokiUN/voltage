from typing import TYPE_CHECKING, Optional, Union

# Internal imports
if TYPE_CHECKING:
    from .internals import HTTPHandler

async def get_file_from_url(http: HTTPHandler, url: str, filename: str = "Attachment", spoiler: bool = False) -> File:
    """
    Returns a file object from the supplied URL.

    Parameters
    ----------
    http: :class:`HTTPHandler`
        The HTTP handler to use.
    url: :class:`str`
        The URL to get the file from.

    Returns
    -------
    :class:`File`
        The file object.
    """
    return File(await http.get_file_binary(url.split("?")[0]), filename=filename, spoiler=spoiler)

class File:
    """
    The Object representing a generic file that can be sent in a Message.

    Parameters
    ----------
    f: Union[str, bytes]
        The file to send.
    filename: Optional[str]
        The name of the file.
    spoiler: Optional[bool]
        Whether or not the file is a spoiler.
    """

    __slots__ = ("file", "filename", "spoiler")

    def __init__(
        self, f: Union[str, bytes], *, filename: Optional[str] = None, spoiler: Optional[bool] = False
    ) -> None:
        if isinstance(f, str):
            with open(f, "rb") as file:
                self.file = file.read()
        elif isinstance(f, bytes):
            self.file = f
        else:
            raise TypeError("f must be a string or bytes")

        filename = filename if not filename is None else "file"

        if spoiler and not filename.startswith("SPOILER_"):
            filename = f"SPOILER_{filename}"

        self.filename = filename

    async def get_id(self, http: "HTTPHandler") -> str:
        """
        Uploads a file to autumn then returns its id for sending.

        Parameters
        ----------
        http: voltage.HTTPHandler
            The http handler.

        Returns
        -------
        str
            The id of the file.
        """
        file = await http.upload_file(self.file, self.filename, "attachments")
        return file["id"]
