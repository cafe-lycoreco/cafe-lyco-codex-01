# Computer-use MCP

このMacにインストール済みのComputer Useエンジンを、ローカルのSTDIO MCPとして起動するプラグインです。新規作成部分は起動スクリプト、プラグイン定義、操作手順、接続検証です。画面取得や入力を実行するエンジンは、既存の `SkyComputerUseClient mcp` を使用します。公式エンジンのバイナリや個人設定は同梱しません。OpenAI公式プラグインではありません。

## 必要な環境

- macOSと、デスクトップアプリでインストール・有効化済みのComputer Use。
- 通常のエンジン配置先は `$HOME/.codex/computer-use/`。ホストが `CODEX_HOME` を設定している場合は、その配下の `computer-use/` を使います。
- 対象アプリへのアクセス許可。画面収録・アクセシビリティの許可は公式Computer Useの案内に従います。
- 接続検証スクリプトにはPython 3。MCP自体の起動にはPython、Node、APIキーは不要です。

## 提供ツール

| ツール | 機能 |
| --- | --- |
| `list_apps` | アプリ一覧と使用情報の取得 |
| `get_app_state` | 対象アプリの画面とアクセシビリティ情報の取得 |
| `click` | 要素または座標のクリック |
| `perform_secondary_action` | 要素の補助アクション |
| `set_value` | アクセシビリティ要素の値設定 |
| `select_text` | 文字選択・カーソル配置 |
| `scroll` | スクロール |
| `drag` | ドラッグ |
| `press_key` | キー・ショートカット入力 |
| `type_text` | 文字入力 |

これは作成時のエンジンから検出した一覧です。更新後は実際の `tools/list` を優先してください。

## 接続確認

プラグインのフォルダーで次を実行します。

```sh
/bin/sh scripts/launch.sh --check
python3 scripts/smoke_test.py
python3 scripts/smoke_test.py --list-apps
```

`--check` は実行ファイルの存在確認だけです。スモークテストはMCPの初期化、ツール取得、pingを確認します。`--list-apps` は読取専用ツールを呼び、アプリ一覧本文を出力・保存せずに成功状態だけを表示します。個別アプリの権限やクリック・入力の成功は別途検証が必要です。

ターミナルからの単独起動では、初期化とツール取得が成功しても `Computer Use server error -10000: Sender process is not authenticated` が返る場合があります。これは実行元の認証エラーです。デスクトップホスト内でインストール・有効化したプラグインから接続を検証してください。認証を模倣したり、認証用データをコピーして回避しないでください。ホスト内での動作は、ターミナルでの初期化成功だけでは証明できません。

## プラグインとして使う

`plugin.json` と `mcp.json` はAgent Plugins 1.0形式です。旧Codex向けに `.codex-plugin/plugin.json` と `.mcp.json` も含めています。ホストのプラグイン導入手順でこのパッケージをインストールし、ローカルMCPサーバーを有効にしてください。アカウントへの非公開保存と、このMacへのインストール・有効化は別の状態です。

## MCPだけを登録する

デスクトップアプリの Settings → MCP servers → Add server に次を指定できます。既存の登録は削除・上書きせず、必要な場合だけ追加してください。

- 名前: `computer-use-mcp`
- 通信: STDIO
- Command: `/bin/sh`
- Args: このプラグイン内の `scripts/launch.sh` の絶対パス（1つの引数として渡す）
- 環境変数: 通常は追加不要

パスに空白があっても、Argsを1つの文字列として渡します。手動登録の場合は、このフォルダーを移動すると登録した絶対パスの更新が必要です。プラグイン経由の場合は `${PLUGIN_ROOT}` をホストが解決します。

## 操作範囲

起動スクリプトは既存エンジンへSTDIOをそのまま引き渡し、権限・安全ポリシーを変更しません。操作する前に、そのターンで `get_app_state` を呼びます。拒否された対象を別経路で操作し直す用途には使いません。プラグイン作成やMCP接続の成功は、特定アプリへの操作許可を意味しません。

このパッケージはローカル実行用で、HTTPエンドポイントを公開しません。アカウントへ保存しても、Webや別のPCで単独動作するクラウドサーバーにはなりません。

## 参照

- [OpenAI公式のComputer Use案内](https://learn.chatgpt.com/docs/computer-use)
- [OpenAI公式のMCP接続案内](https://learn.chatgpt.com/docs/extend/mcp)
- [MCP STDIO仕様](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
