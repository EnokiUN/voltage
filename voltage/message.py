from __future__ import annotations

from asyncio import sleep
from datetime import datetime
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Union

from ulid import ULID

from .asset import Asset, PartialAsset
from .embed import SendableEmbed, create_embed

if TYPE_CHECKING:
    from .file import File
    from .internals import CacheHandler
    from .member import Member
    from .types import (
        MessagePayload,
        MessageReplyPayload,
        OnMessageUpdatePayload,
        SendableEmbedPayload,
    )
    from .user import User


class MessageReply(NamedTuple):
    """A named tuple that represents a message reply.

    Attributes
    ----------
    message: :class:`Message`
        The message that was replied to,
    mention: :class:`bool`
        Wether or not the reply mentions the author of the message.
    """

    message: Message
    mention: bool

    def to_dict(self) -> MessageReplyPayload:
        """Returns a dictionary representation of the message reply."""
        return {"id": self.message.id, "mention": self.mention}


class MessageMasquerade(NamedTuple):
    """A named tuple that represents a message's masquerade.

    Attributes
    ----------
    name: Optional[:class:`str`]
        The name of the masquerade.
    avatar: Optional[:class:`str`]
        The url to the masquerade avatar.
    colour: Optional[:class:`str`]
        CSS-compatible colour of the username.
    color: Optional[:class:`str`]
        CSS-compatible color of the username.
    """

    name: Optional[str] = None
    avatar: Optional[str] = None
    colour: Optional[str] = None
    color: Optional[str] = None

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the message masquerade."""
        data = {}
        if self.name is not None:
            data["name"] = self.name
        if self.avatar is not None:
            data["avatar"] = self.avatar
        colour = self.colour or self.color
        if colour is not None:
            data["colour"] = colour
        return data


class MessageInteractions(NamedTuple):
    """A named tuple that represents a message's interactions.

    Attributes
    ----------
    reactions: Optional[:class:`list[:class:`str`]`]
        The reactions always below this messsage.
    restrict_reactions: Optional[:class:`bool`]
        Only allow reactions specified.
    """

    reactions: Optional[list[str]] = None
    restrict_reactions: Optional[bool] = None

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the message interactions."""
        return {
            "reactions": self.reactions if self.reactions else None,
            "restrict_reactions": self.restrict_reactions if self.restrict_reactions is not None else None,
        }


