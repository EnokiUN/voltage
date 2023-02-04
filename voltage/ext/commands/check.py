from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

from voltage import BotNotEnoughPerms, Member, NotBotOwner, NotEnoughPerms, User

if TYPE_CHECKING:
    from .command import Command, CommandContext


class Check:
    """
    A class which represent's a command pre-invoke check.

    If a check returns ``False``, the command will not be invoked.

    Alternatively, if a check raises an error the command will also not be invoked.

    Checks are ran in parallel using ``asyncio.gather``.
    """

    def __init__(
        self,
        func: Callable[..., Awaitable[Callable[[CommandContext], Awaitable[bool]]]],
    ) -> None:
        self.func = func
        self.args: tuple[Any, ...] = ()
        self.kwargs: dict[str, Any] = {}

    async def check(self, context: CommandContext) -> bool:
        check = await self.func(*self.args, **self.kwargs)
        return await check(context)

    def __call__(self, *args, **kwargs):
        def inner(command: Command):
            self.args = args
            self.kwargs = kwargs
            command.checks.append(self)
            return command

        return inner


def check(func: Callable[..., Awaitable[Callable[[CommandContext], Awaitable[bool]]]]) -> Check:
    """
    A decorator which creates a check from a function.
    """
    return Check(func)


@check
async def is_owner() -> Callable[[CommandContext], Awaitable[bool]]:
    """
    Checks if the user invoking the command is the bot owner.
    """

    async def check(ctx: CommandContext) -> bool:
        return ctx.author.id == ctx.client.user.owner_id

    return check


@check
async def is_server_owner() -> Callable[[CommandContext], Awaitable[bool]]:
    """
    Checks if the user invoking the command is the server owner.
    """

    async def check(ctx: CommandContext) -> bool:
        if not ctx.server:
            return False
        return ctx.author.id == ctx.server.owner_id

    return check


@check
async def has_perms(**kwargs) -> Callable[[CommandContext], Awaitable[bool]]:
    """
    Checks if the user invoking the command has the required perms.
    """

    async def check(ctx: CommandContext) -> bool:
        if isinstance(ctx.author, User):
            return True
        for permission, state in kwargs.items():
            if state:
                if not hasattr(ctx.author.permissions, permission):
                    raise ValueError(f"Permission {permission} does not exist")
                if not getattr(ctx.author.permissions, permission):
                    raise NotEnoughPerms(ctx.author, permission)
        return True

    return check


@check
async def bot_has_perms(**kwargs) -> Callable[[CommandContext], Awaitable[bool]]:
    """
    Checks if bot has the required perms in that channel.
    """

    async def check(ctx: CommandContext) -> bool:
        if not isinstance(ctx.me, Member):
            return True
        for permission, state in kwargs.items():
            if state:
                if not hasattr(ctx.me.permissions, permission):
                    raise ValueError(f"Permission {permission} does not exist")
                if not getattr(ctx.me.permissions, permission):
                    raise BotNotEnoughPerms(permission)
        return True

    return check
