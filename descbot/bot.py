import discord
import os
import time
from datetime import datetime
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

        if message.channel.name == "bot_training_ground":
            print(dir(message))
            #await self.send_message(message.channel, 'Sorry. Didn\'t it! ({}).'.format(answer))

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
        

    def get_all_online_users(self):
        users = []
        desc = self.get_server(Channel.Desc)
        for channel in filter(lambda ch: ch.type == ChannelType.voice, desc.channels):
            if channel.id != Channel.Afk:
                for user in channel.voice_members:
                    if not user.self_deaf:
                        users.append((user, channel))
        return users

bot = Bot()
bot.run(os.environ.get('DESCBOT_TOKEN'))
