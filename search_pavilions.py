"""
以下のセットアップが必要です
pip install playwright pandas
playwright install chromium
"""
import asyncio
import pandas as pd
from playwright.async_api import async_playwright

# CSVファイル "pavilions.csv" からパビリオン名称のリストを取得（ヘッダーなし前提）
csv_file = "pavilions.csv"
df = pd.read_csv(csv_file, header=None, encoding="utf-8-sig")
keywords = df[0].dropna().apply(lambda s: s.strip()).tolist()

print(f"検索用ワードは {len(keywords)} 件取得できました。")
print(f"検索用ワード: {keywords}")

results = []

# 使用する検索ページのURL（必要に応じて最新のものに更新してください）
EXPO_URL = (
    "https://ticket.expo2025.or.jp/event_search/"
    "?id=YM772MRESE%2C9SJKCQATAC%2CVN22XT9M9G%2CBRM4AKTK83"
    "&screen_id=108&lottery=4&entrance_date=20250616"
)

async def search_expo_pavilion():
    async with async_playwright() as p:
        # ログイン済みセッションを利用するための persistent context
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/HP/AppData/Local/Google/Chrome/User Data",
            headless=False
        )
        page = await browser_context.new_page()
        
        # 指定のURLに移動。十分なタイムアウト時間を設定
        await page.goto(EXPO_URL, timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=60000)
        print(f"現在のURL: {page.url}")
        
        # 手作業でマイチケットから検索ページへ遷移してください。
        input("マイチケットの選択が終わったら Enter を押してください...")
        
        # 各キーワードごとの自動検索処理
        for kw in keywords:
            try:
                # 検索入力欄にキーワードを入力
                await page.fill("input.style_search_text__TH7D1", kw)
                # 検索ボタンをクリック
                await page.click("button.basic-btn.type2.style_search_btn__ZuOpx")
    
                # 検索結果の「該当なし」用のメッセージと、該当結果アイテムのどちらかが表示されるまで待機
                await page.wait_for_selector(
                    "p[data-message-code='SW_GP_DL_113_0012'], div.style_search_item_row__moqWC", 
                    timeout=30000
                )
    
                # まず該当なしメッセージの有無をチェック
                no_result = page.locator("p[data-message-code='SW_GP_DL_113_0012']")
                if await no_result.count() > 0:
                    message = (await no_result.text_content()).strip()
                    status = f"該当なし: {message}"
                else:
                    # 該当する検索結果アイテムがある場合
                    search_items = page.locator("div.style_search_item_row__moqWC")
                    count = await search_items.count()
                    details = []
                    for i in range(count):
                        item_title_locator = search_items.nth(i).locator("span.style_search_item_title__aePLg")
                        item_title = await item_title_locator.text_content()
                        details.append(item_title.strip())
                    status = f"該当あり（{count} 件）: {details}"
                    # 検索結果が見つかった場合はポーズしてユーザーに確認してもらう
                    input("検索結果が見つかりました。内容を確認して、次に進むには Enter を押してください...")
            except Exception as e:
                status = f"取得失敗: {str(e)}"
    
            results.append({"パビリオン名称": kw, "status": status})
            print(f"{kw} → {status}")
    
            # 次のキーワードに備え、再度検索ページへ戻る
            await page.goto(EXPO_URL, timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=60000)
    
        await browser_context.close()
    
    # 検索結果をCSVに出力
    out_df = pd.DataFrame(results)
    out_csv = "availability_results.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"完了: {out_csv} に {len(out_df)} 件の結果を書き出しました。")

if __name__ == "__main__":
    asyncio.run(search_expo_pavilion())
