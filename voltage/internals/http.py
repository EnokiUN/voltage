from __future__ import annotations

from asyncio import gather
from io import BytesIO
from json import decoder, dumps
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from aiohttp import ClientSession, FormData

from ..embed import SendableEmbed

# Internal imports
from ..errors import HTTPError
from ..file import File
from ..message import MessageMasquerade, MessageReply

if TYPE_CHECKING:
    from ..enums import *
    from ..message import MessageMasquerade, MessageReply
    from ..types import *


class HTTPHandler:
    """
    A simple handler for http requests.

    Parameters
    ----------
    client: aiohttp.ClientSession
        The client to use for the http requests.
    token: str
        The bot token to use for authentication.
    api_url: Optional[str]
        The url of the api. Defaults to "https://api.revolt.chat/".
    """

    __slots__ = ("client", "token", "api_url", "api_info")

    def __init__(self, client: ClientSession, token: str, *, api_url: str = "https://api.revolt.chat/"):
        self.client = client
        self.token = token
        self.api_url = api_url
        self.api_info: Optional[ApiInfoPayload] = None

    async def request(
        self, method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], url: str, auth: Optional[bool] = True, **kwargs
    ) -> Any:
        """
        Makes a request to the API.

        Parameters
        ----------
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
            The method to use for the request.
        url: :class:`str`
            The url to send the request to.
        auth: Optional[:class:`bool`]
            Whether or not to use authentication. Defaults to True.
        kwargs: dict
            The kwargs to pass to the request.

        Raises
        ------
        HTTPError: If the request didn't respond with a status code between 200 and 300.

        Returns
        -------
        The response of the request.
        """
        header = {"User-Agent": "Voltage (beta)", "Content-Type": "application/json"}
        if auth:
            header["x-bot-token"] = self.token
        async with self.client.request(method, self.api_url + url, headers=header, **kwargs) as request:
            if request.status >= 200 and request.status <= 300:
                if (await request.read()) == b"":
                    return {}
                return await request.json()
            raise HTTPError(request)

    async def upload_file(self, file: bytes, name: str, tag: str) -> AutumnPayload:
        """
        Uploads a file to autumn.

        Parameters
        ----------
        file: :class:`bytes`
            The file to upload.
        name: :class:`str`
            The name of the file.
        tag: :class:`str`
            The tag of the file.
        """
        api_info = await self.get_api_info()

        headers = {
            "User-Agent": "Voltage (beta)",
        }

        autumn = f'{api_info["features"]["autumn"]["url"]}/{tag}'

        form = FormData()
        form.add_field("file", file, filename=name)

        async with self.client.post(autumn, data=form, headers=headers) as request:
            if 200 >= request.status <= 300:
                return await request.json()
            raise HTTPError(request)

    async def get_file_binary(self, url: str) -> bytes:
        """
        Gets the binary of a file.

        Parameters
        ----------
        url: :class:`str`
            The url of the file.
        """
        async with self.client.get(url) as request:
            if 200 >= request.status <= 300:
                return await request.read()
            raise HTTPError(request)

    async def query_node(self) -> ApiInfoPayload:
        """
        Gets info about the API.
        """
        return await self.request("GET", "")

    async def get_api_info(self) -> ApiInfoPayload:
        """
        query_node but better.
        """
        if self.api_info is None:
            self.api_info = await self.query_node()
        return self.api_info

    async def fetch_user(self, user_id: str):
        """
        Gets info about a user.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}")

    async def edit_self(
        self,
        *,
        status: Optional[
            Dict[Literal["text", "presence"], Union[str, Literal["Busy", "Idle", "Invisible", "Online"]]]
        ] = None,
        profile: Optional[Dict[Literal["content", "background"], str]] = None,
        avatar: Optional[str] = None,
        remove: Optional[Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]] = None,
    ) -> UserPayload:
        """
        Edits the bot's profile.

        Parameters
        ----------
        status: Optional[Dict[Literal["text", "presence"], Union[:class:`str`, Literal["Busy", "Idle", "Invisible", "Online"]]]]
            The new status of the bot.
        profile: Optional[Dict[Literal["content", "background"], :class:`str`]]
            The new profile of the bot.
        avatar: Optional[:class:`str`]
            The new avatar of the bot.
        remove: Optional[Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]]
            The thing to remove from the bot.
        """
        data: Dict[str, Any] = {}
        if status:
            data["status"] = status
        if profile:
            data["profile"] = profile
        if avatar:
            data["avatar"] = avatar
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", "users/me", json=data)

    async def fetch_self(self) -> UserPayload:
        """
        Gets info about the bot.
        """
        return await self.request("GET", "users/@me")

    async def fetch_user_profile(self, user_id: str) -> UserProfilePayload:
        """
        Gets the profile of a user.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/profile")

    async def fetch_default_avatar(self, user_id: str) -> bytes:
        """
        Gets the default avatar of a user.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user.
        """
        return await self.get_file_binary(f"users/{user_id}/default_avatar")

    async def fetch_mutuals(self, user_id: str):
        """
        Gets the mutual friends and servers of a user with the bot.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/mutual")

    async def fetch_dms(self) -> List[DMChannelPayload]:
        """
        Gets all the direct messages and group dms a bot is in.
        """
        return await self.request("GET", "users/dms")

    async def open_dm(self, user_id: str) -> DMChannelPayload:
        """
        Opens a direct message with a user.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/dm")

    async def fetch_channel(self, channel_id: str) -> ChannelPayload:
        """
        Gets info about a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        """
        return await self.request("GET", f"channels/{channel_id}")

    async def edit_channel(
        self,
        channel_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        nsfw: Optional[bool] = None,
        remove: Optional[Literal["Description", "Icon"]] = None,
    ) -> ChannelPayload:
        """
        Edits a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        name: Optional[:class:`str`]
            The new name of the channel.
        description: Optional[:class:`str`]
            The new description of the channel.
        icon: Optional[:class:`str`]
            The new icon of the channel.
        nsfw: Optional[:class:`bool`]
            Whether the channel is nsfw or not.
        remove: Optional[Literal["Description", "Icon"]]
            The thing to remove from the channel.
        """
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if icon:
            data["icon"] = icon
        if nsfw:
            data["nsfw"] = nsfw
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"channels/{channel_id}", json=data)

    async def close_channel(self, channel_id: str):
        """
        Depending on the type of channel, deleted it if it's a server channel, leaves it if it's a group channel and closes it if it's a dm.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        """
        return await self.request("DELETE", f"channels/{channel_id}")

    async def create_invite(self, channel_id: str) -> InvitePayload:
        """
        Creates an invite for a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        """
        return await self.request("POST", f"channels/{channel_id}/invites")

    async def set_role_perms(self, channel_id: str, role_id: str, permissions: int):
        """
        Sets the permissions of a role in a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        role_id: :class:`str`
            The id of the role.
        permissions: :class:`int`
            The permissions to set.
        """
        return await self.request(
            "PUT", f"channels/{channel_id}/permissions/{role_id}", json={"permissions": permissions}
        )

    async def set_default_perms(self, channel_id: str, permissions: int):
        """
        Sets the default permissions of a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        permissions: :class:`int`
            The permission to set.
        """
        return await self.request(
            "PUT", f"channels/{channel_id}/permissions/default", json={"permissions": permissions}
        )

    async def send_message(
        self,
        channel_id: str,
        content: str,
        *,
        attachments: Optional[List[Union[str, File]]] = None,
        embeds: Optional[List[Union[SendableEmbedPayload, SendableEmbed]]] = None,
        replies: Optional[List[Union[MessageReplyPayload, MessageReply]]] = None,
        masquerade: Optional[Union[MasqueradePayload, MessageMasquerade]] = None,
    ) -> MessagePayload:
        """
        Sends a message to a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        content: :class:`str`
            The content of the message.
        attachments: Optional[List[Union[:class:`str`, :class:`File`]]]
            The attachments of the message.
        embeds: Optional[List[Union[:class:`SendableEmbedPayload`, :class:`SendableEmbed`]]]
            The embeds of the message.
        replies: Optional[List[Union[:class:`MessageReplyPayload`, :class:`MessageReply`]]]
            The replies of the message.
        masquerade: Optional[Union[:class:`MasqueradePayload`, :class:`MessageMasquerade`]]
            The masquerade of the message.
        """
        data: Dict[str, Any] = {"content": content}
        if attachments:
            data["attachments"] = await gather(*[self.handle_attachment(attachment) for attachment in attachments])
        if embeds:
            data["embeds"] = await gather(*[self.handle_embed(embed) for embed in embeds])
        if replies:
            new_replies: List[MessageReplyPayload] = []
            for i in replies:
                if isinstance(i, MessageReply):
                    new_replies.append(i.to_dict())
                else:
                    new_replies.append(i)
            data["replies"] = new_replies
        if masquerade:
            data["masquerade"] = masquerade.to_dict() if isinstance(masquerade, MessageMasquerade) else masquerade
        return await self.request("POST", f"channels/{channel_id}/messages", json=data)

    async def fetch_messages(
        self,
        channel_id: str,
        sort: Literal["Latest", "Oldest"],
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
        include_users: Optional[bool] = None,
    ) -> List[MessagePayload]:
        """
        Gets a list of messages from a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        sort: Literal["Latest", "Oldest"]
            The way to sort the messages.
        limit: Optional[int]
            The limit of the messages.
        before: Optional[str]
            The id of the message to search before.
        after: Optional[str]
            The id of the message to search after.
        nearby: Optional[str]
            The message id to get the messages near.
        include_users: Optional[bool]
            Whether to include the users in the messages.
        """
        data: Dict[str, Any] = {"sort": sort}
        if limit:
            data["limit"] = limit
        if before:
            data["before"] = before
        if after:
            data["after"] = after
        if nearby:
            data["nearby"] = nearby
        if include_users:
            data["include_users"] = include_users
        return await self.request("GET", f"channels/{channel_id}/messages", params=data)

    async def fetch_message(self, channel_id: str, message_id: str) -> MessagePayload:
        """
        Gets a message from a channel.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        message_id: :class:`str`
            The id of the message.
        """
        return await self.request("GET", f"channels/{channel_id}/messages/{message_id}")

    async def edit_message(
        self,
        channel_id: str,
        message_id: str,
        content: str,
        *,
        embeds: Optional[List[Union[SendableEmbedPayload, SendableEmbed]]] = None,
    ) -> MessagePayload:
        """
        Edits a message.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        message_id: :class:`str`
            The id of the message.
        content: :class:`str`
            The content of the message.
        embeds: Optional[List[Union[:class:`SendableEmbedPayload`, :class:`SendableEmbed`]]]
            The embeds of the message.
        """
        data: Dict[str, Any] = {"content": content}
        if embeds:
            data["embeds"] = await gather(*[self.handle_embed(embed) for embed in embeds])
        return await self.request("PATCH", f"channels/{channel_id}/messages/{message_id}", json=data)

    async def delete_message(self, channel_id: str, message_id: str):
        """
        Deletes a message.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        message_id: :class:`str`
            The id of the message.
        """
        return await self.request("DELETE", f"channels/{channel_id}/messages/{message_id}")

    async def poll_message_changed(
        self, channel_id: str, ids: List[str]
    ) -> Dict[str, Union[str, List[MessagePayload]]]:
        """
        Polls for a message change.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        ids: List[:class:`str`]
            The ids of the messages.
        """
        return await self.request("GET", f"channels/{channel_id}/messages/changed", params={"ids": ",".join(ids)})

    async def search_for_message(
        self,
        channel_id: str,
        query: str,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[Literal["Latest", "Oldest", "Relevance"]] = None,
        include_users: Optional[bool] = None,
    ) -> List[MessagePayload]:
        """
        Searches for a message.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        query: :class:`str`
            The query of the message.
        limit: Optional[:class:`int`]
            The limit of the messages.
        before: Optional[:class:`str`]
            The id of the message to fetch before.
        after: Optional[:class:`str`]
            The id of the message to be fetched after.
        sort: Optional[Literal["Latest", "Oldest", "Relevance"]]
            The way of sorting the messages.
        include_users: Optional[:class:`bool`]
            Whether to include the users in the messages.
        """
        data: Dict[str, Any] = {"query": query}
        if limit:
            data["limit"] = limit
        if before:
            data["before"] = before
        if after:
            data["after"] = after
        if sort:
            data["sort"] = sort
        if include_users:
            data["include_users"] = include_users
        return await self.request("GET", f"channels/{channel_id}/messages/search", params=data)

    async def fetch_group_members(self, channel_id: str) -> List[UserPayload]:
        """
        Gets the members of a group.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        """
        return await self.request("GET", f"channels/{channel_id}/members")

    async def join_call(self, channel_id: str) -> Dict[str, str]:
        """
        Joins a call.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel.
        """
        return await self.request("POST", f"channels/{channel_id}/join_call")

    async def fetch_server(self, server_id: str) -> ServerPayload:
        """
        Gets info about a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}")

    async def edit_server(
        self,
        server_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        banner: Optional[str] = None,
        categories: Optional[List[Dict[Literal["id", "title", "channels"], str]]] = None,
        system_messages: Optional[Dict[Literal["user_joined", "user_left", "user_kicked", "user_banned"], str]] = None,
        nsfw: Optional[bool] = None,
        remove: Optional[Literal["Banner", "Description", "Icon"]] = None,
    ) -> ServerPayload:
        """
        Edits a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        name: Optional[:class:`str`]
            The name of the server.
        description: Optional[:class:`str`]
            The description of the server.
        icon: Optional[:class:`str`]
            The icon of the server.
        banner: Optional[:class:`str`]
            The banner of the server.
        categories: Optional[List[Dict[Literal["id", "title", "channels"], :class:`str`]]]
            The categories of the server.
        system_messages: Optional[Dict[Literal["user_joined", "user_left", "user_kicked", "user_banned"], :class:`str`]]
            The system messages of the server.
        nsfw: Optional[:class:`bool`]
            Whether the server is nsfw.
        remove: Optional[Literal["Banner", "Description", "Icon"]]
            The field to remove.
        """
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if icon:
            data["icon"] = icon
        if banner:
            data["banner"] = banner
        if categories:
            data["categories"] = categories
        if system_messages:
            data["system_messages"] = system_messages
        if nsfw:
            data["nsfw"] = nsfw
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"servers/{server_id}", json=data)

    async def delete_server(self, server_id: str):
        """
        Deletes a server if you own it, otherwise leave it.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        """
        return await self.request("DELETE", f"servers/{server_id}")

    async def create_channel(
        self,
        server_id: str,
        *,
        type: Literal["Text", "Voice"],
        name: str,
        description: Optional[str] = None,
        nsfw: Optional[bool] = None,
    ) -> ChannelPayload:
        """
        Creates a channel.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        type: Literal["Text", "Voice"]
            The type of the channel.
        name: :class:`str`
            The name of the channel.
        description: Optional[:class:`str`]
            The description of the channel.
        nsfw: Optional[:class:`bool`]
            Whether the channel is nsfw.
        """
        data: Dict[str, Any] = {"type": type, "name": name}
        if description:
            data["description"] = description
        if nsfw:
            data["nsfw"] = nsfw
        return await self.request("POST", f"servers/{server_id}/channels", json=data)

    async def fetch_invites(self, server_id: str) -> List[PartialInvitePayload]:
        """
        Gets the invites of a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/invites")

    async def fetch_member(self, server_id: str, member_id: str) -> MemberPayload:
        """
        Gets info about a member.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        member_id: :class:`str`
            The id of the member.
        """
        return await self.request("GET", f"servers/{server_id}/members/{member_id}")

    async def edit_member(
        self,
        server_id: str,
        member_id: str,
        *,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        roles: Optional[List[str]] = None,
        remove: Optional[Literal["Avatar", "Nickname"]] = None,
    ) -> MemberPayload:
        """
        Edits a member.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        member_id: :class:`str`
            The id of the member.
        nickname: Optional[:class:`str`]
            The nickname of the member.
        avatar: Optional[:class:`str`]
            The avatar of the member.
        roles: Optional[List[:class:`str`]]
            The roles of the member.
        remove: Optional[Literal["Avatar", "Nickname"]]
            The field to remove.
        """
        data: Dict[str, Any] = {}
        if nickname:
            data["nick"] = nickname
        if avatar:
            data["avatar"] = avatar
        if roles:
            data["roles"] = roles
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"servers/{server_id}/members/{member_id}", json=data)

    async def kick_member(self, server_id: str, member_id: str) -> None:
        """
        Kicks a member.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        member_id: :class:`str`
            The id of the member.
        """
        return await self.request("DELETE", f"servers/{server_id}/members/{member_id}")

    async def fetch_members(self, server_id) -> GetServerMembersPayload:
        """
        Gets the members of a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/members")

    async def ban_member(self, server_id: str, member_id: str, *, reason: Optional[str] = None):
        """
        Bans a member.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        member_id: :class:`str`
            The id of the member.
        reason: Optional[:class:`str`]
            The reason of the ban.
        """
        data = {}
        if reason:
            data["reason"] = reason
        return await self.request("PUT", f"servers/{server_id}/bans/{member_id}", json=data)

    async def unban_member(self, server_id: str, member_id: str):
        """
        Unbans a member.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        member_id: :class:`str`
            The id of the member.
        """
        return await self.request("DELETE", f"servers/{server_id}/bans/{member_id}")

    async def fetch_bans(self, server_id: str) -> List[BanPayload]:
        """
        Gets the bans of a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/bans")

    async def set_role_permission(
        self, server_id: str, role_id: str, server_permissions: int, channel_permissions: int
    ):
        """
        Sets the permissions of a role.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        role_id: :class:`str`
            The id of the role.
        server_permissions: :class:`int`
            The server permissions.
        channel_permissions: :class:`int`
            The channel permissions.
        """
        return await self.request(
            "PUT",
            f"servers/{server_id}/roles/{role_id}",
            json={"permissions": {"server": server_permissions, "channel": channel_permissions}},
        )

    async def set_default_permissions(self, server_id: str, server_permissions: int, channel_permissions: int):
        """
        Sets the default permissions of a server.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        server_permissions: :class:`int`
            The server permissions.
        channel_permissions: :class:`int`
            The channel permissions.
        """
        return await self.request(
            "PUT",
            f"servers/{server_id}/default_role",
            json={"permissions": {"server": server_permissions, "channel": channel_permissions}},
        )

    async def create_role(self, server_id: str, name: str) -> RolePayload:
        """
        Creates a role.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        name: :class:`str`
            The name of the role.
        """
        return await self.request("POST", f"servers/{server_id}/roles", json={"name": name})

    async def edit_role(
        self,
        server_id: str,
        role_id: str,
        name: str,
        *,
        colour: Optional[str] = None,
        hoist: Optional[bool] = None,
        rank: Optional[int] = None,
        remove: Optional[Literal["Colour"]] = None,
    ) -> RolePayload:
        """
        Edits a role.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        role_id: :class:`str`
            The id of the role.
        name: :class:`str`
            The name of the role.
        colour: Optional[:class:`str`]
            The colour of the role.
        hoist: Optional[:class:`bool`]
            Whether the role is hoisted.
        rank: Optional[:class:`int`]
            The rank of the role.
        remove: Optional[Literal["Colour"]]
            The field to remove.
        """
        data: Dict[str, Any] = {"name": name}
        if colour:
            data["color"] = colour
        if hoist:
            data["hoist"] = hoist
        if rank:
            data["position"] = rank
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"servers/{server_id}/roles/{role_id}", json=data)

    async def delete_role(self, server_id: str, role_id: str):
        """
        Deletes a role.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server.
        role_id: :class:`str`
            The id of the role.
        """
        return await self.request("DELETE", f"servers/{server_id}/roles/{role_id}")

    async def fetch_invite(self, invite_code: str) -> InvitePayload:
        """
        Gets info about an invite.

        Parameters
        ----------
        invite_code: :class:`str`
            The code of the invite.
        """
        return await self.request("GET", f"invites/{invite_code}")

    async def delete_invite(self, invite_code: str):
        """
        Deletes an invite.

        Parameters
        ----------
        invite_code: :class:`str`
            The code of the invite.
        """
        return await self.request("DELETE", f"invites/{invite_code}")

    async def handle_attachment(self, attachment_data: Union[str, File]) -> str:
        """
        Handles an attachment.

        Parameters
        ----------
        attachment_data: Union[:class:`str`, :class:`File`]
            The attachment data.

        Returns
        -------
        :class:`str`
            The attachment's id.
        """
        if isinstance(attachment_data, File):
            return await attachment_data.get_id(self)
        else:
            return attachment_data

    async def handle_embed(self, embed_data: Union[SendableEmbedPayload, SendableEmbed]) -> SendableEmbedPayload:
        """
        Handles an embed.

        Parameters
        ----------
        embed_data: Union[:class:`SendableEmbedPayload`, :class:`SendableEmbed`]
            The embed data.

        Returns
        -------
        :class:`SendableEmbedPayload`
            The embed as a dict.
        """
        if isinstance(embed_data, SendableEmbed):
            return await embed_data.to_dict(self)
        else:
            return embed_data
