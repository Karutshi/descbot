from channels import Channel
from enum import Enum

class StateEvent(Enum):
    Online  = 1
    Offline = 2
    Mute    = 3
    Deafen  = 4
    Afk     = 5

    @classmethod
    def getState(cls, member):
        if member.server is None or member.voice_channel is None or member.server.id != Channel.Gamma_bois:
            return cls.Offline
        elif member.voice_channel.id == Channel.Afk:
            return cls.Afk
        elif member.self_deaf:
            return cls.Deafen
        elif member.self_mute:
            return cls.Mute
        else:
            return cls.Online
