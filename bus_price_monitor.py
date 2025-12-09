#!/usr/bin/env python3
"""
バス価格監視システム
指定されたURLのバス価格を監視し、変動があればDiscordに通知
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import time

class BusPriceMonitor:
    def __init__(self, url, webhook_url, price_file='prices.json'):
        self.url = url
        self.webhook_url = webhook_url
        self.price_file = price_file
        
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
    
    def send_discord_notification(self, current_data, previous_data=None):
        """Discordに通知を送信"""
        if not self.webhook_url:
            print(f"[DEMO] Discord通知")
            return
        
        min_price = current_data['min_price']
        
        # 通知の種類を判定
        if previous_data and previous_data.get('status') == 'success':
            prev_min = previous_data.get('min_price')
            
            if min_price < prev_min:
                # 値下がり
                color = 0x00ff00  # 緑色
                diff = prev_min - min_price
                title = "💰 値下がり検出！"
                description = f"**{diff:,}円 安くなりました！**"
            elif min_price > prev_min:
                # 値上がり
                color = 0xffa500  # オレンジ色
                diff = min_price - prev_min
                title = "📈 値上がり検出"
                description = f"{diff:,}円 高くなりました"
            else:
                # 変動なし
                color = 0x808080  # グレー
                title = "📊 価格確認"
                description = "価格に変動はありません"
        else:
            # 初回
            color = 0x0000ff  # 青色
            title = "🚌 監視開始"
            description = ""
        
        # Discord埋め込みメッセージを作成
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": [
                {
                    "name": "現在の価格(非会員)",
                    "value": f"**{min_price:,}円**",
                    "inline": False
                },
                {
                    "name": "🔗 予約ページへ",
                    "value": f"[こちらをクリック]({self.url})",
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "さくら高速バス 価格監視"
            }
        }
        
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
            
            print(f"✅ 価格取得成功")
            print(f"   最安値: {min_price:,}円")
            print(f"   最高値: {max_price:,}円")
            print(f"   全価格: {', '.join([f'{p:,}円' for p in all_prices])}")
            
            # 前回の価格を読み込み
            previous_data = self.load_previous_prices()
            
            # 通知を送信（毎回）
            self.send_discord_notification(current_data, previous_data)
            
            if previous_data and previous_data.get('status') == 'success':
                prev_min = previous_data.get('min_price')
                if min_price == prev_min:
                    print("   価格変動なし")
                else:
                    print("   価格変動あり")
            
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
    WEBHOOK_URL = "https://discord.com/api/webhooks/1448050592848281612/Y6rkHw3VEQLL-wxyF1J7UUBNU4_tT6C8xHLu55b85rsx6ECIIoT3hJDppxj82KEiHJHK"  # ここにDiscord Webhook URLを設定
    
    monitor = BusPriceMonitor(URL, WEBHOOK_URL)
    monitor.check_and_notify()


if __name__ == "__main__":
    main()
