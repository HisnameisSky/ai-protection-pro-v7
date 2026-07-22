# AI Protection Pro Studio v7.0 🛡️
デジタルコンテンツをAIによる無断学習や泥棒から保護・暗号化するためのマルチツールです。

<!-- ここにドラッグ＆ドロップした画像を貼る -->
![App Screenshot]
<img width="644" height="679" alt="スクリーンショット 2026-07-22 14 29 57" src="https://github.com/user-attachments/assets/78820165-b685-4b67-87bb-d71f333b5039" />
<img width="642" height="571" alt="スクリーンショット 2026-07-22 14 30 35" src="https://github.com/user-attachments/assets/1853d51a-8b32-45f1-bcdd-0312f0ee85da" />
<img width="642" height="651" alt="スクリーンショット 2026-07-22 14 30 12" src="https://github.com/user-attachments/assets/bf575452-7556-40f1-a6f1-4ea5df3f2c3a" />

ーーー
# AI Protection Pro Studio v7.0 🛡️

デジタルコンテンツ（画像・音声・動画・文書）をAIによる無断学習や泥棒から保護・暗号化するためのマルチツールデスクトップアプリです。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 主な機能 (Features)

* **🖼️ 画像保護 & 署名**: 人間の目には目立ちにくい防止ノイズパターンと署名テキストを同時に埋め込み、AI学習を妨害します。
* **🔍 透かし検証**: 元画像/動画と保護後画像/動画の差分（ノイズ）を抽出し、可視化します。
* **📦 Secure ZIP**: 重要なファイルを暗号化（AES-256）付きZIPに圧縮します。
* **🎬 動画保護**: 全フレームに保護パターンを適用し、動画のAI学習を防止します。
* **🎵 音声資産保護**: 人間の耳には聞こえない19kHz帯域に所有者キー（暗号）を埋め込み、ボイスクローンを防御します。（備考：現在Wav書類でしか通じない）
* **📄 文書・コード保護**: PDF、Office文書、PythonコードなどをAES-256で完全暗号化/復元します。
* **🛡️ セキュリティ監査**: SHA-256ハッシュ検証やシステムログ記録機能を搭載しています。
* **🌐 多言語対応**: 日本語 (JPN) / 英語 (ENG) のワンタップ切り替えに対応しています。

---

## 🚀 使い方 (Setup & Run)

### 1. リポジトリのクローン (またはダウンロード)
```bash
git clone [https://github.com/HisnameisSky/ai-protection-pro-v7.git](https://github.com/HisnameisSky/ai-protection-pro-v7.git)
cd ai-protection-pro-v7

### 2. 必要なライブラリのインストール
Bash
pip install -r requirements.txt

### 3. アプリの起動
Bash
python main.py
