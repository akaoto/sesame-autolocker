#!/usr/bin/env python3

import base64
import datetime
import json
import requests
from Crypto.Hash import CMAC
from Crypto.Cipher import AES


class SesameStatus:
    def getStatus(self):
        res = self._request('GET', '')
        return res.json()


class SesameHistory:
    HISTORY_NONE = 0
    HISTORY_BLE_LOCK = 1
    HISTORY_BLE_UNLOCK = 2
    HISTORY_TIME_CHANGED = 3
    HISTORY_AUTO_LOCK_UPDATED = 4
    HISTORY_MECH_SETTING_UPDATED = 5
    HISTORY_AUTO_LOCK = 6
    HISTORY_MANUAL_LOCKED = 7
    HISTORY_MANUAL_UNLOCKED = 8
    HISTORY_MANUAL_ELSE = 9
    HISTORY_DRIVE_LOCKED = 10
    HISTORY_DRIVE_UNLOCKED = 11
    HISTORY_DRIVE_FAILED = 12
    HISTORY_BLE_ADV_PARAMETER_UPDATED = 13
    HISTORY_WM_2_LOCK = 14
    HISTORY_WM_2_UNLOCK = 15
    HISTORY_WEB_LOCK = 16
    HISTORY_WEB_UNLOCK = 17

    def getHistories(self, page, lg):
        res = self._request('GET', f'/history?page={page}&lg={lg}')
        return res.json()

    def isManualUnlocked(self):
        lockEvents = [
            self.HISTORY_BLE_LOCK,
            self.HISTORY_AUTO_LOCK,
            self.HISTORY_MANUAL_LOCKED,
            self.HISTORY_DRIVE_LOCKED,
            self.HISTORY_WM_2_LOCK,
            self.HISTORY_WEB_LOCK
        ]
        unlockEventsBySesame = [
            self.HISTORY_BLE_UNLOCK,
            self.HISTORY_DRIVE_UNLOCKED,
            self.HISTORY_WM_2_UNLOCK,
            self.HISTORY_WEB_UNLOCK
        ]
        lg = 5
        maxPage = 10
        for page in range(maxPage):
            histories = self.getHistories(page, lg)
            for history in histories:
                if history['type'] in lockEvents:
                    return True
                elif history['type'] == self.HISTORY_MANUAL_UNLOCKED:
                    return True
                elif history['type'] in unlockEventsBySesame:
                    return False
        return True


class SesameCmd:
    CMD_LOCK = 82
    CMD_UNLOCK = 83
    CMD_TOGGLE = 88

    def lock(self):
        return self._cmd(self.CMD_LOCK)

    def unlock(self):
        return self._cmd(self.CMD_UNLOCK)

    def toggle(self):
        return self._cmd(self.CMD_TOGGLE)

    def _cmd(self, cmd):
        body = {
            'cmd': cmd,
            'history': base64.b64encode(bytes(self._history, 'utf-8')).decode(),
            'sign': self._createCmac()
        }
        res = self._request('POST', '/cmd', json.dumps(body))
        return res.ok

    def _createCmac(self):
        ts = int(datetime.datetime.now().timestamp())
        message = ts.to_bytes(4, byteorder='little')
        message = message.hex()[2:8]
        cmac = CMAC.new(bytes.fromhex(self._secretKey), ciphermod=AES)
        cmac.update(bytes.fromhex(message))
        return cmac.hexdigest()


class Sesame(SesameStatus, SesameHistory, SesameCmd):
    def __init__(self, uuid, apiKey, secretKey, history,):
        super().__init__()
        self._rootUrl = f'https://app.candyhouse.co/api/sesame2/{uuid}'
        self._apiKey = apiKey
        self._secretKey = secretKey
        self._history = history

    def _request(self, method, endpoint, data=None):
        headers = {'x-api-key': self._apiKey}
        res = requests.request(method, self._rootUrl + endpoint, headers=headers, data=data)
        return res
