"""
PDF → CSV 自動抽出スクリプト
依存：tabula-py, pandas, java

https://www.expo2025.or.jp/wp/wp-content/uploads/0412_servicehours.pdf
をそのままCSV化する
"""
import tabula
import pandas as pd

# PDFファイルのパス（同一フォルダに保存済みとする）
pdf_path = "0412_servicehours.pdf"

# PDF内のすべてのテーブルを抽出
dfs = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

# 複数テーブルが抽出された場合、ひとつに結合
df = pd.concat(dfs, ignore_index=True)
print("抽出されたデータフレームの形状:", df.shape)

# 例：Tabula の抽出結果が12カラムの場合
# ※下記カラム名は、PDF中のデータ（例：時間が“9:00”, “~”, “21:00” に分割されるなど）に合わせた仮の設定です。
new_columns = [
    "入場方法",         # 例："〇"（入場方法の指定）
    "所要時間",         # 例："30"（分）
    "通常営業時間開始",  # 例："9:00"
    "通常営業時間区切り",# 例："~"（タイムレンジの区切り記号）
    "通常営業時間終了",  # 例："21:00"
    "本日営業時間開始",  # 例："12:30"
    "本日営業時間区切り",# 例："~"
    "本日営業時間終了",  # 例："21:00"
    "予約備考",         # 例："関係者のみによる式典を予定(Due to the opening ceremony)"
    "ゾーン",           # 例："C03"
    "パビリオン名称",     # 例："KYy Germany"
    "予備"              # 抽出時の余分なカラム（空白またはその他）
]

# DataFrameのカラム数が一致しているか確認
if len(df.columns) == len(new_columns):
    df.columns = new_columns
else:
    raise ValueError(f"カラム数の不一致: 抽出結果は {len(df.columns)} 列ですが、設定しようとしているカラムは {len(new_columns)} 列です。抽出結果を確認してカラム名リストを調整してください。")

# CSVファイルに出力（UTF-8 BOM付きでExcel互換）
output_csv = "expo2025_pavilions_full.csv"
df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"完了: {output_csv} に {len(df)} 件のパビリオン情報を保存しました。")
