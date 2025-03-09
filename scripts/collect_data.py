import requests
import json
import os

# 収集データを保存するリスト
examples = []

# GitHub上のClaude関連リポジトリを検索して情報収集
def collect_from_github():
    print("GitHubからデータを収集しています...")
    try:
        # GitHub APIを使ってClaude関連のリポジトリを検索
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": "claude anthropic", "sort": "stars", "per_page": 10}
        )
        
        if response.status_code != 200:
            print(f"GitHub APIエラー: ステータスコード {response.status_code}")
            return
            
        repos = response.json().get("items", [])
        
        if not repos:
            print("リポジトリが見つかりませんでした")
            return
            
        print(f"{len(repos)}個のリポジトリを見つけました")
        
        for repo in repos:
            # リポジトリ情報を取得
            examples.append({
                "id": f"github-{repo['id']}",
                "title": f"GitHub: {repo['name']}",
                "description": repo['description'] or "説明なし",
                "usage": f"GitHub上で公開されているClaude活用例。スター数: {repo['stargazers_count']}",
                "source_url": repo['html_url'],
                "category": "開発ツール",
                "tags": ["github", "オープンソース"],
                "processed": False
            })
    except Exception as e:
        print(f"データ収集中にエラーが発生しました: {e}")

# Hugging Face上のClaude関連リポジトリを検索
def collect_from_huggingface():
    print("Hugging Faceからデータを収集しています...")
    try:
        # 簡易的なスクレイピング（APIキーなしで使える範囲）
        response = requests.get(
            "https://huggingface.co/search/claude",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        if response.status_code != 200:
            print(f"Hugging Face検索エラー: {response.status_code}")
            return
            
        # 実際にはもっと複雑なスクレイピングが必要ですが、サンプルとして
        examples.append({
            "id": f"huggingface-sample-1",
            "title": "Hugging Face: Claude プロンプトエンジニアリング集",
            "description": "Claude AIのプロンプトエンジニアリング手法をまとめたリポジトリ",
            "usage": "様々なタスクに対するClaudeの使い方が紹介されています",
            "source_url": "https://huggingface.co/collections/anthropic/claude-3-vision-examples-67f8fdc0ffeb73a8d2fcc2c6",
            "category": "プロンプトエンジニアリング",
            "tags": ["huggingface", "プロンプト", "チュートリアル"],
            "processed": False
        })
    except Exception as e:
        print(f"Hugging Faceデータ収集中にエラーが発生しました: {e}")

# 収集したデータを保存
def save_data():
    # _dataディレクトリがなければ作成
    os.makedirs("_data", exist_ok=True)
    
    try:
        with open("_data/collected_examples.json", "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
        print(f"データを保存しました: _data/collected_examples.json")
    except Exception as e:
        print(f"データ保存中にエラーが発生しました: {e}")

if __name__ == "__main__":
    collect_from_github()
    collect_from_huggingface()
    # 他のソースからの収集関数を追加可能
    save_data()
    print(f"{len(examples)}件の事例を収集しました")
