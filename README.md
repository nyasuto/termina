🎤 WhisperTerm（Mac用ターミナル音声コマンド）

WhisperTermはPythonで作られたmacOSのメニューバー常駐アプリです。音声入力を取得し、OpenAIのWhisper APIで文字起こしを行い、その結果をターミナルコマンドとして送信します。

⸻

✅ 主な機能
	•	メニューバーアイコンから音声コントロール
	•	ホットキーで録音開始（今後対応予定）
	•	音声から変換されたテキストをTerminalに送信
	•	OpenAI Whisper APIを利用した文字起こし

⸻

🧰 技術スタック

機能構成	使用技術
使用言語	Python 3.9以上
メニューバーUI	rumps
音声録音	sounddevice, scipy.io.wavfile
音声認識	OpenAI Whisper API（openaiライブラリ）
ターミナル操作	osascript（AppleScript経由）


⸻

🚀 はじめかた

### 前提条件
- macOS 10.14以上
- Python 3.9以上
- OpenAI APIキー（[OpenAI Platform](https://platform.openai.com/)で取得）
- マイクアクセス許可

### インストール手順

1. **リポジトリをクローン**
```bash
git clone https://github.com/your-username/whisperterm.git
cd whisperterm
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

4. **OpenAI APIキーを設定**

`.env.local`ファイルを作成してAPIキーを設定：
```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env.local
```

または手動で`.env.local`ファイルを作成し、以下の内容を記述：
```
OPENAI_API_KEY=your-openai-api-key-here
```

5. **アプリを実行**
```bash
python whisper_menu_app.py
```

### 初回実行時の設定

初回実行時には以下の許可が必要になる場合があります：

1. **マイクアクセス許可**: システム設定 → セキュリティとプライバシー → マイク
2. **ターミナルアプリへのアクセス許可**: AppleScript実行時に確認ダイアログが表示されます

### 使用方法

1. アプリを実行すると、メニューバーに 🎤 アイコンが表示されます
2. アイコンをクリックして「Start Recording」を選択
3. 5秒間音声を録音（録音中は通知で確認できます）
4. 音声がテキストに変換され、自動的にTerminalで実行されます
5. 実行結果は通知で確認できます

### トラブルシューティング

- **「Please create a .env.local file」エラー**: `.env.local`ファイルが作成されているか、APIキーが正しく設定されているか確認
- **マイクが認識されない**: システム設定でアプリにマイクアクセス許可を与える
- **Terminalでコマンドが実行されない**: AppleScriptのアクセス許可を確認

⸻

💾 動作の流れ
	1.	メニューの “Start Recording” をクリックすると、5秒間マイクから音声を録音。
	2.	録音ファイルを temp.wav に保存。
	3.	Whisper APIに送信して文字起こし。
	4.	結果のテキストをAppleScript経由でTerminalに送信。

⸻

🧠 今後の改善予定
	•	⌨️ グローバルホットキー対応（pynputやkeyboardを使用、アクセシビリティ許可が必要）
	•	🎧 無音検出による動的な録音時間調整
	•	💬 コマンド実行前の確認プロンプト
	•	🛠 オフラインで使えるWhisper（whisper.cpp）への対応

⸻

⚠️ 注意事項
	•	macOS専用（メニューバーUIとAppleScript使用のため）
	•	osascript 実行時にTerminalで毎回新しい行が開かれます
	•	マイクアクセスの許可が必要（システム設定→セキュリティとプライバシー）
	•	Whisper APIの利用にはインターネット接続と従量課金が必要です

⸻

📜 ライセンス

MIT License