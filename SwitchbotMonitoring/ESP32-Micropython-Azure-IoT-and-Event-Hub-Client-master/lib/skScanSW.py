# ============================================================================
# skScanSW.py : スイッチのチャタリングをソフトウエアで防止する為のライブラリ
# ----------------------------------------------------------------------------
# VERSION DATE        BY                  CHANGE/COMMENT
# ----------------------------------------------------------------------------
# 1.00    2021-06-10  きむ茶工房(きむしげ)  Create
# ============================================================================
from machine import Timer

class ScanSW:
    SW_COUNTER = 3    # ピンの状態を3回読み出す
    SW_cnt  = 0
    SW_DATA = []      # 読み出すピンの番号を保存する変数
    sw_data = [[]]    # 読み出したピンの状態を管理する変数

    def tim_Interrupt(self, t):
        """ 10ms毎に起動するコールバック関数
            指定されたピンの状態を3回読み出し、全て同じ状態(1or0)なら、その値をピンの入力値とする
        """
        _l = len(self.SW_DATA)
        for _i in range(_l):
            self.sw_data[_i][self.SW_cnt] += 1  # 読込み回数のカウントを行う
            _d = self._pin(self.SW_DATA[_i]).value()
            self.sw_data[_i][self.sw_data[_i][self.SW_cnt]] = _d  # SWの状態を読込む
            if self.sw_data[_i][self.SW_cnt] > 1:
                if self.sw_data[_i][1] != self.sw_data[_i][self.sw_data[_i][self.SW_cnt]]:
                    # １回目の読込み値とSWの状態が異なる(2回目以降を1回目の値とする)
                    self.sw_data[_i][1] = self.sw_data[_i][self.sw_data[_i][self.SW_cnt]]
                    self.sw_data[_i][self.SW_cnt] = 1  # 1回目のカウント値
                if self.sw_data[_i][self.SW_cnt] >= self.SW_COUNTER:
                    # 読込み値が全て同じであるならその値をSWの状態とする
                    self.sw_data[_i][0] = self.sw_data[_i][1]
                    self.sw_data[_i][self.SW_cnt] = 0  # カウント値をリセット

    def __init__(self, pin, pindt):
        """ 初期化を行う
            pin - Pinのオブジェクトを指定
            pindt - チャタリングのスキャンをするピンの情報（リストで指定）
        """
        self.SW_cnt = self.SW_COUNTER + 1
        self._pin = pin
        # ピンの情報配列データを初期化
        _l = len(pindt)
        self.sw_data = [[0 for _i in range(self.SW_COUNTER + 2)] for _j in range(_l)]
        for _i in range(_l):
            self.SW_DATA.insert(_i, pindt[_i])
            self._pin(pindt[_i], self._pin.IN, self._pin.PULL_UP)
        # タイマーオブジェクトを作成し、10ms毎にコールバック関数を呼び出す様に初期化する
        tim = Timer(-1)  # 仮想のタイマーなのでid=-1とする
        tim.init(period=10, mode=Timer.PERIODIC, callback=self.tim_Interrupt)

    def read(self, pinno):
        """ スイッチの状態を読み出す
            pinho - 読み出すピンの番号
        """
        for _i in range(len(self.SW_DATA)):
            if pinno == self.SW_DATA[_i]:
                break
        return self.sw_data[_i][0]



