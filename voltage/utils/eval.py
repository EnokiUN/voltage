from __future__ import annotations

from re import sub
from typing import TYPE_CHECKING, Optional

import voltage

if TYPE_CHECKING:
    from .. import Client
    from ..internals import HTTPHandler
    from ..types import MessagePayload


async def eval(client: Client, message: MessagePayload, superuser_ids: list[str], message_start: str = "!eval"):
    """
    A function that provides a very basic asynchronous eval function.
    DANGER: THIS FUNCTION CAN PUT YOUR HOST MACHINE IN DANGER SO BE CAREFUL OF WHO USES IT AND HOW IT IS USED.

    Parameters
    ----------
    client: pyvolt.Client
        The client object.
    message: pyvolt.types.MessagePayload
        The raw message object to eval (mainly because a non raw one hasn't been added yet).
    supeuser_ids: List[:class:`str`]
        The id's of people who are supposed to have eval access.
    message_start: :class:`str`
        The expected start of the message with the prefix included. (ex "!eval")
        Defaults to "!eval".
    """
    if not isinstance(message["content"], str):
        return
    if message["content"].startswith(message_start):
        if message["author"] not in superuser_ids:
            return await client.http.send_message(message["channel"], "You don't have access to this command.")
        if not (parts := message["content"].split(" ", 1)) or not (len(parts) > 1):
            return await client.http.send_message(
                message["channel"],
                f"Usage: {message_start} <code>\nYou also have to be a superuser to use this command.",
            )
        content = parts[1]
        content = sub("```python|```py|```", "", content)
        lines = content.splitlines()
        lines = [line.strip() for line in lines if line]
        if not lines[-1].startswith("    "):
            lines[-1] = "return " + lines[-1]
        cmd = "async def __eval__func(client, payload, http):\n    " + "\n    ".join(lines)
        exec(cmd)  # nosec
        try:
            res = await locals()["__eval__func"](client, message, client.http)
            if res:
                await client.http.send_message(
                    message["channel"], str(res).replace(client.http.token, "[TOKEN REDACTED]")
                )
        except Exception as e:
            await client.http.send_message(message["channel"], f"Error: {e}")
