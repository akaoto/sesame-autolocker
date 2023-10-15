# sesame-autolocker

## これは何?

[セサミ](https://jp.candyhouse.co/) と [SwithBot開閉センサー](https://www.switchbot.jp/collections/all/products/switchbot-contact-sensor) を連携させることにより下記機能を実現します。

- ドアを閉めるとすぐにオートロックします。
- (お気持ち程度の) 閉め出し防止機能があります。

### オートロックについて

セサミにはすでにオートロック機能があり、解錠してから一定時間経過後に施錠することで実現されています。

十分な機能ではあるのですが、時間の設定が悩ましいところです。
- 時間を短く設定するとドアをすぐ閉めなければなりません。
- 時間を長く設定すると施錠されるまでドアの前にいないと不安になってしまいます。

そこで閉扉を検知して施錠されるようにしました。

なお発売予定の[オープンセンサー](https://jp.candyhouse.co/products/sesame-opensensor) で公式対応されますが、発売時点ではセサミ5のみの対応、旧機種は今後対応予定 (時期未定) とのことです。

### 閉め出し防止機能について

閉め出される場合は鍵やスマートフォンを持っておらず、手動解錠しているはずです。
そこで手動解錠時には閉扉を検知しても施錠されないようにして閉め出し防止を試みました。

*<注意>*
- セサミの操作履歴から解錠方法を取得することにより実現しています。
- 手動解錠時、ネットワーク遅延などが発生した場合には誤検知して問答無用で締め出されてしまいます。
- ここで言う手動解錠に、SwitchBot開閉センサーのボタン押下による解錠は*含みません*。
   - 自動解錠していることを直感的に認識して閉め出しの可能性に気づくはずなのでよしとしました。
   - とはいえ鍵やスマートフォンを持たずに解錠できてしまうので注意です。
   - 妙案検討中。

## 動作確認環境

- Raspberry Pi3 Model B (Raspberry Pi OS Lite 11)
- Sesame4 + WiFiモジュール
- SwitchBot開閉センサー

## インストール

```
cd /home/pi
git clone https://github.com/akaoto/sesame-autolocker.git

cd sesame-autolocker
sudo apt install python3-pip libglib2.0-dev -y
sudo pip3 install -r requirements.txt

cd config
cp config.yml.sample config.yml
sudo cp sesame-autolocker.service.sample /etc/systemd/system/sesame-autolocker.service

sudo bash -c 'echo export PATH=\$PATH:/home/pi/sesame-autolocker >> /etc/profile'
```

`config.yml` や `sesame-autolocker.service` を適宜設定してください。
閉め出し防止機能の有効化のほか、開閉センサーのBDアドレスやセサミのUUID、APIキー、シークレットキーの設定が必要です。

設定後、サービスを有効化および起動してください。

```
sudo systemctl enable sesame-autolocker
sudo systemctl start sesame-autolocker
```

Raspberry PIではBluetoothが使えなくなることがあり再起動するまで復旧しないようです。
`monitor.sh` はサービス状態が停止している場合に再起動させるためのスクリプトです。
cronで定期実行する場合には `sudo crontab -e` で下記を設定してください。
これは5分毎に実行する場合の例です。

```
*/5 * * * * /home/pi/sesame-autolocker/monitor.sh
```

また、Raspberry PIはリードオンリー化しておくとよいかもしれません。

```
sudo raspi-config nonint enable_overlayfs
```