class Message:
    """A class that represents a Voltage message.

    Attributes
    ----------
    id: Optional[:class:`str`]
        The id of the message.
    created_at: :class:`int`
        The timestamp of when the message was created.
    channel: :class:`Channel`
        The channel the message was sent in.
    attachments: List[:class:`Asset`]]
        The attachments of the message.
    embeds: List[:class:`Embed`]
        The embeds of the message.
    content: :class:`str`
        The content of the message.
    author: Union[:class:`User`, :class:`Member`]
        The author of the message.
    replies: List[:class:`Message`]
        The replies of the message.
    mentions: List[Union[:class:`User`, :class:`Member`]]
        A list of mentioned users/members.
    """

    __slots__ = (
        "id",
        "created_at",
        "channel",
        "attachments",
        "server",
        "embeds",
        "content",
        "author",
        "edited_at",
        "mention_ids",
        "reply_ids",
        "replies",
        "cache",
    )

    def __init__(self, data: MessagePayload, cache: CacheHandler):
        self.cache = cache
        self.id = data["_id"]
        self.created_at = ULID().decode(self.id)
        self.content = data.get("content")
        self.attachments = [Asset(a, cache.http) for a in data.get("attachments", [])]
        self.embeds = [create_embed(e, cache.http) for e in data.get("embeds", [])]

        self.channel = cache.get_channel(data["channel"])

        self.server = self.channel.server
        self.author = (
            cache.get_member(self.server.id, data["author"]) if self.server else cache.get_user(data["author"])
        )

        if masquerade := data.get("masquerade"):
            if av := masquerade.get("avatar"):
                avatar = PartialAsset(av, cache.http)
            else:
                avatar = None
            self.author.set_masquerade(masquerade.get("name"), avatar)

        self.edited_at: Optional[datetime]
        if edited := data.get("edited"):
            self.edited_at = datetime.strptime(edited, "%Y-%m-%dT%H:%M:%S.%fz")
        else:
            self.edited_at = None

        self.reply_ids = data.get("replies", [])
        self.replies = []
        for i in self.reply_ids:
            try:
                self.replies.append(cache.get_message(i))
            except KeyError:
                pass

        self.mention_ids = data.get("mentions", [])

    async def full_replies(self):
        """Returns the full list of replies of the message."""
        replies = []
        for i in self.reply_ids:
            replies.append(await self.cache.fetch_message(self.channel.id, i))
        return replies

    async def edit(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Union[SendableEmbedPayload, SendableEmbed]] = None,
        embeds: Optional[List[Union[SendableEmbedPayload, SendableEmbed]]] = None,
    ):
        """Edits the message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The new content of the message.
        embed: Optional[:class:`SendableEmbed`]
            The new embed of the message.
        embeds: Optional[:class:`List[SendableEmbed]`]
            The new embeds of the message.
        """
        if content is None and embed is None and embeds is None:
            raise ValueError("You must provide at least one of the following: content, embed, embeds")

        if embed:
            embeds = [embed]

        content = str(content) if content else None

        await self.cache.http.edit_message(self.channel.id, self.id, content=content, embeds=embeds)

    async def delete(self, *, delay: Optional[float] = None):
        """Deletes the message."""
        if delay is not None:
            await sleep(delay)
        await self.cache.http.delete_message(self.channel.id, self.id)

    async def reply(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Union[SendableEmbed, SendableEmbedPayload]] = None,
        embeds: Optional[List[Union[SendableEmbed, SendableEmbedPayload]]] = None,
        attachment: Optional[Union[File, str]] = None,
        attachments: Optional[List[Union[File, str]]] = None,
        masquerade: Optional[MessageMasquerade] = None,
        interactions: Optional[MessageInteractions] = None,
        mention: bool = True,
        delete_after: Optional[float] = None,
    ) -> Message:
        """Replies to the message.

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
        masquerade: Optional[:class:`MessageMasquerade`]
            The masquerade of the message.
        interactions: Optional[:class:`MessageInteractions`]
            The interactions of the message.
        mention: Optional[:class:`bool`]
            Wether or not the reply mentions the author of the message.
        delete_after: Optional[:class:`float`]
            The amount of seconds to wait before deleting the message, if ``None`` the message will not be deleted.

        Returns
        -------
        :class:`Message`
            The message that got sent.
        """
        embeds = [embed] if embed else embeds
        attachments = [attachment] if attachment else attachments
        replies = MessageReply(self, mention)

        content = str(content) if content else None

        message = await self.cache.http.send_message(
            self.channel.id,
            content=content,
            embeds=embeds,
            attachments=attachments,
            replies=[replies],
            masquerade=masquerade,
            interactions=interactions,
        )
        msg = self.cache.add_message(message)
        if delete_after is not None:
            self.cache.loop.create_task(msg.delete(delay=delete_after))
        return msg

    async def react(self, emoji: str):
        await self.cache.http.add_reaction(self.channel.id, self.id, emoji)

    async def unreact(self, emoji: str):
        await self.cache.http.delete_reaction(self.channel.id, self.id, emoji)

    async def remove_reactions(self):
        await self.cache.http.delete_all_reaction(self.channel.id, self.id)

    @property
    def jump_url(self) -> str:
        """Returns a URL that allows the client to jump to the message."""
        server_segment = "" if self.server is None else f"/server/{self.server.id}"
        return f"https://app.revolt.chat/{server_segment}channel/{self.channel.id}/{self.id}"

    @property
    def mentions(self) -> list[Union[User, Member]]:
        mentioned: list[Union[User, Member]] = []
        for mention in self.mention_ids:
            if self.server:
                mentioned.append(self.cache.get_member(self.server.id, mention))
                continue
            mentioned.append(self.cache.get_user(mention))
        return mentioned

    def _update(self, data: OnMessageUpdatePayload):
        if new := data.get("data"):
            if edited := new.get("edited"):
                self.edited_at = datetime.strptime(edited, "%Y-%m-%dT%H:%M:%S.%fz")
            if content := new.get("content"):
                self.content = content
            if embeds := new.get("embeds"):
                self.embeds = [create_embed(e, self.cache.http) for e in embeds]
