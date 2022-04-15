from __future__ import annotations
from typing import TYPE_CHECKING, Type, Callable, Awaitable, Any
from re import compile
from voltage import get, UserNotFound, MemberNotFound, ChannelNotFound, RoleNotFound

if TYPE_CHECKING:
    from .command import CommandContext
    from voltage import User, Member, Channel, Role

class Converter:
    """
    Base class that all converters inherit from.

    The only important method is the `convert` method, which takes a context and a string then returns an object.
    """
    async def convert(self, ctx: CommandContext, arg: str):
        """
        Convert a string into an object.

        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Converter.convert must be overridden by subclasses")


class StrConverter(Converter):
    """
    A converter that converts a string into a string.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> str:
        return arg

class IntConverter(Converter):
    """
    A converter that converts a string into an integer.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> int:
        return int(arg)

class FloatConverter(Converter):
    """
    A converter that converts a string into a float.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> float:
        return float(arg)

id_regex = compile(r"[0-9A-HJ-KM-NP-TV-Z]{26}")

class UserConverter(Converter):
    """
    A converter that converts a string into a user.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> User:
        if match := id_regex.match(arg):
            return ctx.client.cache.get_user(match.group(0))
        arg = arg.replace("@", "").lower()
        if user := get(ctx.client.cache.users.values(), lambda u: u.name.lower() == arg):
            return user
        raise UserNotFound(arg)

class MemberConverter(Converter):
    """
    A converter that converts a string into a member.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> Member:
        if ctx.server is None:
            raise ValueError("Cannot convert a member to a member without a server")
        if match := id_regex.search(arg):
            return ctx.client.cache.get_member(ctx.server.id, match.group(0))
        arg = arg.replace("@", "").lower()
        if member := get(ctx.client.cache.members[ctx.server.id].values(), lambda m: m.name.lower() == arg):
            return member
        if member := get(ctx.client.cache.members[ctx.server.id].values(), lambda m: m.nickname.lower() == arg if m.nickname else False):
            return member
        raise MemberNotFound(arg)

class ChannelConverter(Converter):
    """
    A converter that converts a string into a channel.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> Channel:
        if match := id_regex.match(arg):
            return ctx.client.cache.get_channel(match.group(0))
        arg = arg.replace("#", "").lower()
        if channel := get(ctx.client.cache.channels.values(), lambda c: c.name.lower() == arg if c.name else False):
            return channel
        raise ChannelNotFound(arg)

class RoleConverter(Converter):
    """
    A converter that converts a string into a role.
    """
    async def convert(self, ctx: CommandContext, arg: str) -> Role:
        if ctx.server is None:
            raise ValueError("Cannot convert a role to a role without a server")
        if match := id_regex.match(arg):
            if role := ctx.server.get_role(match.group(0)):
                return role
        arg = arg.replace("@", "").lower()
        if role := get(ctx.server.roles, lambda r: r.name.lower() == arg):
            return role
        raise RoleNotFound(arg)


def converter(converter: Callable[[CommandContext, str], Awaitable[Any]]) -> Type[Converter]:
    """
    A decorator that converts a function into a converter.
    """
    class Wrapper(Converter):
        converter = converter
    return Wrapper
