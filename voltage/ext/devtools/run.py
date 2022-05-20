from ast import AsyncFunctionDef, increment_lineno, parse
from time import time

from voltage import File, SendableEmbed

from ..commands import CommandContext, command, is_owner


async def async_eval(ctx: CommandContext, code: str):
    # https://stackoverflow.com/a/60934327
    globs = globals().copy()
    env = {
        "_ctx": ctx,
        "_message": ctx.message,
        "_msg": ctx.message,
        "_author": ctx.author,
        "_client": ctx.client,
        "_channel": ctx.channel,
        "_server": ctx.server,
        "_me": ctx.me,
    }

    for k, v in env.items():
        globs[k] = v

    lines = code.splitlines()

    if lines[-1].lstrip() == lines[-1]:
        lines[-1] = f"return {lines[-1]}"

    code = "\n".join(lines)

    parsed = parse(code)
    parsedfn = parse("async def __voltage__eval(): return")

    for line in parsed.body:
        increment_lineno(line)

    if isinstance(parsedfn.body[0], AsyncFunctionDef):
        parsedfn.body[0].body = parsed.body  # Set the function's body to the supplied code.
    else:
        raise RuntimeError("Error contucting code for evaluation")

    exec(compile(parsedfn, "<ast>", "exec"), globs)  # nosec
    return await eval("__voltage__eval()", globs)  # nosec


@is_owner()  # I'll leave validation up to the user. # sike.
@command(name="py", aliases=["eval"])
async def py_cmd(ctx, *, code: str):
    """Asynchronously executes python code.
    This command is dangerous and should only be used by the owner as it provides no type of sandboxing.
    """
    start = time()
    try:
        res = await async_eval(ctx, code)
    except Exception as e:
        return await ctx.reply(f"Oh no, an error occured while evaluating:\n{e}")
    else:
        if res is None:
            return await ctx.reply(f"Finished in {time() - start:.2f}s :thumbsup:")
        # TODO: make this work for lists of objects too.
        if isinstance(res, SendableEmbed):
            sendcoro = ctx.reply("[]()", embed=res)
        elif isinstance(res, File):
            sendcoro = ctx.reply(attachment=res)
        else:
            res = str(res).replace(ctx.client.http.token, "[TOKEN REDACTED]")
            if len(res) > 2000:
                res = f"{res[:1997]}..."
            sendcoro = ctx.reply(res)

        await sendcoro
