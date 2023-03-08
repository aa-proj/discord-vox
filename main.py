import subprocess
from discord.opus import Encoder
import shlex
import io
import json
import voicevox_core
from pathlib import Path
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
voiceClient: dict[str,discord.VoiceClient] = {}
voiceSource: dict[str,list] = {}

userSetting = {}
botSetting = {}

def speakerIDList():
    tmp = ""
    for speaker in voicevox_core.METAS:
        tmp += speaker.name + "\n"
        for style in speaker.styles:
            id = style.id
            name = style.name
            tmp += f"{str(id):>5}:   {name}\n"
        tmp += "\n"
    return tmp

def speakerIDtoName(id: int):
    for speaker in voicevox_core.METAS:
        for style in speaker.styles:
            if style.id == id:
                return speaker.name+"("+style.name+")"
    return None

with open("botSetting.json") as f:
    string = f.read()
    if string != "":
        botSetting = json.loads(string)
        for id in botSetting["guildIDs"]:
            guilds.append(discord.Object(id=id))

with open("userSetting.json") as f:
    string = f.read()
    print(string)
    if string != "":
        userSetting = json.loads(string)
    print(userSetting)

core = voicevox_core.VoicevoxCore(open_jtalk_dict_dir=Path(botSetting["jtalkPath"]))

@tree.command(
    guilds=guilds,
    name="texvoice",
    description="Voiceの選択" 
)
async def setSpeakerID(ctx: discord.Interaction, voiceid: str = None):
    userid = str(ctx.user.id)
    guildid = str(ctx.guild_id)
    if guildid not in userSetting:
        userSetting[guildid] = {}
        
    if guildid not in voiceSource:
        voiceSource[guildid] = []

    if voiceid is None:
        if userid not in userSetting[guildid]:
            await ctx.response.send_message("SpeakerIDが登録されていません。\n`/texvoice [数字]`で指定できます。\n`/speakerlist` でIDの一覧を表示できます。", ephemeral=True)
        else:
            await ctx.response.send_message("あなたのSpeakerIDは`"+str(userSetting[guildid][userid]["voiceid"])+":"+speakerIDtoName(int(userSetting[guildid][userid]["voiceid"]))+"`です。\n`/texvoice [数字]`で変更できます。\n`/speakerlist` でIDの一覧を表示できます。", ephemeral=True)

    else:
        if speakerIDtoName(int(voiceid)) is None:
            await ctx.response.send_message("! ! !`"+voiceid+"`はリストに含まれません。! ! !\n`/speakerlist` でIDの一覧を表示できます。",ephemeral=True)
            return
        await ctx.response.send_message("OK\n\n"+ctx.user.display_name+"さんの声は`"+voiceid+": "+speakerIDtoName(int(voiceid))+"`に指定されました。")
        if userid not in userSetting[guildid]:
            userSetting[guildid][userid] = {}
        userSetting[guildid][userid]["voiceid"] = voiceid
        userSetting[guildid][userid]["name"] = ctx.user.display_name
        with open("userSetting.json", "w") as f:
            print(json.dumps(userSetting))
            f.write(json.dumps(userSetting))

@tree.command(
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

@tree.command(
    guilds=guilds,
    name="speakerlist",
    description="話者IDの一覧を表示します。"
)
async def speakerList(ctx:discord.Interaction):
    await ctx.response.send_message("```\n"+speakerIDList()+"\n```",ephemeral=True)


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

    if message.channel.id not in botSetting["channelIDs"]:
        return

    if message.author.voice is None:
        return
    
    speakerid = int(userSetting[guildid][str(message.author.id)]["voiceid"])

    if not core.is_model_loaded(speaker_id=speakerid):
        core.load_model(speaker_id=speakerid)

    wav = core.tts(text=message.content,speaker_id=speakerid)
    hoge = FFmpegPCMAudio(wav,pipe = True,stderr= sys.stderr)
    voiceSource[guildid].append(hoge)
    if voiceClient[guildid].is_playing():
        return
    playPop(message,voiceClient[guildid])

client.run(botSetting["token"])