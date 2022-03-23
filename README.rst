-------
Voltage
-------

.. image:: https://img.shields.io/badge/dynamic/json?labelColor=ff4655&color=111823&label=Support%20Server&query=member_count&suffix=%20Members&url=https%3A%2F%2Fapi.revolt.chat%2Finvites%2Fbwtscg1F&style=for-the-badge&logo=python&logoColor=white
   :target: https://api.revolt.chat/invites/bwtscg1F
   :alt: Revolt Support Server

A Simple Pythonic Asynchronous API wrapper for Revolt.

An example bot:

.. code-block:: python3

    import voltage

    client = voltage.Client()

    @client.listen('ready')
    async def on_ready(payload):
        print(f"Logged in as {client.user}")

    @client.listen('message')
    async def on_message(message): # doesn't matter what you call the function.
        if message.content == '-ping':
            await message.channel.send('pong!')
        if message.content == '-embed':
            embed = voltage.SendableEmbed(title="Hello World", description="This is an embed")
            await message.reply(content="embed", embed=embed) # Obligatory message content.

    client.run("TOKEN")

============
Installation
============

Voltage is available on `PyPI <https://pypi.org/project/voltage>`_! 

To install voltage just run:

.. code-block:: sh

    $ pip install voltage

If you want to install the main branch which may have more features but will be more unstable you run:

.. code-block:: sh

    $ pip install git+https://github.com/EnokiUN/voltage``

.. note::
    Python 3.8 or higher is required to install voltage.

    Installing from GitHub requires the git cli to be available on your machine.
