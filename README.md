🎤 Termina（Mac用音声入力アプリ）

TerminaはPythonで作られたmacOSのメニューバー常駐アプリです。音声入力を取得し、AI音声認識で文字起こしを行い、その結果を現在アクティブなアプリケーションにテキストとしてペーストします。

⸻

✅ 主な機能
	•	メニューバーアイコンから音声コントロール
	•	手動録音開始・停止（任意の長さで録音可能）
	•	音声から変換されたテキストを現在のアクティブアプリにペースト
	•	**3つの音声認識プロバイダー対応**：
	  - 🚀 **FFmpeg + Whisper.cpp**（超高速・完全ローカル・GPU対応）
	  - 🌐 **OpenAI Whisper API**（高精度・クラウド）
	  - 💻 **Local Whisper (PyTorch)**（オフライン・中程度）
	•	グローバルホットキー対応（⌘+Shift+V で録音開始・停止）
	•	高度な音声前処理（FFmpeg統合ノイズ除去）

⸻

🧰 技術スタック

機能構成	使用技術
使用言語	Python 3.9以上
パッケージ管理	uv（サポート対象）
メニューバーUI	rumps
音声録音	sounddevice, scipy.io.wavfile
音声認識	OpenAI Whisper API・whisper.cpp・openai-whisper
テキスト入力	osascript（AppleScript経由）
環境変数管理	python-dotenv
グローバルホットキー	pynput
音声前処理	FFmpeg (ノイズ除去)


⸻

🚀 はじめかた

### 前提条件
- macOS 10.14以上
- Python 3.9以上
- uv（推奨パッケージマネージャー）
- マイクアクセス許可
- アクセシビリティアクセス許可（テキスト入力用）

### 🚀 推奨：FFmpeg + Whisper.cpp（超高速ローカル音声認識）
```bash
# FFmpeg 8.0 と whisper.cpp をインストール
brew install ffmpeg whisper-cpp

# Whisperモデルをダウンロード（例：base モデル）
python download_whisper_models.py download base
```

