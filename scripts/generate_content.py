import os
import json
import requests
from datetime import datetime

print("記事生成スクリプトを開始します...")

# 環境変数からAPIキーを取得
api_key = os.environ.get('CLAUDE_API_KEY')

if not api_key:
    print("エラー: CLAUDE_API_KEYが設定されていません")
    exit(1)

# データファイルを読み込み
try:
    print("収集したデータを読み込んでいます...")
    if os.path.exists('_data/collected_examples.json'):
        with open('_data/collected_examples.json', 'r', encoding='utf-8') as f:
            examples = json.load(f)
        print(f"{len(examples)}件のデータを読み込みました")
    else:
        print("警告: データファイルが見つかりません。空のリストで始めます。")
        examples = []
except json.JSONDecodeError as e:
    print(f"警告: データファイルの形式が正しくありません: {e}")
    print("空のリストで始めます。")
    examples = []

# _postsディレクトリが存在しない場合は作成
os.makedirs("_posts", exist_ok=True)
print("_postsディレクトリを確認しました")

# Claude APIの設定
headers = {
    'x-api-key': api_key,
    'content-type': 'application/json',
    'anthropic-version': '2023-06-01'
}

# 未処理の事例を処理
processed_count = 0

for example in examples:
    if not example.get('processed'):
        print(f"処理中: {example['title']}")
        
        # Claude APIにリクエスト
        prompt = f"""
        以下の海外でのClaude活用事例を、日本語で分かりやすく解説してください。
        以下の構成で記事を書いてください:
        
        1. 概要: この事例の簡潔な説明（100〜150文字）
        2. 詳細な使い方: 具体的な活用方法のステップバイステップ解説
        3. 日本での応用方法: 日本語環境や日本市場での応用アイデア
        4. プロンプト例: この事例で使われているプロンプトのサンプル
        
        情報:
        タイトル: {example['title']}
        説明: {example['description']}
        使用方法: {example['usage']}
        URL: {example.get('source_url', 'なし')}
        """
        
        try:
            print("Claude APIにリクエストを送信中...")
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    'model': 'claude-3-opus-20240229',
                    'max_tokens': 2000,
                    'messages': [{'role': 'user', 'content': prompt}]
                }
            )
            
            if response.status_code != 200:
                print(f"API呼び出しエラー: ステータスコード {response.status_code}")
                print(f"レスポンス: {response.text}")
                continue
                
            response_data = response.json()
            content = response_data['content'][0]['text']
            
            # Jekyllの記事として保存
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"_posts/{date_str}-{example['id']}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"""---
layout: post
title: "{example['title']}"
category: {example['category']}
tags: {json.dumps(example['tags'], ensure_ascii=False)}
source_url: "{example.get('source_url', '')}"
prompt_included: true
---

{content}
""")
            
            print(f"記事を生成しました: {filename}")
            
            # 処理済みとしてマーク
            example['processed'] = True
            processed_count += 1
            
        except Exception as e:
            print(f"エラー発生: {e}")
            continue

# 更新されたデータを保存
try:
    with open('_data/collected_examples.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    print("更新されたデータを保存しました")
except Exception as e:
    print(f"データ保存中にエラーが発生しました: {e}")

print(f"処理完了: {processed_count}件の記事を生成しました")
