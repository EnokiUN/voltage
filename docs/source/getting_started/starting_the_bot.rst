Starting The Bot
----------------

So you installed the library and have your bot token ready, great!

Now I'd suggest you make a folder and then make a file called ``main.py`` or ``bot.py`` or whatever you want to call your main script file but before that we need to get our enviroment set up (or that's atleast what I'd do) so go ahead and install ``python-dotenv`` if you haven't already using this command:

.. code-block:: console
    
    $ pip install python-dotenv

Nice, now add your token to your ``.env`` file, it should be in the same folder as your script file.

Let's say that your token is ``qwertyuiop1234567890`` and you want to put it in your ``.env`` file, you'd do this:

.. code-block:: env

   TOKEN=qwertyuiop1234567890

Cool, now open your main script file and write the following, I'll explain it all in just a second:

.. code-block:: python3

    import dotenv
    import voltage

    client = voltage.Client()

    @client.listen("message")
    async def on_message(message):
        if message.content == "!ping":
            await message.reply("Pong!")

    dotenv.load_dotenv()
    client.run(os.getenv("TOKEN"))

Alright so to explain what's going on, first we import the dotenv library to be able to access our enviroment and voltage,

Next we initialize our bot client using the :class:`voltage.Client` class.

Then we registered a decorator using the :meth:`voltage.Client.listen` decorator, we passed in the ``message`` event to listen for when a message is sent.

We then defined an asynchronous function called ``on_message`` tho it doesn't really matter what you call it, what matters however is that it expects one parameter which is the message object.

After that we check if the message's content is equal to ``!ping``, if it is we reply with ``Pong!``.

Then we load the enviroment using the :func:`dotenv.load_dotenv` function and then run the client using the :meth:`voltage.Client.run` method.

Now if you run this code your bot should go online and if you were to type ``!ping`` it will reply to your message with ``Pong!``

Great, we have finally made our bot, now what?

Next up we will go into more detail about how to use the voltage library and it's various classes, functions and so on!
