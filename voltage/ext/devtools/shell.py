from asyncio import get_running_loop
from os import getenv
from subprocess import PIPE, Popen
from sys import platform
from typing import Any, Awaitable, Callable

from ..commands import CommandContext, command, is_owner
from voltage import Message


class Shell:
    """A simple class that executes a shell command sending it's output through a function"""

    def __init__(self, command: str):
        self.command = command
        self.process: Popen[bytes]
        self.loop = get_running_loop()

    def handle_stdout(self, callback: Callable[[str], Awaitable[Any]], *args, **kwargs):
        stdout = self.process.stdout
        if stdout is None:
            raise RuntimeWarning("Process doesn't have an stdout")
        for c in iter(lambda: stdout.readline(), b""):
            self.loop.call_soon_threadsafe(self.loop.create_task, callback(c.decode("UTF-8"), *args, *kwargs))

    def handle_stderr(self, callback: Callable[[str], Awaitable[Any]], *args, **kwargs):
        stderr = self.process.stderr
        if stderr is None:
            raise RuntimeWarning("Process doesn't have an stderr")
        for c in iter(lambda: stderr.readline(), b""):
            self.loop.call_soon_threadsafe(self.loop.create_task, callback(c.decode("UTF-8"), *args, *kwargs))

    async def run(self, callback: Callable[[str], Awaitable[Any]], *args, **kwargs):
        """The fucntion that actually calls the command."""
        start = [getenv("SHELL") or "/bin/bash", "-c"] if platform != "win32" else ["cmd", "/c"]
        self.process = Popen([*start, self.command], stdout=PIPE, stderr=PIPE)
        self.loop.run_in_executor(None, self.handle_stdout, callback, *args, **kwargs)
        f = self.loop.run_in_executor(None, self.handle_stderr, callback, *args, **kwargs)
        await f


class ShellContext:
    """A context for the shell command.

    Attributes
    ==========
    ctx: :cls:`CommandContext`
        The context of the command.
    shell: :cls:`shell`
        The shell for running a command.
    update: :cls:`int`
        The number of lines the output message should update after.
    """

    __slots__ = ("ctx", "shell", "update", "out", "index", "msg")

    def __init__(self, ctx: CommandContext, shell: Shell, update=10):
        self.ctx = ctx
        self.shell = shell
        self.update = update
        self.out = ""
        self.index = 0

        self.msg: Message

    async def handle_out(self, out):
        self.out += out
        if len(self.out) > 1994:  # triple back tics
            while len(self.out) > 1994:
                self.out = "\n".join(self.out.splitlines()[1:])
        self.index += 1
        if self.index % self.update == 0:
            await self.msg.edit(f"```\n{self.out.strip()}\n```")

    async def start(self):
        self.msg = await self.ctx.reply("Waiting for output...")
        await self.shell.run(self.handle_out)
        if self.index % self.update != 0:
            await self.msg.edit(f"```\n{self.out.strip()}\n```")


@is_owner()
@command()
async def sh(ctx, *, cmd: str):
    shell = Shell(cmd)
    shctx = ShellContext(ctx, shell)
    await shctx.start()
    await ctx.reply("Done.")
