from __future__ import annotations

from asyncio import Task, sleep
from typing import TYPE_CHECKING, List, Optional, Union

# Internal imports
from .enums import SortType
from .errors import HTTPError
from .message import Message, MessageInteractions

if TYPE_CHECKING:
    from .embed import SendableEmbed
    from .file import File
    from .internals import CacheHandler
    from .message import MessageMasquerade, MessageReply
    from .types import MessagePayload, MessageReplyPayload, SendableEmbedPayload


class Typing:
    """
    A simple context manager for typing.
    """

    def __init__(self, channel: Messageable):
        self.channel = channel
        self.ws = channel.cache.ws
        self.loop = channel.cache.loop
        self.task: Task

    async def keep_typing(self):
        while True:
            await self.channel.start_typing()
            await sleep(2)

    def __enter__(self):
        self.task = self.loop.create_task(self.keep_typing())
        return self

    def __exit__(self, *_):
        self.task.cancel()
        self.loop.create_task(self.channel.end_typing())

    async def __aenter__(self):
        self.task = self.loop.create_task(self.keep_typing())
        return self

    async def __aexit__(self, *_):
        self.task.cancel()
        await self.channel.end_typing()


class MessageIterator:
    def __init__(self, data: list[MessagePayload], channel: Messageable):
        self.data = data
        self.processed: list[Message] = []
        self.channel = channel

    def _process_next(self):
        if len(self.data) == 0:
            if len(self.processed) == 0:
                return None
            else:
                self.processed.append(Message(self.data.pop(0), self.channel.cache))
                return self.processed[-1]

    def _get_next_message(self):
        return self.processed.pop(0)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.data) == 0:
            raise StopIteration
        return Message(self.data.pop(0), self.channel.cache)

    def __len__(self):
        return len(self.data) + len(self.processed)

    def __getitem__(self, index: int):
        while len(self.processed) <= index:
            self._process_next()
        return Message(self.data[index], self.channel.cache)

    def __reversed__(self):
        return MessageIterator(list(reversed(self.data)), self.channel)


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
        content: Optional[str] = None,
        *,
        embed: Optional[Union[SendableEmbed, SendableEmbedPayload]] = None,
        embeds: Optional[List[Union[SendableEmbed, SendableEmbedPayload]]] = None,
        attachment: Optional[Union[File, str]] = None,
        attachments: Optional[List[Union[File, str]]] = None,
        reply: Optional[MessageReply] = None,
        replies: Optional[List[Union[MessageReply, MessageReplyPayload]]] = None,
        masquerade: Optional[MessageMasquerade] = None,
        interactions: Optional[MessageInteractions] = None,
        delete_after: Optional[float] = None,
    ) -> Message:  # YEAH BABY, THAT'S WHAT WE'VE BEEN WAITING FOR, THAT'S WHAT IT'S ALL ABOUT, WOOOOOOOOOOOOOOOO
        """
        Send a message to the messageable object's channel.

        Parameters
        ----------
        content: Optional[:class:`str`]
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
        interactions: Optional[:class:`MessageInteractions`]
            The interactions of the message.

        Returns
        -------
        :class:`Message`
            The message that got sent.
        """
        embeds = [embed] if embed else embeds
        replies = [reply] if reply else replies
        attachments = [attachment] if attachment else attachments

        content = str(content) if content else None

        message = await self.cache.http.send_message(
            await self.get_id(),
            content=content,
            embeds=embeds,
            attachments=attachments,
            replies=replies,
            masquerade=masquerade,
            interactions=interactions,
        )
        msg = self.cache.add_message(message)
        if delete_after is not None:
            self.cache.loop.create_task(msg.delete(delay=delete_after))
        return msg

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
    ) -> MessageIterator:
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
        returned = []
        for i in messages:
            if i["author"] != "00000000000000000000000000":
                returned.append(i)
        return MessageIterator(returned, self)

    async def search(
        self,
        query: str,
        *,
        sort: SortType = SortType.latest,  # type: ignore
        limit: int = 100,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> MessageIterator:
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
            await self.get_id(),
            query,
            sort=sort.value,
            limit=limit,
            before=before,
            after=after,
            include_users=False,
        )
        return MessageIterator(messages, self)

    async def purge(self, amount: int):
        """
        Purge messages from the messageable object's channel.

        Parameters
        ----------
        amount: :class:`int`
            The amount of messages to purge.
        """
        channel_id = await self.get_id()
        for i in await self.cache.http.fetch_messages(
            channel_id, "Latest", limit=amount
        ):
            try:
                await self.cache.http.delete_message(channel_id, i["_id"])
            except HTTPError as e:
                status = e.response.status
                if status == 404:
                    pass
                else:
                    raise

    def typing(self) -> Typing:
        """
        A context manager that sends a typing indicator to the messageable object's channel.
        """
        return Typing(self)

    async def start_typing(self):
        """
        Send a typing indicator to the messageable object's channel.
        """
        await self.cache.ws.begin_typing(await self.get_id())

    async def end_typing(self):
        """
        Stop sending a typing indicator to the messageable object's channel.
        """
        await self.cache.ws.end_typing(await self.get_id())
