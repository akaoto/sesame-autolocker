#!/usr/bin/env python3

import asyncio
import logging
import yaml
from sesame_autolocker.sesame import Sesame
from sesame_autolocker.contact_sensor import ContactSensor

logging.basicConfig(
    filename="log/debug.log",
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p"
)


class AutoLocker(ContactSensor):
    def __init__(self):
        with open('config/config.yml') as f:
            config = yaml.safe_load(f)

        super().__init__(config['contact_sensor']['address'])
        self._autolockPreventionMode = config['sesame_autolocker']['lockout_prevention_mode']
        self._sesame = Sesame(
            config['sesame']['uuid'],
            config['sesame']['api_key'],
            config['sesame']['secret_key'],
            config['sesame']['history']
        )

    def onButtonPushCounter(self, buttonPushCounter):
        self._sesame.unlock()

    def onDoorStateChange(self, doorState):
        if doorState == self.DOOR_STATE_CLOSE:
            if self._autolockPreventionMode and self._sesame.isManualUnlocked():
                return
            self._sesame.lock()


def main():
    autoLocker = AutoLocker()
    asyncio.run(autoLocker.run())


if __name__ == '__main__':
    main()
