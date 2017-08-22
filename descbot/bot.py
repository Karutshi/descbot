import discord
import os
import time
from datetime import datetime
from discord.enums import ChannelType
from stateevent import StateEvent
from databasehandler import DatabaseHandler
from channels import Channel
client = discord.Client()

dbHandler = DatabaseHandler()
dbHandler.check_in(2, "World of Warcraft")
time.sleep(3)
dbHandler.check_out(2)
#exit(0)
#dbHandler.check_in(2, "World of Warcraft")

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.channel.name == "bot_training_ground":
        print(dir(message))
        #if guess is None:
        #    fmt = 'Sorry, you took too long. It was {}.'
            #await client.send_message(message.channel, fmt.format(answer))
        #    return
        #if int(guess.content) == answer:
            #await client.send_message(message.channel, 'Did it!')
        #else:
            #await client.send_message(message.channel, 'Sorry. Didn\'t it! ({}).'.format(answer))

@client.event
async def on_voice_state_update(before, after):
    bot_channel = None
    for channel in client.get_all_channels():
        if channel.type == ChannelType.text and channel.id == Channel.Bot_training_gamma:
            bot_channel = channel;
            break;
    #beforeName = "None" if before.server is None or before.voice_channel is None else str(before.voice_channel)
    #afterName = "None" if after.server is None or after.voice_channel is None else str(after.voice_channel)
    #await client.send_message(bot_channel, "%s switched from channel **%s** to **%s**" % (str(after.name), str(beforeName), str(afterName)))
    print(datetime.now())
    print(str(before.name) + ", " + str(StateEvent.getState(before)))
    print(str(after.name) + ", " + str(StateEvent.getState(after)))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(os.environ.get('DESCBOT_TOKEN'))
