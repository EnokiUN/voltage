from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import FilePayload

RelationPayload = Literal["Block", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]


class UserBotPayload(TypedDict):
    owner: str


class StatusPayload(TypedDict):
    text: NotRequired[str]
    presence: NotRequired[Literal["Busy", "Idle", "Online", "Invisible"]]


class UserRelationPayload(TypedDict):
    status: RelationPayload
    _id: str


class UserPayload(TypedDict):
    _id: str
    username: str
    avatar: NotRequired[FilePayload]
    bot: NotRequired[UserBotPayload]
    relations: NotRequired[List[UserRelationPayload]]
    badges: NotRequired[int]
    status: NotRequired[StatusPayload]
    online: NotRequired[bool]
    relationship: NotRequired[UserRelationPayload]
    flags: NotRequired[int]


class UserProfilePayload(TypedDict):
    content: NotRequired[str]
    background: NotRequired[FilePayload]
