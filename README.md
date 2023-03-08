# discord-vox
喋れないけど喋りたい

VOICEVOX COREを使って合成した音声をDiscordのVCに流します。

このプログラムはVOICEVOX CORE 0.14.1で動作します。
https://github.com/Hiroshiba/voicevox_core

### コマンド一覧
- `/texvoice [optional int]` 使用する話者IDをDiscordユーザーごとに設定します。IDを省くと、現在設定されている話者を教えてくれます。
- `/speakerlist` 使用できる話者IDの一覧を表示します。
- `/join` `/left` 使用者がいるVCにBotを接続、切断させます。

### 設定
botSetting.json にBotのトークン、使用するサーバーのID、読み上げるテキストチャンネルのID、Open JTalkのパスを入れます。

デフォルトではOpen JTalkはmain.pyと同じディレクトリにあるとしています。

onnxruntimeのDLLが正しく読まれるようにしてください。

## VOICEVOX許諾内容
1. 作成された音声を利用する際は、各音声ライブラリの規約に従ってください。
2. 作成された音声の利用を他者に許諾する際は、当該他者に対し本許諾内容の 1. 及び 2. の遵守を義務付けてください。
