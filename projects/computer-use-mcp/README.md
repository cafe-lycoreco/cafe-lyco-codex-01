# Computer-use MCP プロジェクト

このMac用のローカルMCPプラグイン。新規の起動・検証・パッケージコードと、インストール済みComputer Useエンジンを組み合わせます。

- [プラグイン本体・使い方](plugin/computer-use-mcp/README.md)
- [MCP定義](plugin/computer-use-mcp/mcp.json)
- [起動スクリプト](plugin/computer-use-mcp/scripts/launch.sh)
- [接続検証](plugin/computer-use-mcp/scripts/smoke_test.py)
- [ZIP生成](scripts/package.py)

リポジトリのルートから次を実行します。

```sh
python3 projects/computer-use-mcp/scripts/package.py
python3 projects/computer-use-mcp/plugin/computer-use-mcp/scripts/smoke_test.py --list-apps
```

ZIPとSHA-256は `outputs/` に生成します。ZIPに入るのは `plugin/computer-use-mcp/` 内のプラグインだけです。個人設定、画面画像、アプリ使用履歴、エンジンのバイナリは保存しません。アカウント上のプラグインIDやこのMacでの検証記録は、非公開の `.local/` に記録します。
