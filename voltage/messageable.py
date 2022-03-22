from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

# Internal imports
from .enums import SortType

if TYPE_CHECKING:
    from .embed import Embed, SendableEmbed
    from .file import File
    from .internals import CacheHandler
    from .message import Message, MessageMasquerade, MessageReply
    from .types import MessageReplyPayload, SendableEmbedPayload


class Messageable:  # Really missing rust traits rn :(
    """
    A class which all messageable have to inhertit from.

    Attributes
    ----------
    channel_id: :class:`str`
        The ID of the messageable object's channel.
    cache: :class:`CacheHandler`
        The cache handler of the messageable object.
    """

    __slots__ = ()

    cache: CacheHandler

    async def get_id(self) -> str:
        """
        Get the ID of the messageable object's channel.

        Returns
        -------
        :class:`str`
            The ID of the messageable object's channel.
        """
        return NotImplemented  # TIL: NotImplemented is a thing, thank you mr random stackoverflow user.

    async def send(
        self,
        content: str,
        *,
        embed: Optional[Union[SendableEmbed, SendableEmbedPayload]] = None,
        embeds: Optional[List[Union[SendableEmbed, SendableEmbedPayload]]] = None,
        attachment: Optional[Union[File, str]] = None,
        attachments: Optional[List[Union[File, str]]] = None,
        reply: Optional[MessageReply] = None,
        replies: Optional[List[Union[MessageReply, MessageReplyPayload]]] = None,
        masquerade: Optional[MessageMasquerade] = None,
    ) -> Message:  # YEAH BABY, THAT'S WHAT WE'VE BEEN WAITING FOR, THAT'S WHAT IT'S ALL ABOUT, WOOOOOOOOOOOOOOOO
        """
        Send a message to the messageable object's channel.

        Parameters
        ----------
        content: :class:`str`
            The content of the message.
        embed: Optional[:class:`Embed`]
            The embed of the message.
        embeds: Optional[List[:class:`Embed`]]
            The embeds of the message.
        attachment: Optional[:class:`File`]
            The attachment of the message.
        attachments: Optional[List[:class:`File`]]
            The attachments of the message.
        reply: Optional[:class:`MessageReply`]
            The reply of the message.
        replies: Optional[List[:class:`MessageReply`]]
            The replies of the message.
        masquerade: Optional[:class:`MessageMasquerade`]
            The masquerade of the message.

        Returns
        -------
        :class:`Message`
            The message that got sent.
        """
        embeds = [embed] if embed else embeds
        replies = [reply] if reply else replies
        attachments = [attachment] if attachment else attachments

        message = await self.cache.http.send_message(
            await self.get_id(), content, embeds=embeds, attachments=attachments, replies=replies, masquerade=masquerade
        )
        return self.cache.add_message(message)

    async def fetch_message(self, message_id: str) -> Message:
        """
        Fetch a message from the messageable object's channel.

        Parameters
        ----------
        message_id: :class:`str`
            The ID of the message to fetch.

        Returns
        -------
        :class:`Message`
            The message that got fetched.
        """
        return await self.cache.fetch_message(await self.get_id(), message_id)

    async def history(
        self,
        limit: int = 100,
        *,
        sort: SortType = SortType.latest,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
    ) -> List[Message]:
        """
        Fetch the messageable object's channel's history.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The limit of the history.
        sort: Optional[:class:`SortType`]
            The sort type of the history.
        before: Optional[:class:`str`]
            The ID of the message to fetch before.
        after: Optional[:class:`str`]
            The ID of the message to fetch after.
        nearby: Optional[:class:`str`]
            The ID of the message to fetch nearby.

        Returns
        -------
        List[:class:`Message`]
            The messages that got fetched.
        """
        messages = await self.cache.http.fetch_messages(await self.get_id(), sort.value, limit=limit, before=before, after=after, nearby=nearby, include_users=False)  # type: ignore
        return [Message(data, self.cache) for data in messages]

    async def search(
        self,
        query: str,
        *,
        sort: SortType = SortType.latest,
        limit: int = 100,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> List[Message]:
        """
        Search for messages in the messageable object's channel.

        Parameters
        ----------
        query: :class:`str`
            The query to search for.
        sort: Optional[:class:`SortType`]
            The sort type of the search.
        limit: Optional[:class:`int`]
            The limit of the search.
        before: Optional[:class:`str`]
            The ID of the message to fetch before.
        after: Optional[:class:`str`]
            The ID of the message to fetch after.

        Returns
        -------
        List[:class:`Message`]
            The messages that got found.
        """
        messages = await self.cache.http.search_for_message(
            await self.get_id(), query, sort=sort.value, limit=limit, before=before, after=after, include_users=False
        )
        return [Message(data, self.cache) for data in messages]
