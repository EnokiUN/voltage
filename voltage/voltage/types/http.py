from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, TypedDict

if TYPE_CHECKING:
    from .message import MessagePayload
    from .server import MemberPayload
    from .user import UserPayload

BaseRequestReturnPayload = Dict[Any, Any]


class ApiFeaturePayload(TypedDict):
    enabled: bool
    url: str


class VosoFeaturePayload(TypedDict):
    ws: str


class FeaturesPayload(TypedDict):
    email: bool
    invite_only: bool
    captcha: ApiFeaturePayload
    autumn: ApiFeaturePayload
    voso: VosoFeaturePayload
    january: ApiFeaturePayload


class ApiInfoPayload(TypedDict):
    revolt: str
    features: FeaturesPayload
    ws: str
    app: str
    vapid: str


class AutumnPayload(TypedDict):
    id: str


class GetServerMembersPayload(TypedDict):
    members: List[MemberPayload]
    users: List[UserPayload]


class MessageWihUserDataPayload(TypedDict):
    messages: List[MessagePayload]
    users: List[UserPayload]
    member: List[MemberPayload]
