#!/usr/bin/env python3
"""
バス価格監視システム（グラフ付き）
指定されたURLのバス価格を監視し、変動があればDiscordに通知
価格履歴を保存し、グラフを生成して表示
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import time

class BusPriceMonitor:
    def __init__(self, url, webhook_url, price_file='prices.json', history_file='price_history.json'):
        self.url = url
        self.webhook_url = webhook_url
        self.price_file = price_file
        self.history_file = history_file
        
    def scrape_prices(self):
        """バスサイトから価格情報をスクレイピング"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        }
        
        try:
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = []
            
            # 価格情報を抽出
            for text in soup.stripped_strings:
                if '円' in text:
                    matches = re.findall(r'([\d,]+)\s*円', text)
                    for match in matches:
                        try:
                            price = int(match.replace(',', ''))
                            if 1000 <= price <= 50000:
                                prices.append(price)
                        except ValueError:
                            pass
            
            price_elements = soup.find_all(class_=re.compile(r'price|fare|amount', re.I))
            for elem in price_elements:
                text = elem.get_text()
                matches = re.findall(r'([\d,]+)', text)
                for match in matches:
                    try:
                        price = int(match.replace(',', ''))
                        if 1000 <= price <= 50000:
                            prices.append(price)
                    except ValueError:
                        pass
            
            prices = sorted(list(set(prices)))
            
            page_text = soup.get_text()
            if '該当するバスは見つかりませんでした' in page_text:
                return {'status': 'no_bus', 'prices': [], 'message': 'バスが見つかりませんでした'}
            
            if prices:
                return {
                    'status': 'success',
                    'prices': prices,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'status': 'no_price', 'prices': [], 'message': '価格情報が見つかりませんでした'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def load_previous_prices(self):
        """前回の価格情報を読み込み"""
        if os.path.exists(self.price_file):
            try:
                with open(self.price_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def save_prices(self, data):
        """価格情報を保存"""
        with open(self.price_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_price_history(self):
        """価格履歴を読み込み（最大100件）"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_price_history(self, history):
        """価格履歴を保存（最大100件）"""
        # 最新100件のみ保持
        if len(history) > 100:
            history = history[-100:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def add_to_history(self, price, timestamp):
        """履歴に価格を追加"""
        history = self.load_price_history()
        history.append({
            'price': price,
            'timestamp': timestamp
        })
        self.save_price_history(history)
        return history
    
    def create_ascii_graph(self, history, width=40, height=10):
        """ASCIIアートでグラフを生成"""
        if len(history) < 2:
            return "まだデータが不足しています（最低2件必要）"
        
        prices = [h['price'] for h in history]
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return f"価格は一定です: {min_price:,}円"
        
        # グラフを生成
        graph_lines = []
        price_range = max_price - min_price
        
        # Y軸のラベル
        for i in range(height, -1, -1):
            price_at_line = min_price + (price_range * i / height)
            line = f"{int(price_at_line):>6,}円 "
            
            # データポイントをプロット
            for j, price in enumerate(prices[-width:]):
                normalized = (price - min_price) / price_range * height
                if abs(normalized - i) < 0.5:
                    line += "●"
                elif i == 0:
                    line += "─"
                else:
                    line += " "
            
            graph_lines.append(line)
        
        # X軸
        x_axis = "        " + "─" * min(len(prices), width)
        graph_lines.append(x_axis)
        
        # 時間ラベル
        if len(history) >= 2:
            first_time = datetime.fromisoformat(history[-min(len(history), width)]['timestamp']).strftime('%m/%d %H:%M')
            last_time = datetime.fromisoformat(history[-1]['timestamp']).strftime('%m/%d %H:%M')
            time_label = f"        {first_time}" + " " * (width - 20) + f"{last_time}"
            graph_lines.append(time_label)
        
        return '\n'.join(graph_lines)
    
    def create_sparkline(self, history):
        """シンプルなスパークライングラフを生成"""
        if len(history) < 2:
            return "─"
        
        # Unicode block characters for sparkline
        blocks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        prices = [h['price'] for h in history[-50:]]  # 最新50件
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return '▄' * len(prices)
        
        sparkline = ''
        for price in prices:
            normalized = (price - min_price) / (max_price - min_price)
            block_index = min(int(normalized * len(blocks)), len(blocks) - 1)
            sparkline += blocks[block_index]
        
        return sparkline
    
    def send_discord_notification(self, current_data, previous_data=None, history=None):
        """Discordに通知を送信（グラフ付き）"""
        if not self.webhook_url or self.webhook_url == 'YOUR_DISCORD_WEBHOOK_URL':
            print(f"[DEMO] Discord通知")
            return
        
        min_price = current_data['min_price']
        
        # 価格推移グラフを生成
        graph = ""
        sparkline = ""
        stats = ""
        
        if history and len(history) >= 2:
            # スパークライングラフ
            sparkline = self.create_sparkline(history)
            
            # 統計情報
            recent_prices = [h['price'] for h in history[-24:]]  # 直近24時間
            if recent_prices:
                avg_price = sum(recent_prices) / len(recent_prices)
                stats = f"\n直近24h平均: {int(avg_price):,}円"
        
        # 通知の種類を判定
        if previous_data and previous_data.get('status') == 'success':
            prev_min = previous_data.get('min_price')
            
            if min_price < prev_min:
                # 値下がり
                color = 0x00ff00  # 緑色
                diff = prev_min - min_price
                title = "💰 値下がり検出！"
                description = f"**{diff:,}円 安くなりました！**\n"
            elif min_price > prev_min:
                # 値上がり
                color = 0xffa500  # オレンジ色
                diff = min_price - prev_min
                title = "📈 値上がり検出"
                description = f"{diff:,}円 高くなりました\n"
            else:
                # 変動なし
                color = 0x808080  # グレー
                title = "📊 価格確認"
                description = ""
        else:
            # 初回
            color = 0x0000ff  # 青色
            title = "🚌 監視開始"
            description = ""
        
        # Discord埋め込みメッセージを作成
        embed = {
            "title": title,
            "color": color,
            "fields": [
                {
                    "name": "現在の価格(非会員)",
                    "value": f"**{min_price:,}円**",
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"さくら高速バス 価格監視 | データ数: {len(history) if history else 0}件"
            }
        }
        
        # 価格推移グラフを追加
        if sparkline:
            embed["fields"].append({
                "name": "価格推移（最新50件）",
                "value": f"```{sparkline}```{stats}",
                "inline": False
            })
        
        # 説明文を追加
        if description:
            embed["description"] = description
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("Discord通知送信成功")
        except Exception as e:
            print(f"Discord通知送信失敗: {e}")
    
    def check_and_notify(self):
        """価格をチェックして変動があれば通知"""
        print(f"\n{'='*60}")
        print(f"チェック時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {self.url}")
        print(f"{'='*60}")
        
        # 現在の価格を取得
        current_data = self.scrape_prices()
        
        if current_data['status'] == 'success':
            min_price = current_data['min_price']
            max_price = current_data['max_price']
            all_prices = current_data['prices']
            timestamp = current_data['timestamp']
            
            print(f"✅ 価格取得成功")
            print(f"   最安値: {min_price:,}円")
            print(f"   最高値: {max_price:,}円")
            print(f"   全価格: {', '.join([f'{p:,}円' for p in all_prices])}")
            
            # 履歴に追加
            history = self.add_to_history(min_price, timestamp)
            print(f"   履歴件数: {len(history)}件")
            
            # 前回の価格を読み込み
            previous_data = self.load_previous_prices()
            
            # 通知を送信
            self.send_discord_notification(current_data, previous_data, history)
            
            # 現在の価格を保存
            self.save_prices(current_data)
            
        elif current_data['status'] == 'no_bus':
            print("⚠️  バスが見つかりませんでした（まだ販売開始されていない可能性）")
            
            previous_data = self.load_previous_prices()
            if previous_data and previous_data.get('status') == 'success':
                # バスが見つからなくなった場合のみ通知
                embed = {
                    "title": "⚠️ バスが見つかりませんでした",
                    "description": "満席になったか、販売が終了した可能性があります",
                    "color": 0xff0000,
                    "timestamp": datetime.utcnow().isoformat()
                }
                payload = {"embeds": [embed]}
                try:
                    requests.post(self.webhook_url, json=payload)
                except:
                    pass
            
            self.save_prices(current_data)
            
        else:
            print(f"❌ エラー: {current_data.get('message', '不明なエラー')}")
        
        print(f"{'='*60}\n")


def main():
    # 設定
    URL = "https://www.489.fm/searchbus/tokyo_akita/_/day20251215/"
    WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
    
    monitor = BusPriceMonitor(URL, WEBHOOK_URL)
    monitor.check_and_notify()


if __name__ == "__main__":
    main()
