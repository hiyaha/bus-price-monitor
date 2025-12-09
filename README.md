# 🚌 バス価格監視システム - GitHub Actionsセットアップガイド

東京→秋田（2025年12月15日）のバス価格を1時間ごとに自動監視し、Discordに通知します。

---

## 📋 必要なもの

- GitHubアカウント（無料）
- Discordアカウント（無料）
- 5分程度の時間

---

## 🚀 セットアップ手順（5分）

### ステップ1: GitHubリポジトリを作成

1. [GitHub](https://github.com/)にログイン
2. 右上の「+」→「New repository」をクリック
3. 以下を入力:
   - Repository name: `bus-price-monitor`（任意の名前でOK）
   - Description: `東京→秋田 バス価格監視`（任意）
   - Public を選択（無料で使えます）
4. 「Create repository」をクリック

### ステップ2: ファイルをアップロード

以下の3つの方法から選んでください。

#### 方法A: Webインターフェース（推奨・簡単）

1. 「uploading an existing file」をクリック
2. このフォルダ内のすべてのファイルを選択してドラッグ&ドロップ:
   - `bus_price_monitor.py`
   - `requirements.txt`
   - `.github/workflows/monitor.yml`
3. 「Commit changes」をクリック

⚠️ **重要**: `.github`フォルダは隠しフォルダです。必ず含めてください！

#### 方法B: GitHub Desktop（視覚的）

1. [GitHub Desktop](https://desktop.github.com/)をインストール
2. File → Clone repository → 作成したリポジトリを選択
3. このフォルダの中身をすべてコピー
4. GitHub Desktopで「Commit to main」→「Push origin」

#### 方法C: Git コマンド（経験者向け）

```bash
# このフォルダに移動
cd path/to/github-setup

# Git初期化
git init
git add .
git commit -m "Initial commit"

# リモートリポジトリと連携
git remote add origin https://github.com/YOUR_USERNAME/bus-price-monitor.git
git branch -M main
git push -u origin main
```

### ステップ3: Discord Webhook Secretを設定

1. リポジトリページで「Settings」タブをクリック
2. 左メニューから「Secrets and variables」→「Actions」をクリック
3. 「New repository secret」をクリック
4. 以下を入力:
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: `https://discord.com/api/webhooks/1448050592848281612/Y6rkHw3VEQLL-wxyF1J7UUBNU4_tT6C8xHLu55b85rsx6ECIIoT3hJDppxj82KEiHJHK`
5. 「Add secret」をクリック

✅ これでWebhook URLが安全に保存されました！

### ステップ4: GitHub Actionsを確認

1. リポジトリの「Actions」タブをクリック
2. 「I understand my workflows, go ahead and enable them」をクリック（必要な場合）
3. 「バス価格監視」ワークフローが表示されているか確認

### ステップ5: 初回テスト実行

1. 「Actions」タブ→「バス価格監視」をクリック
2. 右側の「Run workflow」→「Run workflow」をクリック
3. 数十秒〜1分程度待つ
4. ワークフローが緑色のチェックマーク✅になることを確認
5. **Discordを確認** - 通知が届いていれば成功！🎉

---

## 🎯 動作確認

### 成功時の表示

GitHub Actionsのログに以下のように表示されます:

```
============================================================
チェック時刻: 2025-12-09 20:00:00
URL: https://www.489.fm/searchbus/tokyo_akita/_/day20251215/
============================================================
✅ 価格取得成功
   最安値: 6,300円
   最高値: 8,000円
Discord通知送信成功
```

### Discordの通知

以下のような通知が届きます:

```
🚌 バス価格通知

🚌 監視開始

現在の最安値: 6,300円
全価格: 6,300円, 7,000円, 7,300円, 8,000円

🔗 予約ページへ
```

---

## ⚙️ カスタマイズ

### 監視する日付を変更

`bus_price_monitor.py`の83行目を編集:

```python
# 変更前
URL = "https://www.489.fm/searchbus/tokyo_akita/_/day20251215/"

# 変更後（例: 12月20日）
URL = "https://www.489.fm/searchbus/tokyo_akita/_/day20251220/"
```

### チェック間隔を変更

`.github/workflows/monitor.yml`の6行目を編集:

```yaml
# 現在: 1時間ごと
- cron: '0 * * * *'

# 30分ごと
- cron: '*/30 * * * *'

# 2時間ごと
- cron: '0 */2 * * *'

# 毎日朝9時と夜6時（日本時間）
- cron: '0 0,9 * * *'  # UTC = 日本時間-9時間
```

⚠️ **重要**: cronはUTC（協定世界時）で設定します。
- 日本時間の9時 = UTC 0時 → `0 0 * * *`
- 日本時間の18時 = UTC 9時 → `0 9 * * *`

---

## 🔔 通知の種類

### 💰 値下がり検出（緑色）

```
💰 値下がり検出！

前回: 7,000円 → 現在: 6,300円
700円 安くなりました！

🔗 予約ページへ
```

### 📈 値上がり検出（オレンジ色）

```
📈 値上がり検出

前回: 6,300円 → 現在: 7,000円
700円 高くなりました

🔗 予約ページへ
```

### 🚌 初回監視開始（青色）

```
🚌 監視開始

現在の最安値: 6,300円
全価格: 6,300円, 7,000円, 7,300円, 8,000円

🔗 予約ページへ
```

---

## 🐛 トラブルシューティング

### Q1: Discordに通知が来ない

**確認事項:**

1. ✅ Secretが正しく設定されているか
   - Settings → Secrets and variables → Actions
   - `DISCORD_WEBHOOK_URL`が存在するか確認
   
2. ✅ GitHub Actionsが実行されているか
   - Actions タブでワークフローの実行履歴を確認
   - エラーがあればログを確認

3. ✅ Webhook URLが有効か
   - Discordでウェブフックが削除されていないか確認

**解決方法:**
- Secretを削除して再設定してみる
- 「Run workflow」で手動実行してログを確認

### Q2: GitHub Actionsが実行されない

**原因:**
- Actionsが無効化されている
- ワークフローファイルの構文エラー
- リポジトリがPrivate（無料枠の制限）

**解決方法:**
1. Actions タブで「Enable workflow」をクリック
2. ワークフローファイルの構文を確認（YAMLのインデントなど）
3. リポジトリをPublicにする

### Q3: 価格が取得できない

**原因:**
- まだバスが販売開始されていない
- サイトの構造が変更された
- ネットワークエラー

**解決方法:**
1. ブラウザで実際にURLにアクセスして価格が表示されるか確認
2. GitHub Actionsのログで詳細なエラーメッセージを確認
3. 別の日付で試してみる

### Q4: "該当するバスは見つかりませんでした"

**原因:**
- 指定した日付のバスがまだ販売開始されていない
- すでに満席
- 運行予定がない

**解決方法:**
- 公式サイトで販売状況を確認
- 別の日付に変更してテスト
- 販売開始を待つ（システムは動作し続けます）

---

## 📊 実行履歴の確認

### GitHub Actionsで確認

1. 「Actions」タブを開く
2. 左側の「バス価格監視」をクリック
3. 実行履歴が時系列で表示されます
   - ✅ 緑: 成功
   - ❌ 赤: 失敗
4. 各実行をクリックすると詳細ログが見られます

### 保存される価格履歴

`prices.json`ファイルに最新の価格情報が保存されます:

```json
{
  "status": "success",
  "prices": [6300, 7000, 7300, 8000],
  "min_price": 6300,
  "max_price": 8000,
  "timestamp": "2025-12-09T20:00:00"
}
```

---

## 💡 便利な使い方

### スマホで通知を受け取る

1. スマホにDiscordアプリをインストール
2. 通知設定でチャンネルの通知をONにする
3. バス価格が変動したらスマホに即座に通知！

### 複数の日付を監視

複数の日付を監視したい場合:

1. リポジトリを複製して別の日付用にする
2. または`bus_price_monitor.py`を修正して複数URLを処理

### 他の路線にも応用

`URL`を変更すれば、他の路線も監視できます:

```python
# 東京→大阪
URL = "https://www.489.fm/searchbus/tokyo_osaka/_/day20251215/"

# 東京→名古屋
URL = "https://www.489.fm/searchbus/tokyo_nagoya/_/day20251215/"
```

---

## 🎉 完了！

これで、1時間ごとにバス価格が自動的にチェックされ、
価格が変動したらDiscordに通知が届くようになりました！

**次にやること:**
- [ ] Discordで通知を確認
- [ ] 必要に応じて監視間隔をカスタマイズ
- [ ] 友達に共有して一緒に使う

---

## 📧 サポート

問題が発生した場合:
1. このREADMEのトラブルシューティングを確認
2. GitHub Actionsのログを確認
3. GitHubのIssuesで質問

---

**楽しいバス旅行を！🚌✨**

最終更新: 2025-12-09
