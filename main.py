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

speakerID = [{"name":"四国めたん","speaker_uuid":"7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff","styles":[{"id":2,"name":"ノーマル"},{"id":0,"name":"あまあま"},{"id":6,"name":"ツンツン"},{"id":4,"name":"セクシー"},{"id":36,"name":"ささやき"},{"id":37,"name":"ヒソヒソ"}],"version":"0.13.3"},{"name":"ずんだもん","speaker_uuid":"388f246b-8c41-4ac1-8e2d-5d79f3ff56d9","styles":[{"id":3,"name":"ノーマル"},{"id":1,"name":"あまあま"},{"id":7,"name":"ツンツン"},{"id":5,"name":"セクシー"},{"id":22,"name":"ささやき"},{"id":38,"name":"ヒソヒソ"}],"version":"0.13.3"},{"name":"春日部つむぎ","speaker_uuid":"35b2c544-660e-401e-b503-0e14c635303a","styles":[{"id":8,"name":"ノーマル"}],"version":"0.13.3"},{"name":"雨晴はう","speaker_uuid":"3474ee95-c274-47f9-aa1a-8322163d96f1","styles":[{"id":10,"name":"ノーマル"}],"version":"0.13.3"},{"name":"波音リツ","speaker_uuid":"b1a81618-b27b-40d2-b0ea-27a9ad408c4b","styles":[{"id":9,"name":"ノーマル"}],"version":"0.13.3"},{"name":"玄野武宏","speaker_uuid":"c30dc15a-0992-4f8d-8bb8-ad3b314e6a6f","styles":[{"id":11,"name":"ノーマル"},{"id":39,"name":"喜び"},{"id":40,"name":"ツンギレ"},{"id":41,"name":"悲しみ"}],"version":"0.13.3"},{"name":"白上虎太郎","speaker_uuid":"e5020595-5c5d-4e87-b849-270a518d0dcf","styles":[{"id":12,"name":"ふつう"},{"id":32,"name":"わーい"},{"id":33,"name":"びくびく"},{"id":34,"name":"おこ"},{"id":35,"name":"びえーん"}],"version":"0.13.3"},{"name":"青山龍星","speaker_uuid":"4f51116a-d9ee-4516-925d-21f183e2afad","styles":[{"id":13,"name":"ノーマル"}],"version":"0.13.3"},{"name":"冥鳴ひまり","speaker_uuid":"8eaad775-3119-417e-8cf4-2a10bfd592c8","styles":[{"id":14,"name":"ノーマル"}],"version":"0.13.3"},{"name":"九州そら","speaker_uuid":"481fb609-6446-4870-9f46-90c4dd623403","styles":[{"id":16,"name":"ノーマル"},{"id":15,"name":"あまあま"},{"id":18,"name":"ツンツン"},{"id":17,"name":"セクシー"},{"id":19,"name":"ささやき"}],"version":"0.13.3"},{"name":"もち子さん","speaker_uuid":"9f3ee141-26ad-437e-97bd-d22298d02ad2","styles":[{"id":20,"name":"ノーマル"}],"version":"0.13.3"},{"name":"剣崎雌雄","speaker_uuid":"1a17ca16-7ee5-4ea5-b191-2f02ace24d21","styles":[{"id":21,"name":"ノーマル"}],"version":"0.13.3"},{"name":"WhiteCUL","speaker_uuid":"67d5d8da-acd7-4207-bb10-b5542d3a663b","styles":[{"id":23,"name":"ノーマル"},{"id":24,"name":"たのしい"},{"id":25,"name":"かなしい"},{"id":26,"name":"びえーん"}],"version":"0.13.3"},{"name":"後鬼","speaker_uuid":"0f56c2f2-644c-49c9-8989-94e11f7129d0","styles":[{"id":27,"name":"人間ver."},{"id":28,"name":"ぬいぐるみver."}],"version":"0.13.3"},{"name":"No.7","speaker_uuid":"044830d2-f23b-44d6-ac0d-b5d733caa900","styles":[{"id":29,"name":"ノーマル"},{"id":30,"name":"アナウンス"},{"id":31,"name":"読み聞かせ"}],"version":"0.13.3"},{"name":"ちび式じい","speaker_uuid":"468b8e94-9da4-4f7a-8715-a22a48844f9e","styles":[{"id":42,"name":"ノーマル"}],"version":"0.13.3"},{"name":"櫻歌ミコ","speaker_uuid":"0693554c-338e-4790-8982-b9c6d476dc69","styles":[{"id":43,"name":"ノーマル"},{"id":44,"name":"第二形態"},{"id":45,"name":"ロリ"}],"version":"0.13.3"},{"name":"小夜/SAYO","speaker_uuid":"a8cc6d22-aad0-4ab8-bf1e-2f843924164a","styles":[{"id":46,"name":"ノーマル"}],"version":"0.13.3"},{"name":"ナースロボ＿タイプＴ","speaker_uuid":"882a636f-3bac-431a-966d-c5e6bba9f949","styles":[{"id":47,"name":"ノーマル"},{"id":48,"name":"楽々"},{"id":49,"name":"恐怖"},{"id":50,"name":"内緒話"}],"version":"0.13.3"}]

core.initialize(False, 4)
core.voicevox_load_openjtalk_dict("voicevox_core/open_jtalk_dic_utf_8-1.11")

"""
for id in speakerID.keys():
    core.load_model(id)
"""

def speakerIDList():
    tmp = ""
    for speaker in speakerID:
        tmp += speaker["name"] + "\n"
        for style in speaker["styles"]:
            id = style["id"]
            if id>38:
                continue
            name = str(style["name"])
            tmp += f"{str(id):>5}:   {name}\n"
        tmp += "\n"
    return tmp

def speakerIDtoName(id: int):
    if id>38: return None
    for speaker in speakerID:
        for style in speaker["styles"]:
            if style["id"] == id:
                return speaker["name"]+"("+style["name"]+")"
    return None

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

