#!/usr/bin/env python3
"""
バス価格監視システム - デモ版
実際のサイトにアクセスせず、モックデータでテストできます
"""

import json
from datetime import datetime
import random

class BusPriceMonitorDemo:
    def __init__(self, price_file='prices_demo.json'):
        self.price_file = price_file
        self.url = "https://www.489.fm/searchbus/tokyo_akita/_/day20251215/"
        
    def scrape_prices_mock(self):
        """モックデータで価格情報を返す"""
        # 実際のスクリーンショットから取得した価格
        base_prices = [6300, 7000, 7300, 8000]
        
        # ランダムに価格を変動させる（デモ用）
        if random.random() < 0.3:  # 30%の確率で価格変動
            change = random.choice([-500, -300, 300, 500])
            base_prices[0] = max(5000, base_prices[0] + change)
            base_prices = sorted(base_prices)
        
        return {
            'status': 'success',
            'prices': base_prices,
            'min_price': min(base_prices),
            'max_price': max(base_prices),
            'timestamp': datetime.now().isoformat()
        }
    
    def load_previous_prices(self):
        """前回の価格情報を読み込み"""
        try:
            with open(self.price_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def save_prices(self, data):
        """価格情報を保存"""
        with open(self.price_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def format_notification(self, message_type, current_data, previous_data=None):
        """通知メッセージをフォーマット"""
        if message_type == 'price_down':
            prev_min = previous_data.get('min_price')
            curr_min = current_data['min_price']
            diff = prev_min - curr_min
            
            message = f"""
╔═══════════════════════════════════╗
║     💰 値下がり検出！              ║
╚═══════════════════════════════════╝

前回: {prev_min:,}円 → 現在: {curr_min:,}円
✨ {diff:,}円 安くなりました！✨

📊 全価格:
{self._format_price_list(current_data['prices'])}

🔗 予約: {self.url}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
        elif message_type == 'price_up':
            prev_min = previous_data.get('min_price')
            curr_min = current_data['min_price']
            diff = curr_min - prev_min
            
            message = f"""
╔═══════════════════════════════════╗
║     📈 値上がり検出                ║
╚═══════════════════════════════════╝

前回: {prev_min:,}円 → 現在: {curr_min:,}円
⚠️ {diff:,}円 高くなりました

📊 全価格:
{self._format_price_list(current_data['prices'])}

🔗 予約: {self.url}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
        elif message_type == 'first_check':
            message = f"""
╔═══════════════════════════════════╗
║     🚌 監視開始                    ║
╚═══════════════════════════════════╝

現在の最安値: {current_data['min_price']:,}円

📊 全価格:
{self._format_price_list(current_data['prices'])}

🔗 予約: {self.url}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
        else:  # no_change
            message = f"""
╔═══════════════════════════════════╗
║     ✅ 価格変動なし                ║
╚═══════════════════════════════════╝

現在の最安値: {current_data['min_price']:,}円

📊 全価格:
{self._format_price_list(current_data['prices'])}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return message
    
    def _format_price_list(self, prices):
        """価格リストを整形"""
        lines = []
        for i, price in enumerate(prices, 1):
            if i == 1:
                lines.append(f"   🏆 最安: {price:,}円")
            else:
                lines.append(f"   💺 {price:,}円")
        return '\n'.join(lines)
    
    def check_and_notify(self):
        """価格をチェックして通知メッセージを生成"""
        print(f"\n{'='*70}")
        print(f"🔍 バス価格チェック開始")
        print(f"{'='*70}")
        print(f"⏰ 時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')}")
        print(f"🔗 URL: {self.url}")
        print(f"{'='*70}\n")
        
        # 現在の価格を取得（モック）
        current_data = self.scrape_prices_mock()
        
        if current_data['status'] == 'success':
            # 前回の価格を読み込み
            previous_data = self.load_previous_prices()
            
            if previous_data and previous_data.get('status') == 'success':
                prev_min = previous_data.get('min_price')
                curr_min = current_data['min_price']
                
                if curr_min < prev_min:
                    # 値下がり
                    message = self.format_notification('price_down', current_data, previous_data)
                    print(message)
                    
                elif curr_min > prev_min:
                    # 値上がり
                    message = self.format_notification('price_up', current_data, previous_data)
                    print(message)
                    
                else:
                    # 変動なし
                    message = self.format_notification('no_change', current_data)
                    print(message)
            else:
                # 初回チェック
                message = self.format_notification('first_check', current_data)
                print(message)
            
            # 現在の価格を保存
            self.save_prices(current_data)
            
            print(f"\n{'='*70}")
            print(f"✅ チェック完了 - 価格データを保存しました")
            print(f"{'='*70}\n")
        else:
            print(f"❌ エラー: {current_data.get('message', '不明なエラー')}")


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🚌 さくら高速バス 価格監視システム - デモ版             ║
║                                                                ║
║   東京 → 秋田 (2025年12月15日)                                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    monitor = BusPriceMonitorDemo()
    
    # 複数回実行してデモ
    for i in range(3):
        if i > 0:
            print(f"\n\n{'#'*70}")
            print(f"# {i+1}回目のチェック（デモ）")
            print(f"{'#'*70}\n")
            import time
            time.sleep(2)
        
        monitor.check_and_notify()
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  📝 このデモでは、モックデータを使用して価格監視の             ║
║     動作を確認しています。                                     ║
║                                                                ║
║  🚀 実際に使用する場合は:                                      ║
║     1. Discord Webhook URLを設定                               ║
║     2. GitHub Actionsで自動実行を設定                          ║
║     3. README.mdの手順に従ってセットアップ                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
