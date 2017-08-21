import discord
import os
from datetime import datetime
from discord.enums import ChannelType
from stateevent import StateEvent
from channels import Channel
client = discord.Client()

def good_channel(member):
    return member.server.id == Channel.Gamma_bois and member.voice_channel is not None and member.voice_channel.id != Channel.Afk

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
    """if not good_channel(before) and good_channel(after):
        await client.send_message(bot_channel, "%s joined channel **%s**." % (str(after.display_name), str(after.voice_channel)))
    elif good_channel(before) and not good_channel(after):
        await client.send_message(bot_channel, "%s left channel **%s**." % (str(after.display_name), str(before.voice_channel)))
    elif good_channel(before) and good_channel(after):
        await client.send_message(bot_channel, "%s switched from channel **%s** to **%s**." % (str(after.display_name), str(before.voice_channel), str(after.voice_channel)))"""
    print(datetime.now())
    print(StateEvent.getState(before))
    print(StateEvent.getState(after))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(os.environ.get('DESCBOT_TOKEN'))
