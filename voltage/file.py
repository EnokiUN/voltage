from io import BytesIO
from typing import TYPE_CHECKING, Optional, Union

# Internal imports
if TYPE_CHECKING:
    from .internals import HTTPHandler


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

        if spoiler or filename.startswith("SPOILER_"):
            spoiler = True
            if not filename.startswith("SPOILER_"):
                filename = f"SPOILER_{filename}"

        self.filename = filename

    async def to_sendable(self, http: "HTTPHandler") -> str:
        """
        Uploads a file to autumn then returns it's id for sending.

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
