# discord-vox
喋れないけど喋りたい

VOICEVOX COREを使って合成した音声をDiscordのVCに流します。

このプログラムはVOICEVOX CORE 0.14.1で動作します。

### コマンド一覧
- `/texvoice [optional int]` 使用する話者IDをDiscordユーザーごとに設定します。IDを省くと、現在設定されている話者を教えてくれます。
- `/speakerlist` 使用できる話者IDの一覧を表示します。
- `/join` `/left` 使用者がいるVCにBotを接続、切断させます。

### 設定
botSetting.json にBotのトークン、使用するサーバーのID、読み上げるテキストチャンネルのID、Open JTalkのパスを入れます。

デフォルトではOpen JTalkはmain.pyと同じディレクトリにあるとしています。

onnxruntimeのDLLが正しく読まれるようにしてください。