### オプション設定
**OpenAI APIキー**（クラウド音声認識用・オプション）：[OpenAI Platform](https://platform.openai.com/)で取得

### インストール手順（uv）

1. **リポジトリをクローン**
```bash
git clone https://github.com/your-username/termina.git
cd termina
```

2. **uvをインストール（推奨）**
```bash
# macOSの場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# またはHomebrewを使用
brew install uv
```

3. **依存関係をインストール**
```bash
uv sync
```

4. **音声認識プロバイダーを設定**

`.env.local`ファイルを作成して設定：
```bash
# OpenAI APIを使用する場合（推奨）
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env.local
echo "SPEECH_PROVIDER=openai" >> .env.local
```

または手動で`.env.local`ファイルを作成し、以下の内容を記述：
```
# OpenAI Whisper API (推奨)
OPENAI_API_KEY=your-openai-api-key-here
SPEECH_PROVIDER=openai

# またはローカルWhisper使用（オフライン, PyTorch）
# SPEECH_PROVIDER=local
```

5. **アプリを実行**
```bash
uv run python termina.py
```

### ローカルWhisper（PyTorch, オフライン音声認識）の使用

インターネット不要でプライバシーを重視する場合：

1. **openai-whisperをインストール**
```bash
uv add openai-whisper
```

2. **設定ファイルを更新**（プロバイダキーを `local` に統一）
```bash
echo "SPEECH_PROVIDER=local" >> .env.local
```

3. **初回使用時にモデル自動ダウンロード**
- 初回使用時に選択したモデルが自動ダウンロード
- メニューバー > Speech Provider > Manage Local Models でモデル情報確認

### 初回実行時の設定

初回実行時には以下の許可が必要になる場合があります：

1. **マイクアクセス許可**: システム設定 → セキュリティとプライバシー → マイク
2. **アクセシビリティアクセス許可**: システム設定 → セキュリティとプライバシー → アクセシビリティ
   - System Events でのテキスト入力に必要

### 使用方法

#### メニューバーから操作
1. アプリを実行すると、メニューバーに 🎤 アイコンが表示されます
2. ペーストしたいアプリケーション（テキストエディタ、チャットアプリなど）をアクティブにします
3. メニューバーアイコンをクリックして「Start Recording」を選択
4. 録音が開始されます（通知で確認できます）
5. 話し終わったら再度アイコンをクリックして「Stop Recording」を選択
6. 音声がテキストに変換され、アクティブなアプリケーションにペーストされます
7. ペースト結果は通知で確認できます

#### ホットキーで操作
- **⌘+Shift+V**: 録音の開始・停止を切り替え
- どのアプリからでもホットキーで録音をコントロール可能

#### 🎯 音声認識プロバイダーの選択

メニューバー > Speech Provider で切り替え可能

| プロバイダー | 精度 | 速度 | GPU加速 | オフライン | コスト | 推奨用途 |
|-------------|------|------|---------|----------|--------|----------|
| 🚀 **FFmpeg + Whisper.cpp** | **最高** | **超高速** | ✅ Metal | ✅ | **無料** | **日常使用・高頻度** |
| 🌐 **OpenAI API** | 最高 | 高速 | - | ❌ | 従量課金 | たまに使用・最高精度 |
| 💻 **Local Whisper (PyTorch)** | 高い | 中速 | ❌ | ✅ | 無料 | 学習・実験用 |

#### 🚀 Whisper.cpp モデル管理

**モデルダウンロード**:
```bash
# 推奨：バランス重視
python download_whisper_models.py download base

# 利用可能なモデル一覧
python download_whisper_models.py list

# 全モデルダウンロード
python download_whisper_models.py download-all
```

**モデル選択**: メニューバー > Speech Provider > Whisper.cpp Models

| モデル | サイズ | 精度 | GPU速度 | CPU速度 | 推奨用途 |
|--------|--------|------|---------|---------|----------|
| **tiny** | 39MB | ★★☆ | 超高速 | 高速 | テスト・軽量 |
| **base** | 142MB | ★★★ | 高速 | 普通 | **推奨・日常** |
| **small** | 466MB | ★★★★ | 普通 | やや遅い | 高品質 |
| **medium** | 1.5GB | ★★★★ | やや遅い | 遅い | 精度重視 |
| **large-v3** | 2.9GB | ★★★★★ | 遅い | 最遅 | 最高精度 |

#### 💻 PyTorch Whisper モデル（自動ダウンロード）

メニューバー > Speech Provider > PyTorch Model Size から選択：

| モデル | サイズ | 精度 | 速度 | 推奨用途 |
|--------|--------|------|------|----------|
| tiny | 39MB | 低い | 最高速 | テスト・実験 |
| base | 142MB | 普通 | 高速 | バランス |
| small | 466MB | 良い | 普通 | 一般用途 |
| medium | 1.5GB | 高い | やや遅い | 精度重視 |
| large | 3.1GB | 最高 | 遅い | 最高精度 |

### トラブルシューティング

- **「Please create a .env.local file」エラー**: `.env.local`ファイルが作成されているか、APIキーが正しく設定されているか確認
- **マイクが認識されない**: システム設定でアプリにマイクアクセス許可を与える
- **テキストがペーストされない**: システム設定でアクセシビリティアクセス許可を確認
- **日本語が正しく認識されない**: 音声認識はja（日本語）に設定済み、はっきりと話してください
- **録音が停止しない**: メニューから「Stop Recording」を選択してください
- **ホットキーが動作しない**: システム設定でアクセシビリティアクセス許可を確認してください

⸻

💾 動作の流れ（更新済み）
	1.	メニューの “Start Recording” をクリックすると、5秒間マイクから音声を録音。
	2.	録音ファイルを temp.wav に保存。
	3.	Whisper APIに送信して文字起こし。
	4.	Whisper APIに送信して日本語文字起こし。
	5.	結果のテキストをクリップボード経由で現在アクティブなアプリケーションにペースト。

⸻

## 🛠️ 開発者向け

### 開発環境のセットアップ
```bash
# 開発用依存関係をインストール
make dev-setup

# または手動でインストール
uv sync --group dev
```

### 開発用コマンド
```bash
# アプリを実行
make run

# コード品質チェック
make quality

# テストを実行
make test

# コードフォーマット
make format

# セキュリティチェック
make security

# 全てのチェックを実行
make check

# ヘルプを表示
make help
```

### 開発はuvで行います
uv を使ったワークフローのみサポートします（pip 手順は廃止）。

🧠 今後の改善予定
	•	⚙️ ホットキーのカスタマイズ機能
	•	🎧 無音検出による自動録音停止
	•	💬 テキストペースト前の確認プロンプト
	•	🎯 録音時間の表示
	•	📝 録音履歴の保存・管理
	•	🎛️ モデル精度の選択機能（tiny/base/small/medium/large）

⸻

⚠️ 注意事項
	•	macOS専用（メニューバーUIとAppleScript使用のため）
	•	System Events 使用のためアクセシビリティアクセス許可が必要
	•	マイクアクセスの許可が必要（システム設定→セキュリティとプライバシー）
	•	Whisper APIの利用にはインターネット接続と従量課金が必要です
	•	録音は最大10分間まで（それ以上は自動停止）
	•	日本語音声認識に最適化されています

⸻

📜 ライセンス

MIT License
