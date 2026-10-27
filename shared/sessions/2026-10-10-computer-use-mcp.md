# Computer-use MCP作成

- 日付: 2026-10-10
- プロジェクト: [Computer-use MCP](../../projects/computer-use-mcp/README.md)
- 状態: パッケージ作成完了。ホスト導入・個別アプリ操作は未検証。

## 目的

インストール済みComputer Useエンジンを利用するmacOSローカルMCPプラグインを作成する。

## 実施したこと

- [プラグイン本体](../../projects/computer-use-mcp/plugin/computer-use-mcp/README.md)にAgent Plugins 1.0定義、Codex互換定義、標準配色SVG、操作スキル、STDIO起動スクリプト、接続検証を追加。
- [パッケージ生成](../../projects/computer-use-mcp/scripts/package.py)と `outputs/computer-use-mcp-0.1.0.zip`、SHA-256ファイルを追加。
- 公開向け索引・決定を更新。個人アカウントや環境固有の詳細は `.local/` の記録を参照する。

## 検証

- シェル構文、配置先実行ファイルの存在を確認。
- MCP初期化、`tools/list` の10ツール取得、pingが成功。
- ZIPの全9ファイルの本文一致・重複なし・CRC確認。展開後のパッケージでもMCP初期化・ツール取得・pingが成功。
- これらは個別アプリ操作成功の証明ではない。ホスト認証と対象アプリの許可は別途確認する。

## 決定と理由

既存エンジンを起動する構成。バイナリの再配布、OS権限やポリシー変更を含めない。起動・検証コードには外部パッケージ依存なし。

## 未完了事項と次の手順

デスクトップホストでインストール・有効化し、許可された対象アプリで状態読取を確認する。既に拒否されたアプリへの別経路の試行は行わない。ターミナル単独の呼び出しで認証エラーになる場合の説明はプラグインREADMEを読む。

## GitHubへの反映

ローカル保存のみ。commit・pushなし。作業ブランチは `codex/mac-setup-2026-10-09`。共有先はリモートHEADで確認した `cafe`。開始時点で保存済み `origin/cafe` に対して0 behind / 1 ahead。
