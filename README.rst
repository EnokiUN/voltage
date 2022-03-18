-------
Voltage
-------

A Simple Pythonic Asynchronous API wrapper for Revolt.

An example payload bot:

.. code-block:: python3

    import voltage

    client = voltage.Client()

    @client.listen('ready', raw=True)
    async def on_ready(payload):
        print("Started bot!")

    @client.listen('message', raw=True)
    async def on_message(payload):
        if payload['content'] == 'ping':
            await client.send_message(payload['channel'], 'pong')
        if payload['content'] == 'embed':
            embed = voltage.new_embed(title="Hello World", description="This is an embed")
            await client.send_message(payload['channel'], content="Hi", embed=[embed]) # Adding content since it's required by revolt.

    client.run("TOKEN")

============
Installation
============

Voltage is available on `pypi <https://pypi.org/project/voltage>`_! 

To install voltage just run:

.. code-block:: sh

    $ pip install voltage

If you want to install the main branch which may have more features but will be more unstable you run:

.. code-block:: sh

    $ pip install git+https://github.com/EnokiUN/voltage``

note: installing from github requires the git cli to be available on your machine.
