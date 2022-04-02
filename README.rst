-------
Voltage
-------

|Support Server| |PyPi| |Docs| |Checks|

A simple, pythonic, and asynchronous API wrapper for `Revolt. <https://revolt.chat>`_

|Screenshot|

=====
Usage
=====

.. code-block:: python3

    import voltage  # Import voltage.

    client = voltage.Client()  # Initialize the client.


    @client.listen("ready")  # Listen to an event.
    async def on_ready():
        print(f"Logged in as {client.user}")


    @client.listen("message")
    async def on_message(message):  # Doesn't matter what you call the function.
        if message.content == "-ping":
            await message.channel.send("pong!")  # Send a message.
        elif message.content == "-embed":
            embed = voltage.SendableEmbed(title="Hello World", description="This is an embed")  # Create an embed.
            # Reply to a message.
            await message.reply(content="embed", embed=embed)  # Obligatory message content.


    # Run the client which is an abstraction of calling the start coroutine.
    client.run("TOKEN")  # Replace with your token.

For more examples check the `examples <https://github.com/EnokiUN/voltage/tree/main/examples>`_ folder which has a lot of useful, ready to go, and explained examples.

You can also read the code of `RedCrewmate <https://github.com/EnokiUN/redcrewmatw>`_. RedCrewmate also contains a framework for commands and cogs.

============
Installation
============

Voltage is available on `PyPI <https://pypi.org/project/voltage>`_! 

To install voltage just run:

.. code-block:: sh

    $ pip install voltage

If you want to install the main branch which may have more features but will be more unstable you run:

.. code-block:: sh

    $ pip install git+https://github.com/EnokiUN/voltage

.. note::
    Python 3.8 or higher is required to install voltage.

    Installing from GitHub requires the Git CLI to be available on your machine.

=======
Credits
=======

    - **Contributors**, thank you :)

    - `Revolt.py <https://github.com/revoltchat/revolt.py>`_, when shit broke, that's where I went.

    - `Revolt.js <https://github.com/revoltchat/revolt.js>`_, when the docs fail you.

    - `Discord.py <https://github.com/Rapptz/discord.py>`_, also a really great help while making this.

    - **Revolt development team**, absolute chads.

.. |Support Server| image:: https://img.shields.io/badge/dynamic/json?color=ff4655&labelColor=111823&label=Support%20Server&query=member_count&suffix=%20Members&url=https%3A%2F%2Fapi.revolt.chat%2Finvites%2Fbwtscg1F&style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAABiElEQVQoFYVSO0sDQRCefVzUXCI+wGClWPoHrISIlaSy8a9Y2mplYyP2gq21f0ArBSWgRTAi0UgkkJh77q0z4545UHHg25nvm5nbud0V75vbkJvAIMyynLK3uAaZgYdgBDPag4v3N9Z1oWoXY4XoOI2+Q30DxL1DiJ5NzyqqZdvndcydTM6DlYlJezkc1JDwlrKQ/S8Ua5XqKxbxTrqTJHlDZdHzhjlpx9E6ztmdlqo+q/Wx08XW/EIV476eEvQrPw3VFjY+d9Mkw8bvAl9JJlr80ehL1QABg6XSxGne9ZFlZy+JocMC/ft+AHPj8bgvsfaub9JDJBE3ZnzinPvrG5x8iqOduzBsMsFF3gQBOJRykfxjHDWKvKa9DeR0r2wywJfi8H2hXyl762rY+Uod+QBlBBAkzZeDK9yiQZhWFC0XtdWyX49RIEh6mQ4Gw3wUi4eRXo0+2gNj9lAnszXPO0dfIaJ7aUqerH8djGqTQnoWbDo0poeabYbBQVWpEwFCpDYzeH0BFX8CUB2RWiqWVAgAAAAASUVORK5CYII=
    :target: https://rvlt.gg/bwtscg1F
    :alt: Revolt Support Server
.. |PyPi| image:: https://img.shields.io/pypi/v/voltage.svg?labelColor=111823&logo=pypi&logoColor=white&style=for-the-badge
    :target: https://pypi.org/project/voltage
    :alt: PyPi Page.
.. |Docs| image:: https://img.shields.io/readthedocs/revolt-voltage/latest?labelColor=111823&style=for-the-badge&logo=readthedocs&logoColor=white
    :alt: Docs Status
    :target: https://revolt-voltage.readthedocs.io/
.. |Checks| image:: https://img.shields.io/github/workflow/status/EnokiUN/Voltage/mypy?label=checks&labelColor=111823&logo=github&style=for-the-badge
    :alt: GitHub Workflow Status
.. |Logo| image:: https://github.com/EnokiUN/voltage/blob/main/assets/voltage.png
    :alt: Voltage Logo
    :width: 80
.. |Screenshot| image:: https://github.com/EnokiUN/voltage/blob/main/assets/ss.jpg
    :alt: Screenshot Of Starting A Bot.
