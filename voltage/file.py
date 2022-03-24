from __future__ import annotations

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
    f: Union[:class:`str`, :class:`bytes`]
        The file to send, can either be a local filename (str) or bytes.
    filename: Optional[:class:`str`]
        The name of the file.
    spoiler: Optional[:class:`bool`]
        Whether or not the file is a spoiler.

    Examples
    --------

    .. code-block:: python3

        f = voltage.File("image.png", filename="interesting file", spoiler=True)

        await channel.send("Obligatory Message Content", attachment=f) # Uploads the file to autumn, gets the id and sends it.

        # You can also send files in embeds.

        embed = voltage.SendableEmbed(media=f)
        await channel.send("Obligatory Message Content", embed=embed)

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

    async def get_id(self, http: HTTPHandler) -> str:
        """
        Uploads a file to autumn then returns its id for sending.
        You won't need to run this method yourself.

        Parameters
        ----------
        http: :class:`HTTPHandler`
            The http handler.

        Returns
        -------
        :class:`str`
            The autumn id of the file.
        """
        file = await http.upload_file(self.file, self.filename, "attachments")
        return file["id"]
