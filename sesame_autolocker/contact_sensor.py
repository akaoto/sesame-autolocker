#!/usr/bin/env python3

from bluepy import btle


class ServiceData:
    def __init__(self, sensorData=b'\00'*9):
        self.doorState = (sensorData[3] >> 1) & 0x03
        self.buttonPushCounter = sensorData[8] & 0x0f


class ContactSensorDelegate(btle.DefaultDelegate):
    def __init__(self, address):
        btle.DefaultDelegate.__init__(self)
        self._address = address
        self.serviceData = ServiceData()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr != self._address.lower():
            return
        for _, desc, value in dev.getScanData():
            if desc == '16b Service Data':
                payload = bytes.fromhex(value[4:])
                self.serviceData = ServiceData(payload)


class ContactSensor:
    DOOR_STATE_CLOSE = 0
    DOOR_STATE_OPEN = 1
    DOOR_STATE_TMEOUT = 2

    def __init__(self, address):
        delegate = ContactSensorDelegate(address)
        self._scanner = btle.Scanner().withDelegate(delegate)
        self._scanner.scan(1)

    def onDoorStateChange(self, doorState):
        pass

    def onButtonPushCounter(self, buttonPushCounter):
        pass

    async def run(self):
        events = {
            'doorState': self.onDoorStateChange,
            'buttonPushCounter': self.onButtonPushCounter
        }
        while True:
            oldServiceData = self._scanner.delegate.serviceData
            self._scanner.scan(0.1)
            newSeviceData = self._scanner.delegate.serviceData
            for key, event in events.items():
                self._diff(oldServiceData, newSeviceData, key, event)

    def _diff(self, oldServiceData, newServiceData, key, event):
        oldValue = getattr(oldServiceData, key)
        newValue = getattr(newServiceData, key)
        if oldValue != newValue:
            event(newValue)
