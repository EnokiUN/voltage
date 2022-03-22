-------
Voltage
-------

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
