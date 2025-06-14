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

1. リポジトリをクローン

git clone https://github.com/your-username/whisperterm.git
cd whisperterm

2. 仮想環境を作成（推奨）

python3 -m venv venv
source venv/bin/activate

3. 必要なライブラリをインストール

pip install -r requirements.txt

requirements.txt の内容

rumps
sounddevice
scipy
openai

4. OpenAI APIキーを設定

環境変数として設定するか、スクリプト内に直接記述します：

export OPENAI_API_KEY="your-key-here"

もしくはスクリプト内で：

openai.api_key = "your-key-here"

5. アプリを実行

python whisper_menu_app.py

実行後、メニューバーに 🎤 アイコンが表示され、「Start Recording」を選ぶと音声を録音してテキスト化し、Terminalに送信します。

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