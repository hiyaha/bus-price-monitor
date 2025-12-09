# ⚡ クイックスタート（3ステップ）

## 1️⃣ GitHubにアップロード

1. [GitHub](https://github.com/)で新規リポジトリ作成
2. このフォルダの全ファイルをアップロード
3. Publicを選択

## 2️⃣ Secretを設定

1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `DISCORD_WEBHOOK_URL`
4. Secret: `https://discord.com/api/webhooks/1448050592848281612/Y6rkHw3VEQLL-wxyF1J7UUBNU4_tT6C8xHLu55b85rsx6ECIIoT3hJDppxj82KEiHJHK`

## 3️⃣ テスト実行

1. Actions タブ
2. Run workflow → Run workflow
3. Discordで通知を確認！

---

✅ これで完了！1時間ごとに自動監視が開始されます。

詳細は **README.md** を参照してください。
