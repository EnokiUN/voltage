from typing import Optional, Dict, Literal, Union, List, Any
from aiohttp import ClientSession

class HttpHandler:
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
    def __init__(self, client: ClientSession, token: str, api_url: Optional[str]="https://api.revolt.chat/"):
        """
        description here
        """
        self.client = client
        self.token = token
        self.api_url = api_url

    async def request(self, method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], url: str, auth: Optional[bool]=True, **kwargs):
        header = {
            "User-Agent": "Pyvolt (beta)",
            "Content-Type": "application/json"
        }
        if auth:
            header["x-bot-token"] = self.token
        async with self.client.request(method, self.api_url + url, headers=header, **kwargs) as req:
            if 200 >= req.status <= 300:
                return await req.json()
            raise(Exception(f"Error sending request: {req.status}"))

    async def query_node(self):
        """
        Gets info about the API.
        """
        return await self.request("GET", "")

    async def fetch_user(self, user_id: str):
        """
        Gets info about a user.

        Parameters
        ----------
        user_id: str
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/")

    async def edit_user(self, status: Optional[Dict[str, Union[str, Literal["Busy", "Idle", "Invisible", "Online"]]]]=None, profile: Optional[Dict[str, str]]=None, avatar: Optional[str]=None, remove: Optional[Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]]=None):
        """
        Edits the bot's profile.

        Parameters
        ----------
        status: Optional[Dict[str, Union[str, Literal["Busy", "Idle", "Invisible", "Online"]]]]
            The new status of the bot.
        profile: Optional[Dict[str, str]]
            The new profile of the bot.
        avatar: Optional[str]
            The new avatar of the bot.
        remove: Optional[Literal["Avatar", "ProfileBackground", "ProfileContent", "StatusText"]]
            The thing to remove from the bot.
        """
        data = {}
        if status:
            data["status"] = status
        if profile:
            data["profile"] = profile
        if avatar:
            data["avatar"] = avatar
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", "users/me/", json=data)

    async def fetch_self(self):
        """
        Gets info about the bot.
        """
        return await self.request("GET", "users/@me/")

    async def fetch_user_profile(self, user_id: str):
        """
        Gets the profile of a user.

        Parameters
        ----------
        user_id: str
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/profile/")

    async def fetch_default_avatar(self, user_id: str):
        """
        Gets the default avatar of a user.

        Parameters
        ----------
        user_id: str
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/default_avatar/")

    async def fetch_mutual(self, user_id: str):
        """
        Gets the mutual friends of a user.

        Parameters
        ----------
        user_id: str
            The id of the user.
        """
        return await self.request("GET", f"users/{user_id}/mutual/")

    async def fetch_dms(self):
        """
        Gets all the direct messages and group dms a bot is in.
        """
        return await self.request("GET", "users/dms/")

    async def open_dm(self, user_id: str):
        """
        Opens a direct message with a user.

        Parameters
        ----------
        user_id: str
            The id of the user.
        """
        return await self.request("POST", f"users/{user_id}/dm/")
        
    async def fetch_channel(self, channel_id: str):
        """
        Gets info about a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        """
        return await self.request("GET", f"channels/{channel_id}/")
    
    async def edit_channel(self, channel_id: str, name: Optional[str]=None, description: Optional[str]=None, icon: Optional[str]=None, nsfw: Optional[bool]=None, remove: Optional[Literal["Description", "Icon"]]=None):
        """
        Edits a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        name: Optional[str]
            The new name of the channel.
        description: Optional[str]
            The new description of the channel.
        icon: Optional[str]
            The new icon of the channel.
        nsfw: Optional[bool]
            Whether the channel is nsfw or not.
        remove: Optional[Literal["Description", "Icon"]]
            The thing to remove from the channel.
        """
        data = {}
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
        return await self.request("PATCH", f"channels/{channel_id}/", json=data)
    
    async def close_channe(self, channel_id: str):
        """
        Depending on the type of channel, deleted it if it's a server channel, leaves it if it's a group channel and closes it if it's a dm.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        """
        return await self.request("DELETE", f"channels/{channel_id}/")

    async def create_invite(self, channel_id: str):
        """
        Creates an invite for a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        """
        return await self.request("POST", f"channels/{channel_id}/invites/")

    async def set_role_perms(self, channel_id: str, role_id: str, permission: int):
        """
        Sets the permissions of a role in a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        role_id: str
            The id of the role.
        permission: int
            The permission to set.
        """
        return await self.request("PUT", f"channels/{channel_id}/permissions/{role_id}/", json={"permissions": permission})

    async def set_default_perms(self, channel_id: str, permission: int):
        """
        Sets the default permissions of a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        permission: int
            The permission to set.
        """
        return await self.request("PUT", f"channels/{channel_id}/permissions/default/", json={"permissions": permission})

    async def send_message(self, channel_id: str, content: str, attachments: Optional[List[str]]=None, embeds: Optional[List[Dict[str, str]]]=None, replies: Optional[List[Dict[str, Union[str, bool]]]]=None, masquerade: Optional[Dict[str, str]]=None):
        """
        Sends a message to a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        content: str
            The content of the message.
        attachments: Optional[List[str]]
            The attachments of the message.
        embeds: Optional[List[Dict[str, str]]]
            The embeds of the message.
        replies: Optional[List[Dict[str, Union[str, bool]]]]
            The replies of the message.
        masquerade: Optional[Dict[str, str]]
            The masquerade of the message.
        """
        data = {"content": content}
        if attachments:
            data["attachments"] = attachments
        if embeds:
            for embed in embeds:
                embed["type"] = "text"
            data["embeds"] = embeds
        if replies:
            data["replies"] = replies
        if masquerade:
            data["masquerade"] = masquerade
        return await self.request("POST", f"channels/{channel_id}/messages/", json=data)

    async def fetch_messages(self, channel_id: str, sort: Literal["Latest", "Oldest"], limit: Optional[int]=None, before: Optional[str]=None, after: Optional[str]=None, nearby: Optional[str]=None, include_users: Optional[bool]=None):
        """
        Gets messages from a channel.

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
        data = {"sort": sort}
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
        return await self.request("GET", f"channels/{channel_id}/messages/", params=data)

    async def fetch_message(self, channel_id: str, message_id: str):
        """
        Gets a message from a channel.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        message_id: str
            The id of the message.
        """
        return await self.request("GET", f"channels/{channel_id}/messages/{message_id}/")

    async def edit_message(self, channel_id: str, message_id: str, content: str, embeds: Optional[List[Dict[str, str]]]=None):
        """
        Edits a message.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        message_id: str
            The id of the message.
        content: str
            The content of the message.
        embeds: Optional[List[Dict[str, str]]]
            The embeds of the message.
        """
        data = {"content": content}
        if embeds:
            for embed in embeds:
                embed["type"] = "text"
            data["embeds"] = embeds
        return await self.request("PATCH", f"channels/{channel_id}/messages/{message_id}/", json=data)

    async def delete_message(self, channel_id: str, message_id: str):
        """
        Deletes a message.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        message_id: str
            The id of the message.
        """
        return await self.request("DELETE", f"channels/{channel_id}/messages/{message_id}/")

    async def poll_message_changed(self, channel_id: str, ids: List[str]):
        """
        Polls for a message change.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        ids: List[str]
            The ids of the messages.
        """
        return await self.request("GET", f"channels/{channel_id}/messages/changed/", params={"ids": ",".join(ids)})

    async def search_for_message(self, channel_id: str, query: str, limit: Optional[int]=None, before: Optional[str]=None, after: Optional[str]=None, sort: Optional[Literal["Latest", "Oldest", "Relevance"]]=None, include_users: Optional[bool]=None):
        """
        Searches for a message.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        query: str
            The query of the message.
        limit: Optional[int]
            The limit of the messages.
        before: Optional[str]
            The id of the message to fetch before.
        after: Optional[str]
            The id of the message to be fetched after.
        sort: Optional[Literal["Latest", "Oldest", "Relevance"]]
            The way of sorting the messages.
        include_users: Optional[bool]
            Whether to include the users in the messages.
        """
        data = {"query": query}
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
        return await self.request("GET", f"channels/{channel_id}/messages/search/", params=data)

    async def fetch_group_members(self, channel_id: str):
        """
        Gets the members of a group.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        """
        return await self.request("GET", f"channels/{channel_id}/members/")

    async def join_call(self, channel_id: str):
        """
        Joins a call.

        Parameters
        ----------
        channel_id: str
            The id of the channel.
        """
        return await self.request("POST", f"channels/{channel_id}/join_call/")

    async def fetch_server(self, server_id: str):
        """
        Gets info about a server.

        Parameters
        ----------
        server_id: str
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/")

    async def edit_server(self, server_id: str, name: Optional[str]=None, description: Optional[str]=None, icon: Optional[str]=None, banner: Optional[str]=None, categories: Optional[List[Dict[str, str]]]=None, system_messages: Optional[Dict[str, str]]=None, nsfw: Optional[bool]=None, remove: Optional[Literal["Banner", "Description", "Icon"]]=None):
        """
        Edits a server.

        Parameters
        ----------
        server_id: str
            The id of the server.
        name: Optional[str]
            The name of the server.
        description: Optional[str]
            The description of the server.
        icon: Optional[str]
            The icon of the server.
        banner: Optional[str]
            The banner of the server.
        categories: Optional[List[Dict[str, str]]]
            The categories of the server.
        system_messages: Optional[Dict[str, str]]
            The system messages of the server.
        nsfw: Optional[bool]
            Whether the server is nsfw.
        remove: Optional[Literal["Banner", "Description", "Icon"]]
            The field to remove.
        """
        data = {}
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
        return await self.request("PATCH", f"servers/{server_id}/", json=data)

    async def delete_server(self, server_id: str):
        """
        Deletes a server if you own it, otherwise leave it.

        Parameters
        ----------
        server_id: str
            The id of the server.
        """
        return await self.request("DELETE", f"servers/{server_id}/")

    async def create_channel(self, server_id: str, type: Literal["Text", "Voice"], name: str, description: Optional[str]=None, nsfw: Optional[bool]=None):
        """
        Creates a channel.

        Parameters
        ----------
        server_id: str
            The id of the server.
        type: Literal["Text", "Voice"]
            The type of the channel.
        name: str
            The name of the channel.
        description: Optional[str]
            The description of the channel.
        nsfw: Optional[bool]
            Whether the channel is nsfw.
        """
        data = {"type": type, "name": name}
        if description:
            data["description"] = description
        if nsfw:
            data["nsfw"] = nsfw
        return await self.request("POST", f"servers/{server_id}/channels/", json=data)

    async def  fetch_invites(self, server_id: str):
        """
        Gets the invites of a server.

        Parameters
        ----------
        server_id: str
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/invites/")

    async def fetch_member(self, server_id: str, member_id: str):
        """
        Gets info about a member.

        Parameters
        ----------
        server_id: str
            The id of the server.
        member_id: str
            The id of the member.
        """
        return await self.request("GET", f"servers/{server_id}/members/{member_id}/")

    async def edit_member(self, server_id: str, member_id: str, nickname: Optional[str]=None, avatar: Optional[str]=None, roles: Optional[List[str]]=None, remove: Optional[Literal["Avatar", "Nickname"]]=None):
        """
        Edits a member.

        Parameters
        ----------
        server_id: str
            The id of the server.
        member_id: str
            The id of the member.
        nickname: Optional[str]
            The nickname of the member.
        avatar: Optional[str]
            The avatar of the member.
        roles: Optional[List[str]]
            The roles of the member.
        remove: Optional[Literal["Avatar", "Nickname"]]
            The field to remove.
        """
        data = {}
        if nickname:
            data["nick"] = nickname
        if avatar:
            data["avatar"] = avatar
        if roles:
            data["roles"] = roles
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"servers/{server_id}/members/{member_id}/", json=data)

    async def kick_member(self, server_id: str, member_id: str):
        """
        Kicks a member.

        Parameters
        ----------
        server_id: str
            The id of the server.
        member_id: str
            The id of the member.
        """
        return await self.request("DELETE", f"servers/{server_id}/members/{member_id}/")

    async def ban_member(self, server_id: str, member_id: str, reason: Optional[str]=None):
        """
        Bans a member.

        Parameters
        ----------
        server_id: str
            The id of the server.
        member_id: str
            The id of the member.
        reason: Optional[str]
            The reason of the ban.
        """
        data = {}
        if reason:
            data["reason"] = reason
        return await self.request("PUT", f"servers/{server_id}/bans/{member_id}/", json=data)

    async def unban_member(self, server_id: str, member_id: str):
        """
        Unbans a member.

        Parameters
        ----------
        server_id: str
            The id of the server.
        member_id: str
            The id of the member.
        """
        return await self.request("DELETE", f"servers/{server_id}/bans/{member_id}/")

    async def fetch_bans(self, server_id: str):
        """
        Gets the bans of a server.

        Parameters
        ----------
        server_id: str
            The id of the server.
        """
        return await self.request("GET", f"servers/{server_id}/bans/")

    async def set_role_permission(self, server_id: str, role_id: str, permissions: Dict[str, int]):
        """
        Sets the permissions of a role.

        Parameters
        ----------
        server_id: str
            The id of the server.
        role_id: str
            The id of the role.
        permissions: Dict[str, int]
            The permissions of the role.
        """
        return await self.request("PUT", f"servers/{server_id}/roles/{role_id}/", json={"permissions": permissions})

    async def set_default_permissions(self, server_id: str, permissions: Dict[str, int]):
        """
        Sets the default permissions of a server.

        Parameters
        ----------
        server_id: str
            The id of the server.
        permissions: Dict[str, int]
            The permissions of the server.
        """
        return await self.request("PUT", f"servers/{server_id}/default_role/", json={"permissions": permissions})

    async def create_role(self, server_id: str, name: str):
        """
        Creates a role.

        Parameters
        ----------
        server_id: str
            The id of the server.
        name: str
            The name of the role.
        """
        return await self.request("POST", f"servers/{server_id}/roles/", json={"name": name})

    async def edit_role(self, server_id: str, role_id: str, name: str, colour: Optional[str]=None, hoist: Optional[bool]=None, rank: Optional[int]=None, remove: Optional[Literal["Colour"]]=None):
        """
        Edits a role.

        Parameters
        ----------
        server_id: str
            The id of the server.
        role_id: str
            The id of the role.
        name: str
            The name of the role.
        colour: Optional[str]
            The colour of the role.
        hoist: Optional[bool]
            Whether the role is hoisted.
        rank: Optional[int]
            The rank of the role.
        remove: Optional[Literal["Colour"]]
            The field to remove.
        """
        data = {"name": name}
        if colour:
            data["color"] = colour
        if hoist:
            data["hoist"] = hoist
        if rank:
            data["position"] = rank
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f"servers/{server_id}/roles/{role_id}/", json=data)

    async def delete_role(self, server_id: str, role_id: str):
        """
        Deletes a role.

        Parameters
        ----------
        server_id: str
            The id of the server.
        role_id: str
            The id of the role.
        """
        return await self.request("DELETE", f"servers/{server_id}/roles/{role_id}/")

    async def fetch_invite(self, invite_code: str):
        """
        Gets info about an invite.

        Parameters
        ----------
        invite_code: str
            The code of the invite.
        """
        return await self.request("GET", f"invites/{invite_code}/")

    async def delete_invite(self, invite_code: str):
        """
        Deletes an invite.

        Parameters
        ----------
        invite_code: str
            The code of the invite.
        """
        return await self.request("DELETE", f"invites/{invite_code}/")