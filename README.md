# Arduino Projects Archive

## 概要 (Overview)
Arduinoを使用した組み込み開発の学習記録や、試作プロトタイプのコードをまとめたリポジトリです。
ロボット制御、センサー処理、IoT機器（SwitchBot）との連携など、ハードウェア制御に関する実験コードが含まれています。

## ディレクトリ構成 (Directory Structure)
各フォルダは独立したプロジェクトになっています。

| ディレクトリ名 | 概要・内容 | 使用技術・ハードウェア |
| :--- | :--- | :--- |
| **RobotSeminar_2024** | ロボットセミナーにて作成した制御プログラム。初心者向けに各種センサーやスイッチ、モータードライバなどを使用してコントローラーを用いてロボットを操作した。 | Arduino, IMUセンサ, モータードライバ |
| **SwitchbotMonitoring** | SwitchBotと連携した環境モニタリング、または操作を行うシステム。 | ESP32, SwitchBot API |
| **ControllerBox** | 自作コントローラーの入力制御プログラム。物理スイッチやポテンショメータの値を処理。 | Arduino, タクトスイッチ, 可変抵抗 |
| **LED_control** | Arduinoを使用して複数のLEDテープを同時制御。また、スイッチでのモード切替を行う。 | Arduino, LED |

## 使用技術 (Tech Stack)
* **Language**: C++ (Arduino Language)
* **Hardware**:
    * Arduino Mega / ESP32 
    * Sensors: IMU (加速度・ジャイロ), [その他センサ]
    * IoT: SwitchBot
* **IDE**: Arduino IDE 
