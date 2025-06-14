🎤 Termina（Mac用音声入力アプリ）

TerminaはPythonで作られたmacOSのメニューバー常駐アプリです。音声入力を取得し、OpenAIのWhisper APIで文字起こしを行い、その結果を現在アクティブなアプリケーションにテキストとしてペーストします。

⸻

✅ 主な機能
	•	メニューバーアイコンから音声コントロール
	•	手動録音開始・停止（任意の長さで録音可能）
	•	音声から変換されたテキストを現在のアクティブアプリにペースト
	•	OpenAI Whisper APIを利用した日本語音声認識
	•	グローバルホットキー対応（⌘+H で録音開始・停止）

⸻

🧰 技術スタック

機能構成	使用技術
使用言語	Python 3.9以上
メニューバーUI	rumps
音声録音	sounddevice, scipy.io.wavfile
音声認識	OpenAI Whisper API（openaiライブラリ）
テキスト入力	osascript（AppleScript経由）
環境変数管理	python-dotenv
グローバルホットキー	pynput


⸻

🚀 はじめかた

### 前提条件
- macOS 10.14以上
- Python 3.9以上
- OpenAI APIキー（[OpenAI Platform](https://platform.openai.com/)で取得）
- マイクアクセス許可
- アクセシビリティアクセス許可（テキスト入力用）

### インストール手順

1. **リポジトリをクローン**
```bash
git clone https://github.com/your-username/termina.git
cd termina
```

2. **仮想環境を作成（推奨）**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **必要なライブラリをインストール**
```bash
pip install -r requirements.txt
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

# またはローカルWhisper使用（オフライン）
# SPEECH_PROVIDER=whisper_cpp
```

5. **アプリを実行**
```bash
python termina.py
```

### ローカルWhisper（オフライン音声認識）の使用

インターネット不要でプライバシーを重視する場合：

1. **openai-whisperをインストール**
```bash
pip install openai-whisper
```

2. **設定ファイルを更新**
```bash
echo "SPEECH_PROVIDER=whisper_cpp" >> .env.local
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
- **⌘+H**: 録音の開始・停止を切り替え
- どのアプリからでもホットキーで録音をコントロール可能

#### 音声認識プロバイダーの切り替え
- メニューバー > Speech Provider で切り替え可能
- 🌐 = インターネット必要、💻 = オフライン利用可能

| プロバイダー | 精度 | 速度 | オフライン | コスト | 初期サイズ |
|-------------|------|------|-----------|--------|-----------|
| OpenAI API 🌐 | 最高 | 高速 | ❌ | 従量課金 | 0MB |
| Local Whisper 💻 | 高い | 高速 | ✅ | 無料 | 3.1GB |

#### ローカルWhisperモデルサイズと精度

メニューバー > Speech Provider > Select Model Size から選択可能：

| モデル | サイズ | 精度 | 速度 | 推奨用途 |
|--------|--------|------|------|----------|
| tiny | 39MB | 低い | 最高速 | テスト・軽量環境 |
| base | 142MB | 普通 | 高速 | バランス重視 |
| small | 466MB | 良い | 普通 | 一般用途 |
| medium | 1.5GB | 高い | やや遅い | 精度重視 |
| large | 3.1GB | 最高 | 最遅い | 最高精度（デフォルト） |

**注意**: デフォルトで`large`モデルを使用します（最高精度）。メモリ不足の場合は小さなモデルを選択してください。

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