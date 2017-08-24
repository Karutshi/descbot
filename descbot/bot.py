import discord
import os
import time
import re
import signal, sys
from datetime import datetime, timedelta
from discord.enums import ChannelType
from stateevent import StateEvent
from databasehandler import DatabaseHandler
from channels import Channel

#dbHandler = DatabaseHandler()
#dbHandler.check_in(2, "World of Warcraft")
#time.sleep(3)
#dbHandler.check_out(2)
#exit(0)
#dbHandler.check_in(2, "World of Warcraft")

class Bot(discord.Client):

    def __init__(self):
        super().__init__()
        self.dbHandler = DatabaseHandler()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == self.user:
            return

        if message.channel.id == Channel.Descbot_room:
            mgrp = re.search(r"stats.*(\d+)", message.content, re.IGNORECASE)
            if "help" in message.content.lower():
                await self.send_help_message()
            elif "stats" in message.content.lower():
                amount = int(mgrp.group(1)) if mgrp is not None else 5
                print(amount)
                if message.mentions:
                    for user in message.mentions:
                        await self.send_user_stats(user, amount)
                else:
                    await self.send_stats(amount)
    
    async def send_help_message(self): 
        room = self.get_channel(Channel.Descbot_room)
        await self.smart_message(room, "This bot counts the time DESC members spend in voice channels.\n" + 
                                      "Current leaderboard can be seen by sending command `stats` in this channel, " + 
                                      "and if you want to see stats for a specific user you can add their @-tag to the command.")

    async def send_stats(self, amount):
        room = self.get_channel(Channel.Descbot_room)
        message = "Current leaderboard:\n\n"
        i = 0
        for userId, time in self.dbHandler.get_stats(amount):
            i += 1
            user = self.get_server(Channel.Desc).get_member(str(userId))
            userName = user.nick if user.nick is not None else user.name
            message += "%d: **%s**, %s\n" % (i, userName, str(timedelta(seconds = time.seconds)))
        await self.smart_message(room, message)
 
    async def send_user_stats(self, user, amount = None):
        userName = user.nick if user.nick is not None else user.name
        room = self.get_channel(Channel.Descbot_room)
        totalTime = self.dbHandler.get_user_total(int(user.id))
        message = 'Stats for user **%s**:\n\n' % userName
        message += 'Total time in `all channels`: %s\n\n' % str(timedelta(seconds = totalTime.seconds))
        for channel, time in self.dbHandler.get_user_stats(int(user.id), amount):
            message += 'Time in channel `%s`: %s' % (channel, str(timedelta(seconds = time.seconds)))
        await self.smart_message(room, message)

    async def on_voice_state_update(self, before, after):
        beforeState = StateEvent.getState(before)
        afterState = StateEvent.getState(after)
        userName = after.name if after.nick is None else after.nick
        if afterState == StateEvent.Online or afterState == StateEvent.Mute:
            if beforeState == StateEvent.Offline or beforeState == StateEvent.Afk:
                self.dbHandler.check_in(int(after.id), after.voice_channel.name)
                print("%s checked in to %s." % (userName, after.voice_channel.name))
            elif beforeState == StateEvent.Deafen:
                self.dbHandler.check_in(int(after.id), after.voice_channel.name)
                print("%s undeafened themselves in %s." % (userName, after.voice_channel.name))
            else:
                self.dbHandler.check_out(int(after.id))
                self.dbHandler.check_in(int(after.id), after.voice_channel.name)
                if beforeState == StateEvent.Mute:
                    print("%s unmuted themselves in %s." % (after.ick, after.voice_channel.name))
                else:
                    print("%s switched channels from %s to %s." % (userName, before.voice_channel.name, after.voice_channel.name))
        else:
            if beforeState == StateEvent.Online or beforeState == StateEvent.Mute:
                self.dbHandler.check_out(int(before.id))
                if afterState == StateEvent.Deafen:
                    print("%s deafened themselves in %s." % (userName, before.voice_channel.name))
                else:
                    print("%s checked out from %s." % (userName, before.voice_channel.name))
                

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        self.check_everyone_in()
        print('Everyone has been checked in.')
        print('------')

    def check_everyone_in(self):
        for user, channel in self.get_all_online_users():
            self.dbHandler.check_in(int(user.id), channel.name)

    def check_everyone_out(self, time = None):
        time = datetime.now() if time is None else time
        self.dbHandler.check_everyone_out(time)
        print("Everyone has been checked out.")

    def get_all_online_users(self):
        users = []
        desc = self.get_server(Channel.Desc)
        for channel in filter(lambda ch: ch.type == ChannelType.voice, desc.channels):
            if channel.id != Channel.Afk:
                for user in channel.voice_members:
                    if not user.self_deaf:
                        users.append((user, channel))
        return users
    
    async def smart_message(self, channel, message):
        messages = []
        current_message = ""
        for row in message.split("\n"):
            print("loop1")
            row += "\n"
            if (len(row) >= 2000) and current_message:
                messages.append(current_message)
                current_message = ""
            while(len(row) >= 2000):
                print("loop2")
                messages.append(row[:2000])
                row = row[2000:]
            if len(current_message) + len(row) >= 2000:
                messages.append(current_message)
                current_message = ""
            current_message += row
        messages.append(current_message)
        for message in messages:
            await self.send_message(channel, message)

bot = Bot()
def signal_handler(signal, frame):
    bot.check_everyone_out()
    bot.logout()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
bot.run(os.environ.get('DESCBOT_TOKEN'))

