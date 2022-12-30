import subprocess
from discord.opus import Encoder
import shlex
import io
import json
import core
import discord
from discord import app_commands
import sys

class FFmpegPCMAudio(discord.AudioSource):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc
    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret
    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
guilds = []
voiceClient = {}
voiceSource = {}

userSetting = {}
clientSetting = {}

speakerID = {"2": "四国めたん(ノーマル)", "0": "四国めたん(あまあま)",
             "3": "ずんだもん(ノーマル)", "1": "ずんだもん(あまあま)",
             "8": "春日部つむぎ", "10": "雨晴はう", "14": "冥鳴ひまり"}

core.initialize(False, 4)
core.voicevox_load_openjtalk_dict("voicevox_core/open_jtalk_dic_utf_8-1.11")
"""
for id in speakerID.keys():
    core.load_model(id)
"""

with open("clientSetting.json") as f:
    string = f.read()
    if string != "":
        clientSetting = json.loads(string)
        for id in clientSetting["guildIDs"]:
            guilds.append(discord.Object(id=id))

with open("userSetting.json") as f:
    string = f.read()
    print(string)
    if string != "":
        userSetting = json.loads(string)
    print(userSetting)
    #if "users" not in userSetting:
    #    userSetting["users"] = {}

@tree.command(
    #guild=targetGuild,
    guilds=guilds,
    name="texvoice",
    description="Voiceの選択" 
)
async def setVoiceID(ctx: discord.Interaction, voiceid: str = None):
    userid = str(ctx.user.id)
    guildid = str(ctx.guild_id)
    if guildid not in userSetting:
        userSetting[guildid] = {}
        
    if guildid not in voiceSource:
        voiceSource[guildid] = []

    if voiceid is None:
        if userid not in userSetting[guildid]:
            await ctx.response.send_message("VoiceIDが登録されていません。\n`/texvoice [数字]`で指定できます。\n```\n"+"\n".join([f"{obj[0]: >3}:  {obj[1]}" for obj in speakerID.items()])+"```", ephemeral=True)
        else:
            await ctx.response.send_message("あなたのVoiceIDは`"+str(userSetting[guildid][userid]["voiceid"])+":"+speakerID[userSetting[guildid][userid]["voiceid"]]+"`です。\n`/texvoice [数字]`で変更できます。\n```\n"+"\n".join([f"{obj[0]: >3}:  {obj[1]}" for obj in speakerID.items()])+"```", ephemeral=True)

    else:
        if voiceid not in speakerID:
            await ctx.response.send_message("! ! !`"+voiceid+"`はリストに含まれません。! ! !\n```\n"+"\n".join([f"{obj[0]: >3}:  {obj[1]}" for obj in speakerID.items()])+"```",ephemeral=True)
            return
        await ctx.response.send_message("OK\n\n"+ctx.user.name+"さんの声は`"+voiceid+": "+speakerID[voiceid]+"`に指定されました。")
        if userid not in userSetting[guildid]:
            userSetting[guildid][userid] = {}
        userSetting[guildid][userid]["voiceid"] = voiceid
        userSetting[guildid][userid]["name"] = ctx.user.display_name
        with open("userList.json", "w") as f:
            f.write(json.dumps(userSetting))

@tree.command(
    #guild=targetGuild,
    guilds=guilds,
    name="join",
    description="TextVoiceを通話に参加させます。"
)
async def join(ctx: discord.Interaction):
    if ctx.user.voice is None:
        await ctx.response.send_message("あなたはVoiceチャンネルに接続していません。",ephemeral=True)
        return
    voiceClient[str(ctx.guild_id)] = await ctx.user.voice.channel.connect()
    await ctx.response.send_message("接続しました。",ephemeral=True)

@tree.command(
    #guild=targetGuild,
    guilds=guilds,
    name="left",
    description="TextVoiceを通話から切断します。" 
)
async def left(ctx: discord.Interaction):
    if ctx.guild.voice_client is None:
        await ctx.response.send_message("私はVoiceチャンネルに接続していません。",ephemeral=True)
        return
    if ctx.user.voice is None:
        await ctx.response.send_message("あなたはVoiceチャンネルに接続していません。\nボイスチャンネルにいる人が切断できます。",ephemeral=True)
        return
    await ctx.guild.voice_client.disconnect()
    await ctx.response.send_message("切断しました。",ephemeral=True)


@client.event
async def on_ready():
    for guild in guilds:
        await tree.sync(guild=guild)
    print("on_ready")
    print(discord.__version__)
    for guildid in userSetting.keys():
        if guildid not in voiceSource:
            voiceSource[guildid] = []

def playPop(message: discord.message,channel: discord.VoiceClient):
    guildid = str(channel.guild.id)
    if len(voiceSource[guildid]) == 0:
        return
    source = voiceSource[guildid].pop(0)
    channel.play(source,after=lambda e:playPop(message,channel))
    return

@client.event
async def on_message(message: discord.Message):
    print(message.content)
    if message.author.bot:
        return

    if message.guild.voice_client is None:
        return
    
    guildid = str(message.guild.id)

    if str(message.author.id) not in userSetting[guildid]:
        return

    if message.channel.id not in clientSetting["channelIDs"]:
        return
    
    wav = core.voicevox_tts(message.content,int(userSetting[guildid][str(message.author.id)]["voiceid"]))
    #with open("t.wav", "wb") as f:
    #   f.write(wav)
    hoge = FFmpegPCMAudio(wav,pipe = True,stderr= sys.stderr)
    voiceSource[guildid].append(hoge)
    if voiceClient[guildid].is_playing():
        return
    playPop(message,voiceClient[guildid])



client.run(clientSetting["token"])

