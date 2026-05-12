# Upstream issues from `epoplavskis/pyit600`

Exported with GitHub CLI.

This is a maintainer backlog and historical reference for issues left in the
upstream Python client. It is intentionally not a normal support document. Use
it when looking for old protocol reports, device payload examples, gateway
firmware problems, or client behavior that may still be useful for future work.

---

## #48: UG800 stopped working after recent firmware update

- URL: https://github.com/epoplavskis/pyit600/issues/48
- State: open
- Author: @peterwholm-lab
- Created: 2025-11-18T18:53:19Z
- Updated: 2025-11-24T22:43:54Z
- Labels: none

### Issue body

My Salus UG800 gateway stopped working with Home Assistant after a recent firmware update. I know UG800 is not officially supported by pyit600, but it previously worked without issues using the same API behaviour.

After the update, pyit600 can no longer communicate with the gateway.

Device Versions:
- Gateway software version: 020300250804
- Coordinator version: 20250715

Since the recent firmware update, Home Assistant no longer receives any data from the UG800.
Symptoms match those reported here:

https://community.home-assistant.io/t/salus-ug800-integration/948763

Before the update, communication worked flawlessly.

Request:
- Is this something pyit600 might be able to support again?

### Conversation

_No comments._

---

## #47: UG800 stopped working after recent firmware update

- URL: https://github.com/epoplavskis/pyit600/issues/47
- State: closed
- Author: @peterwholm-lab
- Created: 2025-11-18T18:47:05Z
- Updated: 2025-11-18T20:42:24Z
- Labels: none

### Issue body

My Salus UG800 gateway stopped working with Home Assistant after a recent firmware update. I know UG800 is not officially supported by pyit600, but it previously worked without issues using the same API behaviour.

After the update, pyit600 can no longer communicate with the gateway.

Device Versions
	•	Gateway software version: 020300250804
	•	Coordinator version: 20250715

Since the recent firmware update, Home Assistant no longer receives any data from the UG800.
Symptoms match those reported here:

 https://community.home-assistant.io/t/salus-ug800-integration/948763

Before the update, communication worked flawlessly.

Request:
	•	Is this something pyit600 might be able to support again?


### Conversation

_No comments._

---

## #46: Compatibility with UG800

- URL: https://github.com/epoplavskis/pyit600/issues/46
- State: open
- Author: @vyagi
- Created: 2025-10-30T12:45:04Z
- Updated: 2025-11-11T12:15:20Z
- Labels: none

### Issue body

By any chance this library works with UG800 or some modifications are required or it is simply impossible?

### Conversation

#### @sasasilviu commented at 2025-11-11T12:15:20Z

It worked until the last version of Salus gateway. Now seems to be an issue regarding encryption. 

---

## #45: Is a gateway required?

- URL: https://github.com/epoplavskis/pyit600/issues/45
- State: open
- Author: @geohwk
- Created: 2025-09-29T12:25:08Z
- Updated: 2025-09-29T12:29:06Z
- Labels: none

### Issue body

I am looking into getting an RX30RF for my boiler, essentially trying to replace an old RF thermostat/controller but do I require a gateway for this to work? As far as I understand it the RX30RF is an zigbee device so can I not just connect directly to it circumventing the hub as I have my own zigbee hub in home assistant? Apologies that this is probably not the right place for this but am struggling to work out the best way to approach this. 

### Conversation

_No comments._

---

## #44: Problem with Salus FC600NH

- URL: https://github.com/epoplavskis/pyit600/issues/44
- State: open
- Author: @haegele100
- Created: 2025-09-23T17:02:48Z
- Updated: 2025-09-23T17:02:48Z
- Labels: none

### Issue body

Hello, I have a problem with the Salus FC600NH.
I'm getting an error message and can't access the FC600NH.
The system also has an FC600 installed. It's accessible and controllable. The gateway is the UG800.
Please help.

Dieser Fehler stammt von einer benutzerdefinierten Integration

Logger: pyit600
Quelle: custom_components/salus/climate.py:208
Integration: Salus iT600 (Dokumentation, Probleme)
Erstmals aufgetreten: 17:42:43 (12 Vorkommnisse)
Zuletzt protokolliert: 18:53:50

Bad logger message: Exception. %s / %s ((<class 'pyit600.exceptions.IT600CommandError'>, '("iT600 gateway rejected \'write\' command with content \'{\'requestAttr\': \'write\', \'id\': [{\'data\': {\'DeviceType\': 100, \'Endpoint\': 9, \'UniID\': \'001e5e09090d8691\'}, \'sIT600TH\': {\'SetHeatingSetpoint_x100\': 2450}}]}\'",)', IT600CommandError("iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e09090d8691'}, 'sIT600TH': {'SetHeatingSetpoint_x100': 2450}}]}'")))
write failed: {'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e09090d8691'}, 'sIT600TH': {'SetHeatingSetpoint_x100': 2600}}]}
Bad logger message: Exception. %s / %s ((<class 'pyit600.exceptions.IT600CommandError'>, '("iT600 gateway rejected \'write\' command with content \'{\'requestAttr\': \'write\', \'id\': [{\'data\': {\'DeviceType\': 100, \'Endpoint\': 9, \'UniID\': \'001e5e09090d8691\'}, \'sIT600TH\': {\'SetHeatingSetpoint_x100\': 2600}}]}\'",)', IT600CommandError("iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e09090d8691'}, 'sIT600TH': {'SetHeatingSetpoint_x100': 2600}}]}'")))
write failed: {'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e09090d8691'}, 'sIT600TH': {'SetHeatingSetpoint_x100': 2650}}]}
Bad logger message: Exception. %s / %s ((<class 'pyit600.exceptions.IT600CommandError'>, '("iT600 gateway rejected \'write\' command with content \'{\'requestAttr\': \'write\', \'id\': [{\'data\': {\'DeviceType\': 100, \'Endpoint\': 9, \'UniID\': \'001e5e09090d8691\'}, \'sIT600TH\': {\'SetHeatingSetpoint_x100\': 2650}}]}\'",)', IT600CommandError("iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e09090d8691'}, 'sIT600TH': {'SetHeatingSetpoint_x100': 2650}}]}'")))

### Conversation

_No comments._

---

## #43: Smoke sensors are not seen as binary_sensors

- URL: https://github.com/epoplavskis/pyit600/issues/43
- State: open
- Author: @samuellazea
- Created: 2025-02-26T19:50:21Z
- Updated: 2025-02-28T17:18:58Z
- Labels: none

### Issue body

Hello @jvitkauskas and @epoplavskis ,

I noticed that you are the authors and the maintainers for the https://pypi.org/project/pyit600/  . First of all I want to say that you guys done an amazing job and this helps me ( and other people :) ) lots. It's really appreciated.

Now the problem I see. I have homeassistant and I have installed the https://github.com/jvitkauskas/homeassistant_salus. 
It all worked well for like a month. I have in there a gateway, some thermostats, some door sensors and some smoke sensors. 

Now my problem, since a few days ( install was like a month ago ) I started to miss the smoke sensors. In HA they became unavailable. So I started to dig into it and wanted to see what was happening. I have to mention that the smoke sensors are online and available in the salus app.

So during my debugging I installed the pyit600 library ( had to do few minor changes to make it work. You can see https://github.com/epoplavskis/pyit600/pull/42 if you want ;) ) and then I started to debug to see what is going on. Here is part of the output:

`
root@32f54c65cdfe:/app/pyit600# python main.py --host 192.168.150.185 --euid xxxx--debug 
DEBUG:pyit600:Trying to connect to gateway at 192.168.150.185
DEBUG:pyit600:Gateway request: POST http://192.168.150.185:80/deviceid/read
{"requestAttr": "readall"}

DEBUG:pyit600:Gateway response:
{
    "id": [
        {
            "data": {
                "DeviceType": 100,
                "Endpoint": 1,
                "UniID": "xxxx"
            },
            "sGenSche": {
                "UpdateGenScheStatus": 0
            },
            "DeviceL": {
                "DeviceType": 100,
                "getModelIdentifierFlag_i": 1,
                "DeviceSubType": 1026,
                "UnquieID": "xxxx",
                "ClusterIDList_i": "xxxx#",
                "AttributeList": "xxxx",
                "ModelIdentifier_i": "SmokeSensor-EM",
                "DeviceEndpointNum_i": 1
            },
            "sZDO": {
                "ProtocalType_i": 2,
                "FirmwareVersion": "00000014",
                "ShortID_d": xxxx,
                "MACAddress": "xxxx",
                "LeaveNetwork": 0,
                "LeaveRequest_d": 0,
                "DeviceName": "{\"deviceName\":\"Senzor Fum Dormitor\",\"ShortID_d\":xxxx}"
            },
            "sBasicS": {
                "ManufactureName": "HEIMAN",
                "PowerSource": 3,
                "ModelIdentifier": "SmokeSensor-EM",
                "StackVersion_d": 2,
                "ApplicationVersion_d": 20,
                "HardwareVersion": "16"
            },
            "sEndpt": {
                "DeviceType": 1026,
                "Endpoint_i": 1
            },
            "sZDOInfo": {
                "JoinConfigEnd": 0,
                "OnlineStatus_i": 1
            },
            "sOTA": {
                "OTAStatus_d": 0
            },
            "sPowerS": {
                "BatteryVoltage_x10": 30
            }
        },
        {
            "data": {
                "DeviceType": 100,
                "Endpoint": 1,
                "UniID": "xxxx"
            },
            "sGenSche": {
                "UpdateGenScheStatus": 0
            },
            "DeviceL": {
                "DeviceType": 100,
                "getModelIdentifierFlag_i": 1,
                "DeviceSubType": 1026,
                "UnquieID": "xxxx",
                "ClusterIDList_i": "xxxx#",
                "AttributeList": "xxxx",
                "ModelIdentifier_i": "SW600",
                "DeviceEndpointNum_i": 1
            },
            "sZDO": {
                "JoinConfigVersion_i": "240329",
                "ProtocalType_i": 2,
                "FirmwareVersion": "20240103",
                "ShortID_d": xxxx,
                "MACAddress": "xxxx",
                "LeaveNetwork": 0,
                "LeaveRequest_d": 0,
                "DeviceName": "{\"deviceName\":\"Usa Depozitare\",\"ShortID_d\":xxxx}"
            },
            "sBasicS": {
                "ManufactureName": "SALUS",
                "PowerSource": 3,
                "ModelIdentifier": "SW600",
                "ApplicationVersion_d": 1,
                "HardwareVersion": "0"
            },
            "sEndpt": {
                "DeviceType": 1026,
                "Endpoint_i": 1
            },
            "sZDOInfo": {
                "JoinConfigEnd": 1,
                "zigbeeOTAFailDebugCode_i": 2304,
                "OnlineStatus_i": 1,
                "zigbeeOTArespond_i": 0,
                "zigbeeOTATimeout_i": 4800
            },
            "sOTA": {
                "OTAStatus_d": 0,
                "OTAFirmwareURL_d": "xxxx"
            },
            "sIASZS": {
                "ZoneStatus_d": 0,
                "ErrorIASZSTrouble": 0,
                "ErrorIASZSTampered": 0,
                "ErrorIASZSAlarmed1": 0,
                "ErrorIASZSLowBattery": 0,
                "ErrorIASZSAlarmed2": 0,
                "ErrorIASZSACFault": 0,
                "ZoneState_d": 1
            },
            "sPowerS": {
                "BatteryVoltage_x10": 29,
                "BatteryVolThreshold3_x10_d": 25,
                "ErrorPowerSLowBattery": 0,
                "ErrorBatteryAlarmState_d": 0,
                "BatteryVolThreshold_x10_d": 21,
                "BatteryAlarmMask_d": 0,
                "BatteryVolThreshold1_x10_d": 22,
                "BatteryVolThreshold2_x10_d": 23
            },
            "sTempS": {
                "MeasuredValue_x100": 2495
            }
        },


...................................................................


All binary sensor devices:
{'xxxx': BinarySensorDevice(available=True, name='Usa Depozitare', unique_id='xxxx', is_on=False, device_class='window', data={'DeviceType': 100, 'Endpoint': 1, 'UniID': 'xxxx'}, manufacturer='SALUS', model='SW600', sw_version='20240103'), 'xxxx': BinarySensorDevice(available=True, name='Usa Living', unique_id='xxxx', is_on=False, device_class='window', data={'DeviceType': 100, 'Endpoint': 1, 'UniID': 'xxxx'}, manufacturer='SALUS', model='SW600', sw_version='20240103'), 'xxxx': BinarySensorDevice(available=True, name='Usa Dormitor', unique_id='xxxx', is_on=False, device_class='window', data={'DeviceType': 100, 'Endpoint': 1, 'UniID': 'xxxx'}, manufacturer='SALUS', model='SW600', sw_version='20240103')}
Binary sensor device xxxx status:
BinarySensorDevice(available=True, name='Usa Depozitare', unique_id='xxxx', is_on=False, device_class='window', data={'DeviceType': 100, 'Endpoint': 1, 'UniID': 'xxxx'}, manufacturer='SALUS', model='SW600', sw_version='20240103')
'Usa Depozitare' is on: False

.............................

`

Now I tried to find out why is this happening. Looking at the gateway code I see this

`
    async def _refresh_binary_sensor_devices(self, devices: List[Any], send_callback=False):
        local_devices = {}

        if devices:
            status = await self._make_encrypted_request(
                "read",
                {
                    "requestAttr": "deviceid",
                    "id": [{"data": device["data"]} for device in devices]
                }
            )

            for device_status in status["id"]:
                unique_id = device_status.get("data", {}).get("UniID", None)

                if unique_id is None:
                    continue

                try:
                    model: Optional[str] = device_status.get("DeviceL", {}).get("ModelIdentifier_i", None)
                    if model in ["it600MINITRV", "it600Receiver"]:
                        is_on: Optional[bool] = device_status.get("sIT600I", {}).get("RelayStatus", None)
                    else:
                        is_on: Optional[bool] = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1", None)

.............................................................................................................................................................................

        try:
            binary_sensors = list(
                filter(lambda x: "sIASZS" in x or
                                 ("sBasicS" in x and
                                  "ModelIdentifier" in x["sBasicS"] and
                                  x["sBasicS"]["ModelIdentifier"] in ["it600MINITRV", "it600Receiver"]), all_devices["id"])
            )

............................................................................................................................................................................................


`

In my case based on the output of the debug call from above my you can see that the smoke sensor doesn't have the "sIASZS" and in "sBasicS" the ModelIdentifier is not part of  ["it600MINITRV", "it600Receiver"]. This means that my smoke sensor **doesn't** meet the criteria and it's **excluded** from start. 

In order to add it in there I had to add the smoke sensor in the ModelIdentifier list like so:

`
        try:
            binary_sensors = list(
                filter(lambda x: "sIASZS" in x or
                                 ("sBasicS" in x and
                                  "ModelIdentifier" in x["sBasicS"] and
                                  x["sBasicS"]["ModelIdentifier"] in ["it600MINITRV", "it600Receiver", "SmokeSensor-EM"]), all_devices["id"])
            )
`

So now we are a step further cause he sees them in the _refresh_binary_sensor_devices 

`
    async def _refresh_binary_sensor_devices(self, devices: List[Any], send_callback=False):
        local_devices = {}
        _LOGGER.debug(f"!!!!!!! _refresh_binary_sensor_devices: {devices}")
`

But it's still excluded because of this

`
                try:
                    model: Optional[str] = device_status.get("DeviceL", {}).get("ModelIdentifier_i", None)
                    if model in ["it600MINITRV", "it600Receiver"]:
                        is_on: Optional[bool] = device_status.get("sIT600I", {}).get("RelayStatus", None)
                    elif model == "SmokeSensor-EM":
                        is_on = 0  # temporary indicates the alarm state
                    else:
                        is_on: Optional[bool] = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1", None)
`

After adding the 
                    elif model == "SmokeSensor-EM":
                        is_on = 0  # temporary indicates the alarm state

I get the smoke sensors in the list. Please note that is_on = 0 is just temporary to test why the smoke sensors were not in the list. At this moment I don't have physical access to the smoke sensors to trigger one and see what data I get in the response so I can track the correct alarm state.
The moment I can trigger one I will update here the issue. 

Hopefully I made myself understood from all of this digging and debugging. 
Please let me know if there is anything else I can do or do so we can get this fixed somehow ( of course if you guys agree with my above tryouts ;) )

Thank you and looking forward for your feedback

### Conversation

#### @samuellazea commented at 2025-02-28T17:18:56Z

As promised I come back with more debugging info. 
I have managed to trigger a smoke sensor and then the info I got is this

`

"data": {
                "DeviceType": 100,
                "Endpoint": 1,
                "UniID": "xxx"
            },
            "sGenSche": {
                "UpdateGenScheStatus": 0
            },
            "DeviceL": {
                "DeviceType": 100,
                "getModelIdentifierFlag_i": 1,
                "DeviceSubType": 1026,
                "UnquieID": "xxx",
                "ClusterIDList_i": "xxx#",
                "AttributeList": "xxx",
                "ModelIdentifier_i": "SmokeSensor-EM",
                "DeviceEndpointNum_i": 1
            },
            "status": "success",
            "sZDO": {
                "ProtocalType_i": 2,
                "FirmwareVersion": "00000014",
                "ShortID_d": xxx,
                "MACAddress": "xxx",
                "LeaveNetwork": 0,
                "LeaveRequest_d": 0,
                "DeviceName": "{\"deviceName\":\"Senzor Fum Bucatarie\",\"ShortID_d\":xxx}"
            },
            "sBasicS": {
                "ManufactureName": "HEIMAN",
                "PowerSource": 3,
                "ModelIdentifier": "SmokeSensor-EM",
                "StackVersion_d": 2,
                "ApplicationVersion_d": 20,
                "HardwareVersion": "16"
            },
            "sEndpt": {
                "DeviceType": 1026,
                "Endpoint_i": 1
            },
            "sZDOInfo": {
                "JoinConfigEnd": 0,
                "OnlineStatus_i": 1
            },
            "sOTA": {
                "OTAStatus_d": 0
            },
            "sPowerS": {
                "BatteryVoltage_x10": 30
            },
            "sIASZS": {
                "ZoneStatus_d": 32,
                "ErrorIASZSTampered": 0,
                "ErrorIASZSTrouble": 0,
                "ErrorIASZSAlarmed1": 0,
                "ErrorIASZSLowBattery": 0,
                "ErrorIASZSAlarmed2": 0,
                "ErrorIASZSACFault": 0
            }
        },

`

Basically here you can see a difference between a smoke sensor that was not triggered and one that was triggered

![Image](https://github.com/user-attachments/assets/afa2cfb3-b611-406e-8881-12db12036778)

So I went ahead and changed to this in my code

`

                try:
                    model: Optional[str] = device_status.get("DeviceL", {}).get("ModelIdentifier_i", None)
                    if model in ["it600MINITRV", "it600Receiver"]:
                        is_on: Optional[bool] = device_status.get("sIT600I", {}).get("RelayStatus", None)
                    **elif model == "SmokeSensor-EM":
                        # First try to get the standard alarm attribute
                        is_on = Optional[bool] = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1", None)
                        # If it doesn't exist, default to 0 (not alarmed)
                        if is_on is None:
                            is_on = 0**
                    else:
                        is_on: Optional[bool] = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1", None)
                    if is_on is None:
                        continue
                    if model == "SB600":
                        continue  # Skip button
                    device = BinarySensorDevice(
                        available=True if device_status.get("sZDOInfo", {}).get("OnlineStatus_i", 1) == 1 else False,

`

Please let me know what you think about this and if you agree with this I would be happy to create a PR for this. Thank you 

---

## #41: Debugging "Unknown error occurred while communicating with iT600 gateway"

- URL: https://github.com/epoplavskis/pyit600/issues/41
- State: open
- Author: @prupert
- Created: 2024-11-03T13:18:20Z
- Updated: 2024-11-03T13:20:49Z
- Labels: none

### Issue body

While working on the Home Assistant integration of a Salus UGE600 gateway, I noticed that the underlying `pyit600` library suddenly stopped being able to connect to the device. Because I believe that the gateway is configured correctly, and I am able to ping and HTTP the device IP address, I am looking for guidance how to further debug this issue. 

I have installed [pyit600](https://github.com/epoplavskis/pyit600) module on a VM to debug. I get the following errors:

```
% python main.py --host 192.168.x.25 --euid 001Exxxxxxxxxxxx --debug
```
Quickly gives the following output:
```
DEBUG:pyit600:Trying to connect to gateway at 192.168.x.25
DEBUG:pyit600:Gateway request: POST http://192.168.x.25:80/deviceid/read
{"requestAttr": "readall"}

(--- Logging error ---
Traceback (most recent call last):
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 922, in _make_encrypted_request
    with async_timeout.timeout(self._request_timeout):
         ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'Timeout' object does not support the context manager protocol

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/logging/__init__.py", line 1150, in emit
    msg = self.format(record)
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/logging/__init__.py", line 998, in format
    return fmt.format(record)
           ~~~~~~~~~~^^^^^^^^
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/logging/__init__.py", line 711, in format
    record.message = record.getMessage()
                     ~~~~~~~~~~~~~~~~~^^
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/logging/__init__.py", line 400, in getMessage
    msg = msg % self.args
          ~~~~^~~~~~~~~~~
TypeError: not all arguments converted during string formatting
Call stack:
  File "/redacted-path-tovenv/main.py", line 172, in <module>
    asyncio.run(main())
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 194, in run
    return runner.run(main)
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/base_events.py", line 708, in run_until_complete
    self.run_forever()
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/base_events.py", line 679, in run_forever
    self._run_once()
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/base_events.py", line 2027, in _run_once
    handle._run()
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/events.py", line 89, in _run
    self._context.run(self._callback, *self._args)
  File "/redacted-path-tovenv/main.py", line 72, in main
    await gateway.connect()
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 101, in connect
    all_devices = await self._make_encrypted_request(
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 956, in _make_encrypted_request
    _LOGGER.error("Exception. %s / %s", type(e), repr(e.args), e)
Message: 'Exception. %s / %s'
Arguments: (<class 'TypeError'>, '("\'Timeout\' object does not support the context manager protocol",)', TypeError("'Timeout' object does not support the context manager protocol")))
Traceback (most recent call last):
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 922, in _make_encrypted_request
    with async_timeout.timeout(self._request_timeout):
         ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'Timeout' object does not support the context manager protocol

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/redacted-path-tovenv/main.py", line 172, in <module>
    asyncio.run(main())
    ~~~~~~~~~~~^^^^^^^^
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/redacted-path-to-python/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/base_events.py", line 721, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/redacted-path-tovenv/main.py", line 72, in main
    await gateway.connect()
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 101, in connect
    all_devices = await self._make_encrypted_request(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
    )
    ^
  File "/redacted-path-tovenv/lib/python3.13/site-packages/pyit600/gateway.py", line 957, in _make_encrypted_request
    raise IT600CommandError(
        "Unknown error occurred while communicating with iT600 gateway"
    ) from e
pyit600.exceptions.IT600CommandError: Unknown error occurred while communicating with iT600 gateway
```

I tried the following already:
- Changed the EUID to `000000000000`: same output
- Confirmed that local WiFi mode was NOT disabled in Salus app 
- Made sure the device was reachable (ping and HTTP)
- Reboot the UGE600 gateway device

The mentioned URL in the debug output responds (quickly) to a curl request:
```
% curl -I http://192.168.x.25:80/deviceid/read
```
Quickly returns the following output:
```
HTTP/1.1 200 OK
Keep-Alive: timeout=5, max=199
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Date: Sun, 03 Nov 2024 13:15:30 GMT
Content-Length: 32
X-XSS-Protection: 1; mode=block
Connection: Keep-Alive
Accept-Ranges: bytes
```

So to me it seems that the Salus UGE600 device should be reachable. I am totally clueless as to why `line 957, in _make_encrypted_request raise IT600CommandError("Unknown error occurred while communicating with iT600 gateway"`

Details about the UGE600 device:
- Model: Universal Gateway
- Software version: `021720240719`
- Coordinator version: `20240613`

### Conversation

_No comments._

---

## #40: Can KL08RF output be controlled?

- URL: https://github.com/epoplavskis/pyit600/issues/40
- State: open
- Author: @ronniebach
- Created: 2024-08-04T08:30:30Z
- Updated: 2024-08-04T08:30:30Z
- Labels: none

### Issue body

I'm considering using Shelly Wall-display instead of Salus thermostats.

Can the output of the KL08RF be controlled through this API - thus the temperatur regulation can be done in Home Assistant?

### Conversation

_No comments._

---

## #39: HA not controlling Salus Thermostats

- URL: https://github.com/epoplavskis/pyit600/issues/39
- State: closed
- Author: @discodancerstu
- Created: 2024-05-24T13:19:45Z
- Updated: 2024-05-24T13:20:55Z
- Labels: none

### Issue body

HA is now not able to adjust/control my Salus thermostat temperatures, I can't figure out why.

I can see the entities and attributes, no problem, but adjusting the temperature of a thermostat in HA does not seem to get through to the thermostat.

However, HA can control the thermostat mode, ie from permanent hold to schedule etc.

If I manually adjust the temperature on the thermostat in the room, HA sees the adjustment.

So it my diagnosis is that HA isn't sending temperature adjustments through to the gateway, but the gateway sends information to HA.  Any ideas please?

### Conversation

#### @discodancerstu commented at 2024-05-24T13:20:53Z

Wong group, apologies!

---

## #38: Notice of transfer of ownership

- URL: https://github.com/epoplavskis/pyit600/issues/38
- State: closed
- Author: @jvitkauskas
- Created: 2023-10-30T19:24:24Z
- Updated: 2023-12-05T19:29:20Z
- Labels: none

### Issue body

I have transferred ownership of this repo, pyit600 python package and homeassistant_salus repo to @epoplavskis. Edgaras has volunteered to continue the development of this project.

### Conversation

_No comments._

---

## #37: Selling my Salus devices on eBay

- URL: https://github.com/epoplavskis/pyit600/issues/37
- State: closed
- Author: @jvitkauskas
- Created: 2023-10-11T21:30:52Z
- Updated: 2023-10-30T19:19:36Z
- Labels: none

### Issue body

Hi, I am selling another batch of my Salus devices on eBay. You may want to bid:

https://www.ebay.de/itm/186112299685
https://www.ebay.de/itm/186112301948
https://www.ebay.de/itm/186112305165
https://www.ebay.de/itm/186112315420
https://www.ebay.de/itm/186112319081
https://www.ebay.de/itm/186112320967
https://www.ebay.de/itm/186112325208
https://www.ebay.de/itm/186112327735
https://www.ebay.de/itm/186112328927
https://www.ebay.de/itm/186112331150
https://www.ebay.de/itm/186112339334
https://www.ebay.de/itm/186112339986
https://www.ebay.de/itm/186112340443
https://www.ebay.de/itm/186112341582

### Conversation

_No comments._

---

## #36: Maintainer wanted

- URL: https://github.com/epoplavskis/pyit600/issues/36
- State: closed
- Author: @jvitkauskas
- Created: 2023-02-10T19:27:37Z
- Updated: 2023-10-30T19:26:09Z
- Labels: help wanted

### Issue body

I am no longer developing this integration and therefore I am seeking someone who is willing to maintain it. Please contact me if you are interested.

### Conversation

#### @jvitkauskas commented at 2023-10-30T19:26:09Z

I have transferred ownership of this repo, pyit600 python package and homeassistant_salus repo to @epoplavskis. Edgaras has volunteered to continue the development of this project.

---

## #35: Selling my Salus devices on eBay

- URL: https://github.com/epoplavskis/pyit600/issues/35
- State: closed
- Author: @jvitkauskas
- Created: 2022-12-04T22:11:08Z
- Updated: 2023-10-11T21:37:49Z
- Labels: none

### Issue body

Hi, I am selling my Salus devices on eBay. You may want to bid:

https://www.ebay.de/itm/185684523634
https://www.ebay.de/itm/185684530276
https://www.ebay.de/itm/185684533779
https://www.ebay.de/itm/185684535419
https://www.ebay.de/itm/185684537226
https://www.ebay.de/itm/185684538688
https://www.ebay.de/itm/185684540335


### Conversation

#### @falkenhawk commented at 2023-09-25T11:55:35Z

@jvitkauskas Since it looks like you divorced salus, may I ask what other system did you migrate your setup to?

#### @jvitkauskas commented at 2023-10-11T21:37:49Z

I was originally supposed to install some kind of heating control system for my parents. Salus wireless system seemed to be a good choice because they forgot to lay the wires. Unfortunately, they also did not install oversized boxes for underfloor heating controls, so the controllers did not have any space to fit. In the end I've just made something custom with esp32 relays, esphome and those square small xiaomi bluetooth sensors.

---

## #34: SyntaxError: 'async with' outside async function

- URL: https://github.com/epoplavskis/pyit600/issues/34
- State: closed
- Author: @samezrp
- Created: 2022-11-22T07:26:59Z
- Updated: 2023-12-05T19:29:51Z
- Labels: none

### Issue body

I'm not python specialist, so could you help me with following error?

`SyntaxError: 'async with' outside async function`

I run script with following arguments:

`python3 get_dev.py 192.168.0.145 001E5E09xxxxxxxx`


edit:
never mind...
Eventually I run:
`python3 main.py --host 192.168.0.145 --euid 001E5E09xxxxxxxx`
with success

### Conversation

_No comments._

---

## #32: Unable to write fan mode to UGE600 for FC600 device

- URL: https://github.com/epoplavskis/pyit600/issues/32
- State: open
- Author: @efenex
- Created: 2022-07-23T10:23:58Z
- Updated: 2022-10-18T07:49:52Z
- Labels: none

### Issue body

While attempting to configure the HA integration I noticed that I am unable to change any settings. Narrowing it down to a minimal reproduction, I ended up with the following code:


```
import asyncio
import pyit600

async def go() -> asyncio.coroutine:
    gateway = pyit600.IT600Gateway(host="192.168.254.232", euid="001e5e09021f333d", debug=True)
    await gateway.connect()
    await gateway.poll_status()

    #climate_devices = gateway.get_climate_devices()

    #print("All climate devices:")
    #print(repr(climate_devices))

    #for climate_device_id in climate_devices:
    #    print(f"Climate device {climate_device_id} status:")
    #    print(repr(climate_devices.get(climate_device_id)))

    climate_device_id="001e5e0902626670"
    print(f"Setting heating device {climate_device_id} fan_mode to low")
    await gateway.set_climate_device_fan_mode(climate_device_id, "Low")

asyncio.run(go())
```

After fixing a few minor issues (renaming FAN_MODE_MID to FAN_MODE_MEDIUM and adding more debug entries), output is as follows:

```
Gateway request: POST http://192.168.254.232:80/deviceid/read
{"requestAttr": "readall"}

Gateway encrypted request: POST http://192.168.254.232:80/deviceid/read
b'\xe5\xa1![\xf9mv\xe6\xff\xd2,q6\xf8\xae\x1b\xc3\xc3\x12\xcd\x9e^\xe3\xda\x12u\xf6\x86\x83s5\xe5'

Gateway decrypted response:
{"status":"success","id":[{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":2,"FanMode_a":2},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625ea5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2600,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":34,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625ea5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625ea5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Hallway Thermostat\",\"ShortID_d\":49791}","FirmwareVersion":"003A0027","ShortID_d":49791,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"data":{"DeviceType":200,"Endpoint":0,"UniID":"0000000000000000"},"DeviceL":{"DeviceType":200,"DeviceSubType":0,"UnquieID":"0000000000000000","AttributeList":"000100040003001100050008000b00100033","ModelIdentifier_i":"SAU2AG1-ZC","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"DeviceName":"{\"deviceName\":\"Salus Gateway\",\"ShortID_d\":0}","LeaveRequest_d":0,"MACAddress":"001e5e09021f333d","FirmwareVersion":"20210813","LeaveNetwork":0,"ShortID_d":0},"sCoord":{"PANID_d":21441,"Form_d":1,"Channel_d":18,"TimeFormat24Hour":1,"PermitJoinState_d":0,"ErrorCoordUART":0,"ReceiveZigbeeCommand_d":"7c0f230300830e0900427e010000ea"},"sBasicS":{"ModelIdentifier":"SAU2AG1-ZC","HardwareVersion":"161"},"sEndpt":{"DeviceType":0,"Endpoint_i":0},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/7a40e413-cf77-4953-acf4-3d47d96ee033/SAU2AG1-ZC_20210813.tar.gz","OTAFirmwareVersion_d":"20210813","endPoint_i":0,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818"}},{"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902626670"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2000,"LocalTemperature_x100":2450,"CoolingSetpoint_x100":2000,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902626670","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902626670","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Reading Thermostat\",\"ShortID_d\":17481}","FirmwareVersion":"00360023","ShortID_d":17481,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","endPoint_i":9,"OTAStatus_d":3},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"Debug_d":"+2000+2000302102002102402102001415C000G51886E2A71A46E2AG51886E2A71A46E2A","AutoCoolingSetpoint_x100":0,"CoolingFanDelay":0,"HoldType":2,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010000611100000007FFF0000000000"}},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090256d8f7"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1600,"LocalTemperature_x100":2650,"CoolingSetpoint_x100":1600,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090256d8f7","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090256d8f7","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Guestroom Thermostat\",\"ShortID_d\":538}","FirmwareVersion":"003A0027","ShortID_d":538,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"data":{"DeviceType":300,"Endpoint":0,"UniID":"0000000000000000"},"DeviceL":{"DeviceType":300,"DeviceSubType":0,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e003100330036","ModelIdentifier_i":"SAU2AG1-GW","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sAyla_i":{"aylaNetWorkStatus":1,"aylaConfigStatus":1,"aylaDeviceID":"AC000W000624324","aylaGateWayDsn":"VR00ZN000787818","aylaTimeConfig":"1,1,60,1667091600","aylaSetUTCTimeStatus":1},"sGateway":{"GatewaySoftwareVersion":"020149211103","NetworkWiFiMAC":"00:1e:5e:01:b1:76","LEDMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","GatewayHardwareVersion":"161","NetworkWiFiIP":"","NetworkLANMAC":"00:1e:5e:01:b1:77","NetworkLANIP":"192.168.254.232","IsRtcRight_i":1,"DisableLocalMode":0,"NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","AylaConnected_i":1,"ModelIdentifier":"UG888","KeyState_i":0,"TimeOffset_i":1,"LANConnected_d":1,"WiFiConnected_d":0,"IsSdCardNormal_i":0,"PhoneLocation":"","DSTEnable_i":1,"DeviceTimeZone_i":3600,"LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509b38ce1a30d58225e0cc18de6db548e88","WiFiMode":0,"EnableNetworkReset":0,"WirelessAPpassword":"a3390e639c5e320d6c2177d3257fb5ea","TimeZone":"Europe/Belgrade","TimeStatus_i":2,"NetworkLANSubnet":"255.255.248.0","NetworkPriDNS":"192.168.254.254","NetworkLANRouterAddr":"192.168.254.254","NetworkSecDNS":"8.8.8.8","NetworkLANMode":1},"Product":{"Mode":1,"Model":"SAE2AG1"},"sAWSIoT":{"CertsStatus":0,"CertARN":"   "},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/167608df-3be8-4a90-a006-8bf523fcbacb/SAU2AG1-GW_020149211103.tar.gz","OTAFirmwareVersion_d":"020149211103","endPoint_i":0,"OTAStatus_d":0},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAE2AG1","AylaHeartBeatFrequency":0},"status":"success"},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625e0c"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1500,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1500,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":768,"UnquieID":"001e5e0902625e0c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625e0c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Office Thermostat\",\"ShortID_d\":4719}","FirmwareVersion":"003A0027","ShortID_d":4719,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":768,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":2400,"AutoHeatingSetpoint_x100":2100,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"sScheS":{"CoolSchedule1":"020f","CoolSchedule2":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":0,"FanMode_a":0},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090262659c"},"sDiadS":{"LastMessageRSSI_d":-65},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2100,"LocalTemperature_x100":2750,"CoolingSetpoint_x100":2100,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":0,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090262659c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090262659c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Children Thermostat\",\"ShortID_d\":3715}","FirmwareVersion":"003A0027","ShortID_d":3715,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010003011100000007FFF0000000000"}},{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1,"CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff"},"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625de5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625de5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625de5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Dining Thermostat\",\"ShortID_d\":4131}","FirmwareVersion":"003A0027","ShortID_d":4131,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}}]}

Gateway request: POST http://192.168.254.232:80/deviceid/read
{"requestAttr": "readall"}

Gateway encrypted request: POST http://192.168.254.232:80/deviceid/read
b'\xe5\xa1![\xf9mv\xe6\xff\xd2,q6\xf8\xae\x1b\xc3\xc3\x12\xcd\x9e^\xe3\xda\x12u\xf6\x86\x83s5\xe5'

Gateway decrypted response:
{"status":"success","id":[{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":2,"FanMode_a":2},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625ea5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2600,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":34,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625ea5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625ea5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Hallway Thermostat\",\"ShortID_d\":49791}","FirmwareVersion":"003A0027","ShortID_d":49791,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"data":{"DeviceType":200,"Endpoint":0,"UniID":"0000000000000000"},"DeviceL":{"DeviceType":200,"DeviceSubType":0,"UnquieID":"0000000000000000","AttributeList":"000100040003001100050008000b00100033","ModelIdentifier_i":"SAU2AG1-ZC","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"DeviceName":"{\"deviceName\":\"Salus Gateway\",\"ShortID_d\":0}","LeaveRequest_d":0,"MACAddress":"001e5e09021f333d","FirmwareVersion":"20210813","LeaveNetwork":0,"ShortID_d":0},"sCoord":{"PANID_d":21441,"Form_d":1,"Channel_d":18,"TimeFormat24Hour":1,"PermitJoinState_d":0,"ErrorCoordUART":0,"ReceiveZigbeeCommand_d":"7c0f230300830e0900427e010000ea"},"sBasicS":{"ModelIdentifier":"SAU2AG1-ZC","HardwareVersion":"161"},"sEndpt":{"DeviceType":0,"Endpoint_i":0},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/7a40e413-cf77-4953-acf4-3d47d96ee033/SAU2AG1-ZC_20210813.tar.gz","OTAFirmwareVersion_d":"20210813","endPoint_i":0,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818"}},{"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902626670"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2000,"LocalTemperature_x100":2450,"CoolingSetpoint_x100":2000,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902626670","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902626670","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Reading Thermostat\",\"ShortID_d\":17481}","FirmwareVersion":"00360023","ShortID_d":17481,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","endPoint_i":9,"OTAStatus_d":3},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"Debug_d":"+2000+2000302102002102402102001415C000G51886E2A71A46E2AG51886E2A71A46E2A","AutoCoolingSetpoint_x100":0,"CoolingFanDelay":0,"HoldType":2,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010000611100000007FFF0000000000"}},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090256d8f7"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1600,"LocalTemperature_x100":2650,"CoolingSetpoint_x100":1600,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090256d8f7","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090256d8f7","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Guestroom Thermostat\",\"ShortID_d\":538}","FirmwareVersion":"003A0027","ShortID_d":538,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"data":{"DeviceType":300,"Endpoint":0,"UniID":"0000000000000000"},"DeviceL":{"DeviceType":300,"DeviceSubType":0,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e003100330036","ModelIdentifier_i":"SAU2AG1-GW","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sAyla_i":{"aylaNetWorkStatus":1,"aylaConfigStatus":1,"aylaDeviceID":"AC000W000624324","aylaGateWayDsn":"VR00ZN000787818","aylaTimeConfig":"1,1,60,1667091600","aylaSetUTCTimeStatus":1},"sGateway":{"GatewaySoftwareVersion":"020149211103","NetworkWiFiMAC":"00:1e:5e:01:b1:76","LEDMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","GatewayHardwareVersion":"161","NetworkWiFiIP":"","NetworkLANMAC":"00:1e:5e:01:b1:77","NetworkLANIP":"192.168.254.232","IsRtcRight_i":1,"DisableLocalMode":0,"NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","AylaConnected_i":1,"ModelIdentifier":"UG888","KeyState_i":0,"TimeOffset_i":1,"LANConnected_d":1,"WiFiConnected_d":0,"IsSdCardNormal_i":0,"PhoneLocation":"","DSTEnable_i":1,"DeviceTimeZone_i":3600,"LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509b38ce1a30d58225e0cc18de6db548e88","WiFiMode":0,"EnableNetworkReset":0,"WirelessAPpassword":"a3390e639c5e320d6c2177d3257fb5ea","TimeZone":"Europe/Belgrade","TimeStatus_i":2,"NetworkLANSubnet":"255.255.248.0","NetworkPriDNS":"192.168.254.254","NetworkLANRouterAddr":"192.168.254.254","NetworkSecDNS":"8.8.8.8","NetworkLANMode":1},"Product":{"Mode":1,"Model":"SAE2AG1"},"sAWSIoT":{"CertsStatus":0,"CertARN":"   "},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/167608df-3be8-4a90-a006-8bf523fcbacb/SAU2AG1-GW_020149211103.tar.gz","OTAFirmwareVersion_d":"020149211103","endPoint_i":0,"OTAStatus_d":0},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAE2AG1","AylaHeartBeatFrequency":0},"status":"success"},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625e0c"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1500,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1500,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":768,"UnquieID":"001e5e0902625e0c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625e0c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Office Thermostat\",\"ShortID_d\":4719}","FirmwareVersion":"003A0027","ShortID_d":4719,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":768,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":2400,"AutoHeatingSetpoint_x100":2100,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"sScheS":{"CoolSchedule1":"020f","CoolSchedule2":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":0,"FanMode_a":0},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090262659c"},"sDiadS":{"LastMessageRSSI_d":-65},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2100,"LocalTemperature_x100":2750,"CoolingSetpoint_x100":2100,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":0,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090262659c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090262659c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Children Thermostat\",\"ShortID_d\":3715}","FirmwareVersion":"003A0027","ShortID_d":3715,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010003011100000007FFF0000000000"}},{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1,"CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff"},"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625de5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625de5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625de5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Dining Thermostat\",\"ShortID_d\":4131}","FirmwareVersion":"003A0027","ShortID_d":4131,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}}]}

Gateway request: POST http://192.168.254.232:80/deviceid/read
{"requestAttr": "deviceid", "id": [{"data": {"DeviceType": 300, "Endpoint": 0, "UniID": "0000000000000000"}}]}

Gateway encrypted request: POST http://192.168.254.232:80/deviceid/read
b'\xe5\xa1![\xf9mv\xe6\xff\xd2,q6\xf8\xae\x1bu\xc4o\xdc\xea\xe3x\xd5o-\xc5\xfb\x96\xc0L\x7f3\x180\x15aj\xd3\x98\x13\xf9\x1a!\x8d2\x91.\xb1\xd6\xf7q\xae\x13k\xdb1\xde5\x9e\xa7\xde=%\x10tDRU\x12\xc0\xddM\x1dDA\xaa_\xeeG/\x8a5{\x8a\xaf\x18\xb5\xa7-\xce:B\xef\x99\xf6\x03\x1fA(\xf3\xe0f\xe7\x80\xdaN\xf8]\xeb\xd6\xed'

Gateway decrypted response:
{"status":"success","id":[{"data":{"DeviceType":300,"Endpoint":0,"UniID":"0000000000000000"},"DeviceL":{"DeviceType":300,"DeviceSubType":0,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e003100330036","ModelIdentifier_i":"SAU2AG1-GW","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sAyla_i":{"aylaNetWorkStatus":1,"aylaConfigStatus":1,"aylaDeviceID":"AC000W000624324","aylaGateWayDsn":"VR00ZN000787818","aylaTimeConfig":"1,1,60,1667091600","aylaSetUTCTimeStatus":1},"sGateway":{"GatewaySoftwareVersion":"020149211103","NetworkWiFiMAC":"00:1e:5e:01:b1:76","LEDMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","GatewayHardwareVersion":"161","NetworkWiFiIP":"","NetworkLANMAC":"00:1e:5e:01:b1:77","NetworkLANIP":"192.168.254.232","IsRtcRight_i":1,"DisableLocalMode":0,"NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","AylaConnected_i":1,"ModelIdentifier":"UG888","KeyState_i":0,"TimeOffset_i":1,"LANConnected_d":1,"WiFiConnected_d":0,"IsSdCardNormal_i":0,"PhoneLocation":"","DSTEnable_i":1,"DeviceTimeZone_i":3600,"LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509b38ce1a30d58225e0cc18de6db548e88","WiFiMode":0,"EnableNetworkReset":0,"WirelessAPpassword":"a3390e639c5e320d6c2177d3257fb5ea","TimeZone":"Europe/Belgrade","TimeStatus_i":2,"NetworkLANSubnet":"255.255.248.0","NetworkPriDNS":"192.168.254.254","NetworkLANRouterAddr":"192.168.254.254","NetworkSecDNS":"8.8.8.8","NetworkLANMode":1},"Product":{"Mode":1,"Model":"SAE2AG1"},"sAWSIoT":{"CertsStatus":0,"CertARN":"   "},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/167608df-3be8-4a90-a006-8bf523fcbacb/SAU2AG1-GW_020149211103.tar.gz","OTAFirmwareVersion_d":"020149211103","endPoint_i":0,"OTAStatus_d":0},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAE2AG1","AylaHeartBeatFrequency":0},"status":"success"}]}

Gateway request: POST http://192.168.254.232:80/deviceid/read
{"requestAttr": "deviceid", "id": [{"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e0902625ea5"}}, {"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e0902626670"}}, {"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e090256d8f7"}}, {"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e0902625e0c"}}, {"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e090262659c"}}, {"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e0902625de5"}}]}

Gateway encrypted request: POST http://192.168.254.232:80/deviceid/read
b"\xe5\xa1![\xf9mv\xe6\xff\xd2,q6\xf8\xae\x1bu\xc4o\xdc\xea\xe3x\xd5o-\xc5\xfb\x96\xc0L\x7f3\x180\x15aj\xd3\x98\x13\xf9\x1a!\x8d2\x91.2\xb9\xc2P\x7f\xa9\x1a\xec\xbdn\x12\x89\x80\x12(\x84\x03\x0c\x0e:\xa6HKH\xe3\xee\xc4n\xc4\xfe\x8c{\xc5\x81\xee1\xb4\xa4\x14N\xe5\xd1\xcc\xe03R\x80\xa3U\x11X\x95I\x91\xce~\xf4Y\xc8\xa0\xb4\xd7>\xc6\xaf[I\xb9n\xc7\x1e\x9d\x95P\xb1\xa9\xd2\xdd#\xa2 \xcc4\x05\xe7|\xfd\x8f\x18\xd1\xabt\xacL\x90qu\xbc8\xcfC\xa1\x9cI?\x84\xbe\x1d2\x8a>\xfeO\r@z\xe9l\xf7\xe3[\xb2\x11\xb5nP\xb3<w\xa1\xd8\x11\x89\xee\x93\xb3j\xb7\xa6\x82\xaa&\x06<\xda\xbcd\x03\xff>\x8f\x92\x8bQ<\xe1\xa9.c\x1f+\xee?\xb3)\xfa\xe5\xf5V\xa7UY\xb0\xc5A\x7f\r\xa3\xaa\xf5\x0b\x80\x8e\xb5\x0e\xb3L\x0f\xfbB\xab\x16\xb1o8tl\xaf\xab\x15!\xef$\xcd\xbd\xbf\x8d\xbc\xca\x8a&\xf2\xe9\xe5\xa0\xcc\xb6e\xcc\xe7\x95\xc7B\xba#7\x91%#\x1c\x14\xedO\xd2aGn\x8d\x0e\x8e:!B\xd9Y\xa8\xb2z\xad\xa6\xe1\n\xb3\xa6\xd5\xd6\x9f\xe7vD\xcfY\x04\xbc\xd4\xfa\xc3\x98f\x9e\x87C\xfck\xd1+5\x96nM\xb3\xd09\x845\xa8\xd2\r/h\xcb\xe5\xa6\xc3x\xce\xcf\xec\xc4\xf9\x1f\xbf\xbc\xf2\xccb\xc9\xc6\xfd\x111\x98>\xeeK\xb0\xb9D\xa0q\\\xc4\xacji\xc9\xef\xb0\xbe\r\x91(\x8e_\xady*\xdc\xde\xa3\xa8\xd1\xec\xd0zh\x83.\x13C\xb4\xf4\xb4d\xceUd\x08k\xeech\xf2\x9e\xf8\xfe\xb7\xa57\xef \xd7\x11\xdc\x91'{\xc1\xe9\xda\x16\x95\xa4\xc4\xb0\x1dQ*\xfa\x8c\x9a\x83\xe6\x97\x83\x0eJ\x0f\xf1\x85w\xcb\xf9\x9dj\xd7\xe7J\xc7\xf0\x92?H\x1c\x81Y2\xed<\x9d+t\xea\xcb\xc3\x14\xfb\xec\xc3bH\x84\xd8i\xba8\x7fT\x83\xe3\x99\x02\x1f\x16\xa1\xaf\x9c\x1c"

Gateway decrypted response:
{"status":"success","id":[{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":2,"FanMode_a":2},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625ea5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2600,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":34,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625ea5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625ea5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Hallway Thermostat\",\"ShortID_d\":49791}","FirmwareVersion":"003A0027","ShortID_d":49791,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902626670"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2000,"LocalTemperature_x100":2450,"CoolingSetpoint_x100":2000,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902626670","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902626670","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Reading Thermostat\",\"ShortID_d\":17481}","FirmwareVersion":"00360023","ShortID_d":17481,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","endPoint_i":9,"OTAStatus_d":3},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"Debug_d":"+2000+2000302102002102402102001415C000G51886E2A71A46E2AG51886E2A71A46E2A","AutoCoolingSetpoint_x100":0,"CoolingFanDelay":0,"HoldType":2,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010000611100000007FFF0000000000"}},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090256d8f7"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1600,"LocalTemperature_x100":2650,"CoolingSetpoint_x100":1600,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090256d8f7","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090256d8f7","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Guestroom Thermostat\",\"ShortID_d\":538}","FirmwareVersion":"003A0027","ShortID_d":538,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"sFanS":{"FanMode":1,"FanMode_a":1},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625e0c"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1500,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1500,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":6,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":768,"UnquieID":"001e5e0902625e0c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625e0c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Office Thermostat\",\"ShortID_d\":4719}","FirmwareVersion":"003A0027","ShortID_d":4719,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":768,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":2400,"AutoHeatingSetpoint_x100":2100,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}},{"sScheS":{"CoolSchedule1":"020f","CoolSchedule2":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","CoolSchedule3":"02ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1},"sFanS":{"FanMode":0,"FanMode_a":0},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090262659c"},"sDiadS":{"LastMessageRSSI_d":-65},"status":"success","sTherS":{"CoolingSetpoint_x100_a":2100,"LocalTemperature_x100":2750,"CoolingSetpoint_x100":2100,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":0,"OperationMode":0,"RunningState":0,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e090262659c","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e090262659c","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Children Thermostat\",\"ShortID_d\":3715}","FirmwareVersion":"003A0027","ShortID_d":3715,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1,"DeviceSetting":"001030501001006032100030000000000800000010003011100000007FFF0000000000"}},{"sScheS":{"CoolSchedule1":"01010600240023002800ffffffffffffffffffffffffffffffffdd0600240023002800ffffffffffffffffffffffffffffffffffffffffffffffffffffffff","CoolSchedule3":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff","ScheduleEnable":1,"CoolSchedule2":"01ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffff"},"sFanS":{"FanMode":3,"FanMode_a":3},"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e0902625de5"},"status":"success","sTherS":{"CoolingSetpoint_x100_a":1300,"LocalTemperature_x100":2700,"CoolingSetpoint_x100":1300,"UnocCoolingSetpoint_x100":3000,"MinHeatSetpoint_x100":500,"HeatingSetpoint_x100":2100,"ACErrorCode_d":0,"HeatingSetpoint_x100_a":2100,"TempCalibration_x10":0,"ErrorTherSCompressor":0,"ErrorTherSTempSensor":0,"MaxCoolSetpoint_x100":4000,"UnocHeatingSetpoint_x100":1500,"MaxHeatSetpoint_x100":4000,"ErrorTherSOutdSensor":0,"Ocupancy":0,"MinCoolSetpoint_x100":500,"SystemMode":3,"SystemMode_a":3,"RunningMode":3,"OperationMode":0,"RunningState":66,"ErrorTherSOutdSensorShort":0,"ErrorTherSTempSensorShort":0,"ErrorInWallSwitchReleased":0},"DeviceL":{"DeviceType":100,"DeviceSubType":769,"UnquieID":"001e5e0902625de5","AttributeList":"000100100003001100330034000500080019001c001d001a00210022002a000b001b","ModelIdentifier_i":"FC600","ClusterIDList_i":"00000003000400050201020202040402fc04fc06fc09000a0019#","getModelIdentifierFlag_i":1,"DeviceEndpointNum_i":1},"sZDO":{"ProtocalType_i":2,"MACAddress":"001e5e0902625de5","LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Dining Thermostat\",\"ShortID_d\":4131}","FirmwareVersion":"003A0027","ShortID_d":4131,"LeaveNetwork":0,"JoinConfigVersion_i":"211018"},"sTherUIS":{"TemperatureDisplayMode":0,"LockKey":0},"sBasicS":{"ManufactureName":"SALUS","ModelIdentifier":"FC600","HardwareVersion":"2","ApplicationVersion_d":1,"StackVersion_d":87,"PowerSource":1},"sEndpt":{"DeviceType":769,"Endpoint_i":9},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/b478a944-6a14-4f20-9320-4854ce7b141d/FC600_003A0027.tar.gz","OTAFirmwareVersion_d":"003A0027","endPoint_i":9,"OTAStatus_d":0},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000787818","JoinConfigEnd":1},"sComm":{"TimeFormat24Hour":1,"CoolingFanDelay":0,"HoldType":2,"AutoCoolingSetpoint_x100":0,"AutoHeatingSetpoint_x100":0,"HoldType_a":2,"ShortCycleProtection":300},"sFanCoil":{"FanCoilType":0,"S1ComTerminals":0,"CompleteSetup":15,"HeatCoolSelection":1,"S2ComTerminals":0,"WindowIconEnable":1}}]}

Setting heating device 001e5e0902626670 fan_mode to low
Gateway request: POST http://192.168.254.232:80/deviceid/write
{"requestAttr": "write", "id": [{"data": {"DeviceType": 100, "Endpoint": 9, "UniID": "001e5e0902626670"}, "sFanS": {"FanMode": 1}}]}

Gateway encrypted request: POST http://192.168.254.232:80/deviceid/write
b"\xe5\xa1![\xf9mv\xe6\xff\xd2,q6\xf8\xae\x1b\xdfv\x8e\xf1zt\x84@\x18u\xe5!j\x7fD\x99V\xd8\xc8\xca\xfe\x9b\x8b9-r\xb2e\xa5\xcb\x85\x0f\xb4\x93\x11h[\xe2Oi\xca5i\x81\xe9\xfd\t*\x7f\x81\xc5\x9b\xbc\xf4\x9a\xfb\xb0\xd0$\xb8\x99\x02e\x88\xcao4{\xecT\x8e=\xa1\xa1n\xb8\x1d\xafxmT\xcf\xfe\xa1\xf5T\x12\x13I\x05{'\x14y\x1c\x13\xdd\xdd\xc2\xe3\x17{\xb6\nto\xb6\xfa\x95\xd2\xf4\x97@0\x9dWeT\x82\xfb\xafJ;\xfdb\xdd\x7f\xe8"

Gateway decrypted response:
{"status":"fail","id":[{"status":"fail","data":{"Endpoint":9,"Devicetype":100,"UniID":"001e5e0902626670\t"}}]}

write failed: {'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e0902626670'}, 'sFanS': {'FanMode': 1}}]}
Exception. <class 'pyit600.exceptions.IT600CommandError'> ("iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e0902626670'}, 'sFanS': {'FanMode': 1}}]}'",) / iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e0902626670'}, 'sFanS': {'FanMode': 1}}]}'
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/pyit600/gateway.py", line 943, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'Endpoint': 9, 'UniID': '001e5e0902626670'}, 'sFanS': {'FanMode': 1}}]}'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/config/test-salus.py", line 22, in <module>
    asyncio.run(go())
  File "/usr/local/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/usr/local/lib/python3.10/asyncio/base_events.py", line 646, in run_until_complete
    return future.result()
  File "/config/test-salus.py", line 20, in go
    await gateway.set_climate_device_fan_mode(climate_device_id, "Low")
  File "/usr/local/lib/python3.10/site-packages/pyit600/gateway.py", line 809, in set_climate_device_fan_mode
    await self._make_encrypted_request(
  File "/usr/local/lib/python3.10/site-packages/pyit600/gateway.py", line 960, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: Unknown error occurred while communicating with iT600 gateway
Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0xb58b3748>
Unclosed connector
connections: ['[(<aiohttp.client_proto.ResponseHandler object at 0xb58a2988>, 11537.496090802)]']
connector: <aiohttp.connector.TCPConnector object at 0xb58b3868>
```

The relevant error is the "iT600 gateway rejected 'write' command with content" message. Reading data appears to work perfectly fine. 

### Conversation

#### @efenex commented at 2022-10-18T07:49:52Z

A small patch to the library to output the response from the gateway itself gives me:

```
pyit600.exceptions.IT600CommandError: iT600 gateway rejected 'write' command with content '{'requestAttr': 'write', 'id': [{'data': {'DeviceType': 100, 'UniID': '001e5e0902626670', 'Endpoint': 9}, 'sFanS': {'FanMode': 1}}]}' and response '{'status': 'fail', 'id': [{'status': 'fail', 'data': {'Devicetype': 100, 'UniID': '001e5e0902626670\t', 'Endpoint': 9}}]}'
```

Does not provide any real relevant additional information, other than status "fail".

Is there any way to set debugging on the gateway or to figure out what is causing the failure on that end, besides trial & error?

---

## #31: Salus SQ610(WB) - Connecting to Smartthings - Device Handler Code needed

- URL: https://github.com/epoplavskis/pyit600/issues/31
- State: closed
- Author: @Coombes11
- Created: 2022-05-09T16:25:37Z
- Updated: 2022-05-10T16:28:07Z
- Labels: none

### Issue body

I am trying to connect a SQ610(WB) zigbee thermostat to my Smartthings hub (V2). It is connecting as a "Thing" and defaulting in the devices type. I want to create a device handler but dont know what the code is. Can anyone help?

### Conversation

#### @Coombes11 commented at 2022-05-10T16:28:05Z

i think i put this in the wrong place

---

## #30: Integration of pyit600 to fhem is also available

- URL: https://github.com/epoplavskis/pyit600/issues/30
- State: closed
- Author: @staeblvo
- Created: 2022-02-02T15:42:38Z
- Updated: 2022-02-05T21:28:08Z
- Labels: none

### Issue body

Hi jvitkauskas,
there is also a integration of your package to fhem available by the module fhempy from dominikkarall: https://github.com/dominikkarall/fhempy.
Currently there is implementation for climate devices (tested with device VS20WRF) available.
https://github.com/dominikkarall/fhempy/blob/master/FHEM/bindings/python/fhempy/lib/pyit600/README.md

Maybe you want add this info also to your README.md.

BR
Volker 


### Conversation

#### @jvitkauskas commented at 2022-02-05T21:28:08Z

Ok, added this to readme.

---

## #28: Support for AWRT10RT thermostat, wiring center 

- URL: https://github.com/epoplavskis/pyit600/issues/28
- State: open
- Author: @rmsppu
- Created: 2021-11-28T20:00:02Z
- Updated: 2021-11-28T20:03:47Z
- Labels: none

### Issue body

I've got a Salus UG600 gateway that's paired via zigbee with 3 Salus [AWRT10RT thermostats](https://shop.salusinc.com/pages/salus-awrt10rf-wireless-radiant-thermostat?_pos=1&_sid=ea33a9b56&_ss=r) and one [AKL04PRF wireless pump relay controller](https://shop.salusinc.com/pages/salus-akl04prf-wireless-pump-relay-controller?_pos=5&_sid=afc66c1e0&_ss=r).

The gateway responds to queries from pyit600 but the reported devices aren't recognized.

Attached is the output of `main.py --host 192.168.1.69 --euid FFFFFFFFFFFFFFFF  --debug` (real EUID obfuscated).
[debug.txt](https://github.com/jvitkauskas/pyit600/files/7614266/debug.txt)



I've tried a quick and dirty modification to gateway.py to add the device "sIT600D" as model "AWRT10RF" -- that seems to work to recognize the thermostats, but the call to:

```
DEBUG:pyit600:Gateway request: POST http://192.168.1.69:80/deviceid/write
{"requestAttr": "write", "id": [{"data": {"UniID": "FFFFFFFFFFFFFFFF", "DeviceType": 100, "Endpoint": 9}, "sIT600D": {"SetHeatingSetpoint_x100": 2100}}]}
```

fails and produces:

```
DEBUG:pyit600:Gateway response:
{"status":"fail","id":[{"status":"fail","data":{"UniID":"FFFFFFFFFFFFFFFF\t","Devicetype":100,"Endpoint":9}}]}

```




### Conversation

#### @rmsppu commented at 2021-11-28T20:03:47Z

My end goal is to gain control of the Salus thermostats through Hubitat, meaning re-writing pyit600 in Groovy. I'd be very happy to start with a device handler for the Salus gateway and thermostats that works in Smartthings, if anyone knows of that.

---

## #27: Support for ecm600

- URL: https://github.com/epoplavskis/pyit600/issues/27
- State: open
- Author: @bse4792
- Created: 2021-11-14T21:32:54Z
- Updated: 2022-12-03T23:06:27Z
- Labels: none

### Issue body

Hi I have to show gratitude for your work in getting salus to ha

I have a ecm600 that measures the power usage via clamps on ingoing line.

Hoping you can include this into your portfolio.

Kindly bse4792 

### Conversation

#### @bse4792 commented at 2022-12-03T23:06:26Z

i run you script and filtered out what i think you need, if more is needed please ask


{"DeviceType":100,"DeviceSubType":9,"getModelIdentifierFlag_i":1,"UnquieID":"001e5e09021293d4","AttributeList":"00010010000300110033003400370005000700080006001b001600170018000b","ModelIdentifier_i":"ECM600","ClusterIDList_i":"000000010003001507020b05fc01fc02fc03000a0019#","DeviceEndpointNum_i":4},"sZDO":{"FirmwareVersion":"09160525","MACAddress":"001e5e09021293d4","ShortID_d":18824,"ProtocalType_i":2,"DeviceName":"{\"deviceName\":\"Strømmåler\",\"ShortID_d\":18824}","LeaveNetwork":0,"LeaveRequest_d":0,"JoinConfigVersion_i":"220119"},"sGenSche":{"UpdateGenScheStatus":0},"sBasicS":{"ManufactureName":"Computime Inc","ApplicationVersion_d":22,"ModelIdentifier":"ECM600","PowerSource":3,"HardwareVersion":"191"},"sEndpt":{"DeviceType":9,"Endpoint_i":1},"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000089491","ConfigureReportResponse":"0702010000000000000004","JoinConfigEnd":1,"AppData_c":"{\"ClampsUsed\":[{\"clamp\":1,\"name\":\"3 faset strøm ind\",\"phase\":3},{\"clamp\":2,\"name\":\"clamp2\",\"phase\":3},{\"clamp\":3,\"name\":\"clamp3\",\"phase\":3},{\"clamp\":4,\"name\":\"clamp4\",\"phase\":0}]}"},"sPowerS":{"BatteryVoltage_x10":51,"BatteryVolThreshold_x10_d":40,"BatteryVolThreshold3_x10_d":52,"BatteryVolThreshold2_x10_d":46,"ErrorPowerSLowBattery":0,"ErrorBatteryAlarmState_d":0,"BatteryAlarmMask_d":0,"BatteryVolThreshold1_x10_d":42,"BatteryRemaining":200,"MainsVoltage_x10":2200},"sMeterS":{"Multiplier":1,"Divisor":10000}},{"data":{"DeviceType":100,"Endpoint":9,"UniID":"001e5e090219b57d"},"sOTA":{"OTAStatus_d":0},"DeviceL":

---

## #26: SQ610 works!

- URL: https://github.com/epoplavskis/pyit600/issues/26
- State: closed
- Author: @mobopx
- Created: 2021-10-01T06:09:19Z
- Updated: 2022-01-14T20:33:00Z
- Labels: none

### Issue body

Salus SQ610 works but on version 0.2.6. Up to version 0.3.0 at all, the HA did not detect devices, neither the SQ610, nor the SQ610RF, nor the VS20WRF.
![image](https://user-images.githubusercontent.com/79940882/135573844-95c29f5d-9bc6-4381-9375-7c17648039a3.png)


### Conversation

#### @jvitkauskas commented at 2021-10-01T19:04:53Z

Can you please try version 0.3.1?

#### @mobopx commented at 2021-10-03T07:43:10Z

0.3.1
SQ610 works
VS20WRF works
SQ610RF - i can test on teusday

how to read the humidity entity from SQ610 in HA?

#### @jvitkauskas commented at 2021-10-06T20:04:01Z

@mobopx try this https://github.com/jvitkauskas/homeassistant_salus/issues/9#issuecomment-770362764

---

## #25: EUID seems invalid

- URL: https://github.com/epoplavskis/pyit600/issues/25
- State: closed
- Author: @pboca
- Created: 2021-09-30T22:10:13Z
- Updated: 2022-02-05T21:09:32Z
- Labels: none

### Issue body

Hello!
Have you had any issues using the EUID on the gateway?
I get an error immediately after it tries to connect and enumerate all devices. It wont succeed with readall request even if I tried all the possible combinations.

### Conversation

#### @pboca commented at 2021-09-30T22:12:33Z

Also I checked everything, including Disable Local Wifi Mode set to No and also reviewed the code to see what it does.

#### @pekarsky commented at 2021-10-06T19:38:47Z

@pboca @jvitkauskas 
having this (euid and address was checked a dozen times)
bash-5.1# ./main.py --host 192.168.100.185 --euid 001E5E0902621653 --debug
DEBUG:pyit600:Trying to connect to gateway at 192.168.100.185
DEBUG:pyit600:Gateway request: POST http://192.168.100.185:80/deviceid/read
{"requestAttr": "readall"}

ERROR:pyit600:Timeout while connecting to gateway: 
Authentication error: check if you have specified gateway's EUID correctly.


tcpdump in different session:
21:32:47.295717 IP 192.168.100.50.51894 > 192.168.100.185.80: tcp 0
E..<..@.@.....d2..d....P.6..........Jk.........
............
21:32:47.296145 IP 192.168.100.185.80 > 192.168.100.50.51894: tcp 0
E..<..@.@.....d...d2.P.....9.6......s..........
............
21:32:47.296232 IP 192.168.100.50.51894 > 192.168.100.185.80: tcp 0
E..4..@.@.....d2..d....P.6.....:....Jc.....
........
21:32:47.296909 IP 192.168.100.50.51894 > 192.168.100.185.80: tcp 196
E.....@.@.....d2..d....P.6.....:....K'.....
........POST /deviceid/read HTTP/1.1
Host: 192.168.100.185
content-type: application/json
Accept: */*
Accept-Encoding: gzip, deflate
User-Agent: Python/3.9 aiohttp/3.7.4.post0
Content-Length: 32


21:32:47.297064 IP 192.168.100.50.51894 > 192.168.100.185.80: tcp 32
E..T..@.@.....d2..d....P.6.....:....J......
............k).t..IB.....+Y...y........{
21:32:47.297265 IP 192.168.100.185.80 > 192.168.100.50.51894: tcp 0
E..46.@.@.....d...d2.P.....:.6.............
........
21:32:47.297337 IP 192.168.100.185.80 > 192.168.100.50.51894: tcp 0
E..46.@.@.....d...d2.P.....:.6.............
........
21:32:52.298965 IP 192.168.100.50.51894 > 192.168.100.185.80: tcp 0
E..4..@.@.....d2..d....P.6.....:....Jc.....
........
21:32:52.299233 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..<..@.@.dk..d2..d....P.:x.........Jk.........
............
21:32:52.299624 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 0
E..<..@.@.....d...d2.P.....9.:x................
............
21:32:52.299724 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.dr..d2..d....P.:x....:....Jc.....
........
21:32:52.300325 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 130
E.....@.@.c...d2..d....P.:x....:....J......
........GET / HTTP/1.1
Host: 192.168.100.185
Accept: */*
Accept-Encoding: gzip, deflate
User-Agent: Python/3.9 aiohttp/3.7.4.post0


21:32:52.300692 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 0
E..4..@.@.....d...d2.P.....:.:y.....$%.....
........
21:32:52.336468 IP 192.168.100.185.80 > 192.168.100.50.51894: tcp 0
E..46.@.@.....d...d2.P.....:.6.......(.....
........
21:32:52.359339 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 350
E.....@.@.....d...d2.P.....:.:y............
........HTTP/1.1 200 OK
Keep-Alive: timeout=30, max=199
X-Frame-Options: SAMEORIGIN
Content-Type: text/html
X-Content-Type-Options: nosniff
Date: Wed, 06 Oct 2021 19:32:51 GMT
ETag: "48-3584-606fcaf4"
Content-Length: 13700
X-XSS-Protection: 1; mode=block
Last-Modified: Fri, 09 Apr 2021 03:33:08 GMT
Connection: Keep-Alive
Accept-Ranges: bytes


21:32:52.359422 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.dp..d2..d....P.:y.........Jc.....
........
21:32:52.359511 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 1448
E.....@.@..P..d...d2.P.......:y......~.....
........<html>

  <head>
    <!--
    <meta http-equiv="cache-control" content="max-age=0" />
    <meta http-equiv="cache-control" content="no-cache" />
    <meta http-equiv="expires" content="0" />
    <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
    <meta http-equiv="pragma" content="no-cache" />-->
    <title>AppwebTest</title>
    <script src="js/jquery.js"></script>

    <script type="text/javascript">

      window.onload = function() {
      if(!window.location.hash) {
      window.location = window.location + '#loaded';
      window.location.reload();
      }
      }
      var all_data_buf = new Object();
      if (typeof JSON == 'undefined') {
        $('head').append($("<script type='text/javascript' src='json2.js'>"));
          }


        $(function(){

        //var itv = setInterval("devInfoGetting()", 5000);
        devInfogetting();
        //alert($("#device_id_select option:selected").val());
        //var obj = $("#device_id_select option:selected");
        //changeSelectID(obj);

        var itv = setInterval("web_readFromDevice()", 1000);


        });

        var content_table = new Array();
        content_table = [{"name":"Gateway", "input_type":"text", "ele_attr":["SetLedState","SetRebootGateway","SetTimeZone","SetFactoryReset_d"]},
        {"name":"ZDO", "input_type":"text", "ele_attr":["SetLeaveNetwork_d","SetRefresh_d"]},
        {"name":"Coord", "input_type":"text", "ele_attr":
21:32:52.359554 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.do..d2..d....P.:y...#@....Jc.....
........
21:32:52.359629 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 1448
E.....@.@..O..d...d2.P....#@.:y.....]......
........["SetPermitJoinPeriod","SetReadLocalTime_d","SetChannel_d","SetZigbeeCommand_d","SetRebootCoordinator_d","SetLocalTime_i","SetUTCTime_i"]},
        {"name":"BasicS", "input_type":"text", "ele_attr":["SetSubDeviceEnable_d"]},
        {"name":"MeterS", "input_type":"text", "ele_attr":["ResetSummationDelivered","SetRequestFastPollPeriod","SetRequestFastPollDuration"]},
        {"name":"PowerS", "input_type":"text", "ele_attr":["SetVoltage_x10"]},
        {"name":"IdentifS", "input_type":"text", "ele_attr":["SetIndicator","SetReadIdentifyTime_d"]},
        {"name":"OnOffS", "input_type":"text", "ele_attr":["SetOnOff"]},

        ];

        var content_from_table = new Array();
        content_from_table = [{"name":"Gateway", "input_type":"text", "ele_attr":["SoftwareVersion","HardwareVersion","Network_WiFiMAC","Network_WiFiIP","Network_LANMAC","Network_LANIP","NetworkWifiConnectRouterSSID","NetworkWifiConnectRouterPassword","TimeZone","DSTStart","DSTEnd","DSTShift","KeyState", "LANConnected_d","WiFiConnected_d"]},
        {"name":"ZDO", "input_type":"text", "ele_attr":["ProtocalType","FirmwareVersion","MACAddress","ShortID_d","BindTable_d","FastModeConfig_d","IsFastMode_d"]},
        {"name":"Coord", "input_type":"text", "ele_attr":["LocalTime_d", "PANID_d","Channel_d","Form_d","ReceiveZigbeeCommand_d","CoordinatorUARTError"]},
        {"name":"BasicS", "input_type":"text", "ele_attr":["ManufactureName","ModelIdentifier","Appli
21:32:52.359670 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.dn..d2..d....P.:y...(.....Jc.....
........
21:32:52.359888 IP 192.168.100.185.80 > 192.168.100.50.51898: tcp 1200
E.....@.@..F..d...d2.P....(..:y............
........cationVersion_d","StackVersion_d","SubDeviceName_c","DeviceType","Endpoint_d","PowerSource_d","SubDeviceEnable_d"]},
        {"name":"MeterS", "input_type":"text", "ele_attr":[ "CurrentSummationDelivered","Multiplier","Divisor","ErrorMeterSLeakDetect","ErrorStatus_d","DemandDelivered_x10k","DefaultUpdatePeriod","FastPollUpdatePeriod","FastPollEndTime","ACPhase"]},
        {"name":"PowerS", "input_type":"text", "ele_attr":[ "Voltage_x10","BatteryVoltage_x10","ErrorPowerSLowBattery","ErrorBatteryAlarmState_d","BatteryVoltageThreshold_d","BatteryVoltageThreshold1_d","BatteryVoltageThreshold2_d","BatteryVoltageThreshold3_d","BatteryAlarmMask_d"]},
        {"name":"IdentifS", "input_type":"text", "ele_attr":[ "IdentifyTime_d"]},
        {"name":"OnOffs", "input_type":"text", "ele_attr":[ "OnOff"]},
        {"name":"Product", "input_type":"text", "ele_attr":[ "Mode", "Model"]},

        ];
        //-------------------------------------------------------------------------------------------------------------


        function initDevInfo(){
        $("#web_write_data").empty();
        //alert($("#device_id_select option:selected").val());
        //alert(all_data_buf.id[obj.value][conte
21:32:52.359933 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.dm..d2..d....P.:y...-.....Jc.....
........
21:32:52.360493 IP 192.168.100.50.51898 > 192.168.100.185.80: tcp 0
E..4..@.@.dl..d2..d....P.:y...-.....Jc.....
........
^C
56 packets captured
56 packets received by filter
0 packets dropped by kernel


#### @jvitkauskas commented at 2021-10-06T20:01:16Z

@pboca @pekarsky can you see a (broken) webpage when you go to the gateways IP address using your web browser?

#### @pekarsky commented at 2021-10-06T20:15:05Z

@jvitkauskas 
yes. 
I can see empty drop-down list
and "Refresh ID List" button below

Page title is "Appweb Test"

#### @pekarsky commented at 2021-10-08T12:04:10Z

@jvitkauskas 
ok, so what I've did now:
I've added 
`                with open("salus_req_body.bin", "wb") as f:
                    f.write(self._encryptor.encrypt(request_body_json))`
to gateway.py, So I wrote encrypted body to a file.
Than I've created a POST call in Postman to URL: http://192.168.100.185:80/deviceid/read 
with binary body prom a previous step.
And I've got this:
`<!DOCTYPE html>

<head>
	<title>Request Timeout</title>
	<link rel="shortcut icon" href="data:image/x-icon;," type="image/x-icon">
</head>

<body>
	<h2>Access Error: 408 -- Request Timeout</h2>
	<pre>Exceeded inactivity timeout of 30 sec</pre>
</body>

</html>`

Any ideas?


#### @Ashden commented at 2021-10-17T14:09:49Z

Hello,

I can confirm, the same thing happens to me. Using a Salus UGE600, I have the same error as the others:
```ERROR:pyit600:Timeout while connecting to gateway:```
```Authentication error: check if you have specified gateway's EUID correctly.```

#### @rgrabowski commented at 2021-10-17T18:32:51Z

Hi, I have the same issue too.

#### @zylxpl commented at 2021-10-20T12:47:22Z

Have the same problem. Also when try connect using Smart Home app lan option, but it miraculously connect when i log in and out of online account.

#### @mindvisionro commented at 2021-10-20T13:41:48Z

what firmware version do you have? what do you see when you access the gateway ip locally from a web browser? 

#### @mindvisionro commented at 2021-10-20T13:51:29Z

also what connection do you use? wifi or cable?
what type of ip did you set? static or dynamic?
What is the state of Local Wifi?

Another weird thing I've noticed is that authentication doesn't work when you open a browser window with the local gateway address or use the web interface ("Too many connections"). 

#### @zylxpl commented at 2021-10-20T14:06:55Z

@mindvisionro 
software version: 020143210405
coordinator version: 20210317
 When access from web browser i can see empty drop down menu and "Refresh ID list" button. Disable local WiFi mode is set to no. I tested on both, wifi and cable, same result. Gateway gets it ip from DHCP server, (static dhcp lease configured on server).

If you need any more info i will be happy to help. 


#### @mindvisionro commented at 2021-10-20T14:16:12Z

You have the same firmware and software version with me, so the problem is somewhere else. 
How is the network connection mode set? Auto or Hot spot, also the gateway is in the same vlan as Home assistant? 
Sorry if the questions sound silly but I'm trying to get step by step.

#### @zylxpl commented at 2021-10-20T14:22:47Z

Network connection mode is set to Auto. Gateway is in different vlan as HA, but for test proposes i also tried without vlan.
There is always a chance i missed something silly, so nothing for you to be sorry for :)

#### @mindvisionro commented at 2021-10-20T14:54:41Z

I tend to think it's a network issue or even how the token is written.

Is the gateway on the same ip class as HA? Ex: HA: 192.168.1.100, Gateway: 192.168.1.106

Does the token have 16 digits? sure you didn't mess 0(zero) with o ? :) 

#### @pekarsky commented at 2021-10-20T16:08:28Z

@mindvisionro 

Software version: 020143210405
Coordinator version: 20210317

That's what I took from Salus Internet application: 
device: {product_name: "home-uge600", model: "AY001MRT1", dsn: ".........", oem_model: "sau2ag1",…}
connected_at: "2021-10-20T09:32:05Z"
connection_status: "Online"
dealer: null
device_type: "Gateway"
dsn: "......."
gateway_type: "Generic"
has_properties: true
hwsig: "MAC-.........."
key: ........
lan_enabled: false
lan_ip: "192.168.100.111"
mac: "........."
manuf_model: "SalusZigbee1"
model: "AY001MRT1"
oem_model: "sau2ag1"
product_class: null
product_name: "home-uge600"
**sw_version: "devd 1.4.2-eng 2021-04-09 11:29:06 root/"**
template_id: 210
unique_hardware_id: null
(some sensitive data is substituted with dots)

I've tried both LAN and Wifi - always DHCP (can try static IP)
As for token - yes, I am absolutely sure - Salus integration does not accept in wrong format, checked a dozen times - 16 hex digits

Gateway and HA are in the same net 192.168.100.0/24

Disable local wifi set to no

#### @mindvisionro commented at 2021-10-20T17:23:22Z

the only thing different from what I use is only the static ip part, otherwise I have the same software and firmware versions.

And i use the last version of integration 0.31

what you could try is to manually install the component in config / python_scripts / pyit600


I will try tonight to make a new installation, so maybe we can find the problem, because the current integration has been going well for a long time

#### @mindvisionro commented at 2021-10-20T20:21:08Z

ok, i did a test and here's how it worked for me: 

1. I installed the Salus component from HACS 
2. In the python_scripts folder I copied the pyit600 folder (https://github.com/jvitkauskas/pyit600/tree/master/pyit600)  
3. HA restart 
4. Go to Configuration -> Integration -> Add integration -> search Salus -> enter your gateway ip & token 
5. Done

My Home Assistant is on a RPI4



#### @pekarsky commented at 2021-10-21T11:17:31Z

@mindvisionro I've even tried to clone this repository to my linux and execute main.py, which have to connect to UGE600 and just download device list and it failed.

Obviously, HA integration is not working too.
I can see network traffic on interface using tcpdump, but getting bad response, probably, because of bad request. I'll try to play around after my holidays - maybe region change will solve the issue


#### @mindvisionro commented at 2021-10-21T11:22:04Z

> 
> 
> @mindvisionro I've even tried to clone this repository to my linux and execute main.py, which have to connect to UGE600 and just download device list and it failed.
> 
> Obviously, HA integration is not working too. I can see network traffic on interface using tcpdump, but getting bad response, probably, because of bad request. I'll try to play around after my holidays - maybe region change will solve the issue

Yeah, I really don't know where the problem might be, what else I'd try, try resetting the gateway(factory reset) .

#### @zylxpl commented at 2021-10-22T18:25:55Z

ok, after 3 resets it started to work. Also, i need to put token using lower case only.

#### @mindvisionro commented at 2021-10-22T18:43:23Z

I'm glad to hear that

#### @loopez76 commented at 2021-11-02T20:59:43Z

same issue - even verified euid with salus - tried everything above - no success

#### @jvitkauskas commented at 2022-01-14T20:38:06Z

Some people mentioned that 0000000000000000 as euid might work https://github.com/jvitkauskas/homeassistant_salus/issues/20

#### @Ashden commented at 2022-01-25T20:34:18Z

I actually had the time now to check, and the EUID 0000000000000000 actually works!

---

## #21: Upstreaming into HA

- URL: https://github.com/epoplavskis/pyit600/issues/21
- State: closed
- Author: @ishioni
- Created: 2021-03-24T12:34:54Z
- Updated: 2022-12-05T14:20:44Z
- Labels: none

### Issue body

Hi

Will you consider upstreaming this into Home Assistant itself?

### Conversation

#### @jvitkauskas commented at 2021-04-04T16:39:04Z

Yes, I think it should be done. But I would like to get some code review done before. I am not a python developer by trade. If you want to help me with that you are more than welcome.

---

## #20: ITG500/IT500 request/investigation

- URL: https://github.com/epoplavskis/pyit600/issues/20
- State: closed
- Author: @hrford
- Created: 2021-02-11T22:03:38Z
- Updated: 2021-03-21T18:17:26Z
- Labels: none

### Issue body

Would like to help with support on ITG500 and the IT500 
Could I clarify if this device is not in scope for this project? If so, is there another project?
If this device is in scope, I have years of experience with Python, Linux, Bash, Network protocols.
Qutie happy to hack and play with WireShark to get network packets.
Otherwise I was going to write a python client for the naff web interface Salus provide.

### Conversation

#### @jvitkauskas commented at 2021-02-12T13:53:55Z

Took a quick look at iT500 app. It seems to be an entirely different system. So I don't see which code could be reused from iT600 integration. So it's probably better to create a separate library, unless I am wrong and there is some code which could be shared (I took only a quick look, did not analyze any protocols).

#### @jvitkauskas commented at 2021-02-12T21:13:01Z

Are you saying Salus provides a fully functional local web interface for controlling iT500 things locally? If that's the case, it's probably best to write client for that.

#### @hrford commented at 2021-02-13T14:05:16Z

Hey, 
There is a web interface for the IT500, but it goes to their servers, not to the gateway. 

The local gateway has visible UDP traffic, but I guess that also goes to their servers. 

If I was to write a Python client, it would have to emulate a browsing session.

I guess your project is not compatible with my plan as I'm assuming yours goes direct to the local gateway. Is that correct?

Thanks
-- 
Android, K-9 Mail.

On 12 February 2021 21:13:18 GMT, Julius Vitkauskas <notifications@github.com> wrote:
>Are you saying Salus provides a fully functional local web interface
>for controlling iT500 things locally? If that's the case, it's probably
>best to write client for that.
>
>-- 
>You are receiving this because you authored the thread.
>Reply to this email directly or view it on GitHub:
>https://github.com/jvitkauskas/pyit600/issues/20#issuecomment-778457933


#### @jvitkauskas commented at 2021-02-13T22:04:13Z

Yes, my project uses local communication and does not rely on the cloud. Despite that, I feel that request/response data would be different enough, so that barely any code (if any) could be reused (although, it is only my guess, I don't have any iT500 devices). I can help you with reverse engineering though. You can mail me.

---

## #16: request - Humidity and battery stats from sq610rf

- URL: https://github.com/epoplavskis/pyit600/issues/16
- State: open
- Author: @albei
- Created: 2020-12-19T21:41:37Z
- Updated: 2026-02-09T01:43:32Z
- Labels: none

### Issue body

@jvitkauskas Is it possible to get this two parameters?
Humidity and battery can be put to good use in home-assistant integration.
You did an awesome job with this client.
Thanks!

### Conversation

#### @albei commented at 2020-12-19T22:21:08Z

Continuing here with answers to your questions.
Yes it does.
The app shows humidity and battery status. 
Gonna try the client tomorrow and see what I get from thermostat.

#### @albei commented at 2020-12-20T07:41:56Z

From what I see from looking at app values during main.py run the humidity stat is  ""SunnySetpoint_x100": 53,".
Can't figure it out how it gets the battery.

```yaml
{
        "sBasicS": {
            "ModelIdentifier": "SQ610RF",
            "HardwareVersion": "2"
        },
        "sZDOInfo": {
            "GatewayNodeDSN_i": "ID",
            "OnlineStatus_i": 1,
            "JoinConfigEnd": 1
        },
        "data": {
            "DeviceType": 100,
            "Endpoint": 9,
            "UniID": "uniID"
        },
        "status": "success",
        "sOTA": {
            "OTAFirmwareURL_d": "http://eu.salusconnect.io/download/firmware/765e0085-18aa-409c-93ab-6970bc92315e/SQ610RF_0000001D.tar.gz",
            "endPoint_i": 9,
            "OTAStatus_d": 3
        },
        "DeviceL": {
            "DeviceSubType": 64,
            "DeviceType": 100,
            "AttributeList": "0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "UnquieID": "UniID",
            "DeviceEndpointNum_i": 1,
            "ModelIdentifier_i": "SQ610RF",
            "getModelIdentifierFlag_i": 1
        },
        "sZDO": {
            "ProtocalType_i": 1,
            "FirmwareVersion": "0000001D",
            "LeaveNetwork": 0,
            "MACAddress": "0000000000000000",
            "ShortID_d": 705,
            "DeviceName": "{\"deviceName\":\"TL\",\"ShortID_d\":705}",
            "LeaveRequest_d": 0,
            "JoinConfigVersion_i": "190629"
        },
        "sEndpt": {
            "DeviceType": 64,
            "Endpoint_i": 9
        },
        "sIT600D": {
            "DeviceIndex": 32,
            "SyncResponseVersion_d": "0000001D",
            "ConnectType_i": 1
        },
        "sIT600TH": {
            "Status_d": "716a0d0023600000012250210021000404013030303000005304ffffffffffffffffffffffff010003860005003500000104b0c8ab950200000000ffffffffffffffffffffffffffffffffff1c",
            "Error06": 0,
            "SystemMode_a": 4,
            "Error22": 0,
            "Error31": 0,
            "LockKey_a": 0,
            "SystemMode": 4,
            "ProgramOperationMode": 0,
            "Error01": 0,
            "OUTSensorType": 0,
            "Error24": 0,
            "Error02": 0,
            "Error03": 0,
            "Error07": 0,
            "AutoHeatingSetpoint_x100": 2100,
            "Error30": 0,
            "Error08": 0,
            "CloudySetpoint_x100": 0,
            "Error04": 0,
            "Error09": 0,
            "AutoCoolingSetpoint_x100_a": 2100,
            "Error21": 0,
            "Error23": 0,
            "Error25": 0,
            "Error32": 0,
            "AutoCoolingSetpoint_x100": 2100,
            "CoolingSetpoint_x100": 2250,
            "LocalTemperature_x100": 2360,
            "HeatingSetpoint_x100": 2250,
            "RunningMode": 4,
            "RunningState": 1,
            "LockKey": 0,
            "PairedWCNumber": 1,
            "SunnySetpoint_x100": 53,
            "HoldType": 0,
            "ScheduleType": 1,
            "MinCoolSetpoint_x100": 500,
            "TimeFormat24Hour": 1,
            "PairedTRVShortID": "FFFFFFFFFFFFFFFFFFFFFFFF",
            "MaxHeatSetpoint_x100_a": 3500,
            "HeatingControl": 1,
            "CoolingSetpoint_x100_a": 2250,
            "HeatingSetpoint_x100_a": 2250,
            "HoldType_a": 0,
            "AutoHeatingSetpoint_x100_a": 2100,
            "Status_2_d": "7242010000010500350000010001040027001000060035000500350005000100000001018001000083ef000000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "Schedule": "7242010000010500350000010001040027001000060035000500350005000100000001018001000083ef000000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "OUTSensorProbe": 0,
            "CoolingControl": 1,
            "MaxHeatSetpoint_x100": 3500,
            "MinHeatSetpoint_x100": 500,
            "MaxCoolSetpoint_x100": 3500,
            "MinCoolSetpoint_x100_a": 500,
            "TemperatureDisplayMode": 0
        },
        "sScheS": {
            "ScheduleEnable": 1,
            "HeatSchedule1": "770006002400120022501700240023002250ffff2100ffff2100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "HeatSchedule2": "77ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd",
            "HeatSchedule3": "77ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"
        },
        "sIT600I": {
            "CommandResponse_d": "42323000"
        }
    }

#### @albei commented at 2020-12-23T11:47:51Z

I made a small patch and I added the humidity. Works on my thermostat.

#### @ebeigarts commented at 2021-01-05T08:05:32Z

According to https://eu.salusconnect.io/js/consumer_370cc5e9767f0b172651a92febd9413a.js the battery level could be the character at 99 inside `Status_d`.

```
this.addBinding(null,".bb-battery-icon",{observe:"Status_d",onGet:function(e){var t,i=e?e.getProperty():null;return u.isString(i)?(t=parseInt(i[99]),u.isNumber(t)&&t>=0&&t<=5?t:null):null},update:function(e,t){var i={0:"critical",1:"critical",2:"low",3:"half",4:"most",5:"full"}
```

Example:

```
>> "716a0d0023600000012250210021000404013030303000005304ffffffffffffffffffffffff010003860005003500000104b0c8ab950200000000ffffffffffffffffffffffffffffffffff1c"[99]
"4"
```


#### @albei commented at 2021-01-05T08:30:44Z

Such a strange way they chose for battery status. With 20% steps can't be very usefull for battery sensor in hassio. :( but is still better then nothing.

#### @peterczarlarsen-ha commented at 2021-01-09T07:40:58Z

https://salus-controls.com/dk/hjaelp/

(I'm sorry its in danish, can't find a better version)... go down to "Fejlkode I display", unfold "Fejlkoder"

error 22 and 32 is "lavt batteri" ... low battery

#### @George-andrew commented at 2021-04-07T07:31:40Z

@albei @jvitkauskas 

Alarm battery information has error number 32 shows on the thermostat and SALUS app. 

If you need have any information about errors from UGE600, 
this is information has a boolean type, below descriptions of how it looks :


```
"sIT600TH":
"Error01": 1 - Thermostat paired TRV hardware issue
"Error02": 1 - Thermostat floor sensor overheating
"Error03": 1 - Thermostat floor sensor open
"Error04": 1 - Thermostat floor sensor short
"Error05": 1 - Thermostat lost link with ZigBee Coordinator
"Error06": 1 - Thermostat lost link with Wiring Center KL08RF
"Error07": 1 - Thermostat lost link with TRV
"Error08": 1 - Thermostat lost link with RX10RF (RX1)
"Error09": 1 - Thermostat lost link with RX10RF (RX2)
"Error21": 1 - Thermostat paired TRV lost link with Coordinator
"Error22": 1 - Thermostat paired TRV low battery
"Error23": 1 - Thermostat receive message form unpaired TRV or TRV receive a message from   unpaired Thermostat
"Error24": 1 - Thermostat reject by Wiring Centre
"Error25": 1 - Thermostat lost link with Parent
"Error30": 1 - Thermostat paired TRV gear issue
"Error31": 1 - Thermostat paired TRV adaptation issue
"Error32": 1 - Thermostat low battery

```




#### @horatiurus commented at 2022-10-12T10:17:19Z

> I made a small patch and I added the humidity. Works on my thermostat.

Could you be so kind and add some information about how you did that?
I would be nice to have this displayed in Home Assistant next to the already displayed information

#### @adynis commented at 2025-12-26T03:19:15Z

I found out today that HomeAssistant doesn't notify me about low battery on salus sq610rf because.... there's no battery info in HA.
Any solution here?

Thanks

#### @Gucioo commented at 2026-02-09T01:43:32Z

### Floor Sensor add reqest

Also             "**CloudySetpoint_x100**": 0, --> seems to contain External Temperature Sensor (Like Floor Sensor)
Tested with openHAB Salus Cloud integration for SQ610RF with  S1/S2 inputs set to Floor sensor and connected probe.

SunnySetpoint is humidity as on screen (0.00 to 1.00), 
also battery level (it goes from 0 to 5).

Can this feature be implemented to this addon and  to Home Assistant
<img width="1072" height="590" alt="Image" src="https://github.com/user-attachments/assets/34f3bf19-5bf0-456f-a4a8-064220e4dea8" />




---

## #15: OS600

- URL: https://github.com/epoplavskis/pyit600/issues/15
- State: closed
- Author: @peter4200
- Created: 2020-11-19T20:11:58Z
- Updated: 2020-12-30T20:18:31Z
- Labels: none

### Issue body

Dear developer 

It looks like the OS600 Windows Device are wrong. It appears as a temperature device and not as a binary switch

SensorDevice(available=True, name='Kontor, sensor', unique_id='xxxxxxxxxxxxxxxx', state='15.76', unit_of_measurement='°C', device_class='temperature', data={'DeviceType': 100, 'Endpoint': 1, 'UniID': '001e5e09021bf7c3'}, manufacturer='SALUS', model='OS600', sw_version='20160620')


### Conversation

#### @jvitkauskas commented at 2020-12-19T21:08:39Z

It seems like some devices have extra temperature measurement capability.

@peter4200 try now. I have updated https://github.com/jvitkauskas/homeassistant_salus

---

## #11: Support a new device SPE600

- URL: https://github.com/epoplavskis/pyit600/issues/11
- State: closed
- Author: @George-andrew
- Created: 2020-10-13T13:19:01Z
- Updated: 2020-12-30T20:18:27Z
- Labels: none

### Issue body

Dear Julius, 

Please add a new binary device binary (ON/OFF),  
Smart Plug  SPE600 has two working options.   

### Conversation

#### @jvitkauskas commented at 2020-10-16T20:46:15Z

Added support to this library. Will add support for home assistant in the upcoming days.

#### @George-andrew commented at 2020-12-07T07:25:05Z

@jvitkauskas it doesn't work in home assistant, seems not found in HA  

#### @jvitkauskas commented at 2020-12-19T21:07:11Z

@George-andrew try now. I have updated https://github.com/jvitkauskas/homeassistant_salus

---

## #7: FC600 users wanted

- URL: https://github.com/epoplavskis/pyit600/issues/7
- State: closed
- Author: @jvitkauskas
- Created: 2020-09-17T23:33:11Z
- Updated: 2021-10-06T20:06:09Z
- Labels: enhancement, help wanted

### Issue body

Salus FC600 Fan Coil thermostat it's probably not supported yet. I am looking for owners to provide logs and help me figure this out.

### Conversation

#### @George-andrew commented at 2021-02-16T14:21:23Z

Dear Julius,
Sorry for my confusion, 
Now there are correctly my logs from FC600 :  

I also noticed that the commands are different from IT600 regulators, but I did some test to understand how it works, and below the comment for this  

```
"SystemMode": , 
5 = Cooling mode,
4 = Heating mode. 

"HoldType" : ,
0 = Follow Schedule, 
1 = Schedule Override, 
2 = Permanent Hold, 
10 =ECO, 
7 = Off

"sFanS": {
         "FanMode": ,
5 = Auto mode, 
3 = Speed 3 High,
2 = Speed 2 Medium,
1 = Speed 1 Low,
0 = Off.
```

Thank you very much for your very hard work in creating this integration 

  
Log from FC600 : 
```
{
    "status": "success",
    "id": [
        {
            "DeviceL": {
                "ModelIdentifier_i": "SAU2AG1-ZC",
                "DeviceType": 200,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "000100040003001100050008000b00100033",
                "DeviceSubType": 0,
                "DeviceEndpointNum_i": 1,
                "UnquieID": "0000000000000000"
            },
            "data": {
                "DeviceType": 200,
                "Endpoint": 0,
                "UniID": "0000000000000000"
            },
            "sEndpt": {
                "DeviceType": 0,
                "Endpoint_i": 0
            },
            "sZDO": {
                "DeviceName": "{\"deviceName\":\"SALUS HA\",\"ShortID_d\":0}",
                "LeaveNetwork": 0,
                "ProtocalType_i": 2,
                "FirmwareVersion": "20200115",
                "MACAddress": "001e5e0902149a96",
                "ShortID_d": 0,
                "LeaveRequest_d": 0
            },
            "sCoord": {
                "TimeFormat24Hour": 1,
                "PANID_d": 29486,
                "Channel_d": 15,
                "IdentifyInProgress_i": 0,
                "Form_d": 1,
                "ErrorCoordUART": 0,
                "PermitJoinState_d": 0,
                "PermitJoinTime_i": 0,
                "ReceiveZigbeeCommand_d": "7c0f5304fc9b270900087e03800098"
            },
            "sBasicS": {
                "ModelIdentifier": "SAU2AG1-ZC",
                "HardwareVersion": "197"
            },
            "sZDOInfo": {
                "OnlineStatus_i": 1,
                "GatewayNodeDSN_i": "VR00ZN000561360"
            }
        },
        {
            "data": {
                "DeviceType": 300,
                "Endpoint": 0,
                "UniID": "0000000000000000"
            },
            "sDebug": {
                "LocalDebugMsg_d": "net down:1,add fail:0,update fail:0,node status fail:0,prop nak:0,confirm_status_fail:0,status_partial_success:0,err_conn:0,err_app:0,err_unkwn:0,dests_ads:0,dests_lan:0",
                "AylaHeartBeatFrequency": 0,
                "OtherDebugMsg_d": "del device euid:001e5e090223649d, shortid: 0x0357, debug_code:3"
            },
            "DeviceL": {
                "ModelIdentifier_i": "SAU2AG1-GW",
                "DeviceType": 300,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "00010002000b000c001e00310033",
                "DeviceSubType": 0,
                "DeviceEndpointNum_i": 1,
                "UnquieID": "0000000000000000"
            },
            "sGateway": {
                "GatewaySoftwareVersion": "020141201211",
                "NetworkWiFiMAC": "00:1e:5e:01:66:3a",
                "LEDMode": 1,
                "NetworkWiFiIP": "",
                "NetworkLANMAC": "00:1e:5e:01:66:3b",
                "NetworkLANIP": "192.168.1.13",
                "KeyState_i": 0,
                "NetworkSSID": "fdb783604bdf1a2e4d6a78802c91ab7b",
                "ModelIdentifier": "UGE600",
                "NetworkPassword": "fdb783604bdf1a2e4d6a78802c91ab7b",
                "NetworkLANSubnet": "255.255.255.0",
                "NetworkSecDNS": "8.8.8.8",
                "LANConnected_d": 1,
                "IsRtcRight_i": 1,
                "DisableLocalMode": 0,
                "LocalModeAccessCode": "2ca44efc0c3316b53e65c02b8307f5093e49f27a99073224599c206bd24bcc94",
                "WiFiConnected_d": 0,
                "NetworkPriDNS": "192.168.1.1",
                "IsSdCardNormal_i": 0,
                "TimeZone": "Europe/Amsterdam",
                "AylaConnected_i": 1,
                "NetworkLANRouterAddr": "192.168.1.1",
                "PhoneLocation": "",
                "WiFiMode": 0,
                "DeviceTimeZone_i": 3600,
                "EnableNetworkReset": 0,
                "GatewayHardwareVersion": "197",
                "DSTEnable_i": 1,
                "TimeOffset_i": 0,
                "WirelessAPpassword": "9c3cb00e4683b5986e8579bb4943c290",
                "NetworkLANMode": 1,
                "TimeStatus_i": 2
            },
            "sAWSIoT": {
                "CertARN": "   ",
                "CertsStatus": 0
            },
            "status": "success",
            "Product": {
                "Mode": 1,
                "Model": "SAL2BG1"
            },
            "sAyla_i": {
                "aylaConfigStatus": 1,
                "aylaNetWorkStatus": 1,
                "aylaDeviceID": "AC000W000616783",
                "aylaSetUTCTimeStatus": 1,
                "aylaTimeConfig": "0,1,60,1616893200",
                "aylaGateWayDsn": "VR00ZN000561360"
            }
        },
        {
            "sTherUIS": {
                "TemperatureDisplayMode": 0,
                "LockKey": 0
            },
            "DeviceL": {
                "ModelIdentifier_i": "FC600",
                "ClusterIDList_i": "00000003000400050201020202040402fc04fc06fc09000a0019#",
                "DeviceType": 100,
                "DeviceSubType": 769,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "00010010000300110033000500080019001c001d001a00210022002a000b",
                "DeviceEndpointNum_i": 1,
                "UnquieID": "001e5e090223649d"
            },
            "data": {
                "DeviceType": 100,
                "Endpoint": 9,
                "UniID": "001e5e090223649d"
            },
            "sFanS": {
                "FanMode": 5,
                "FanMode_a": 5
            },
            "sZDO": {
                "ProtocalType_i": 2,
                "DeviceName": "{\"deviceName\":\"FC600 HA\",\"ShortID_d\":10139}",
                "LeaveNetwork": 0,
                "MACAddress": "001e5e090223649d",
                "ShortID_d": 10139,
                "LeaveRequest_d": 0,
                "FirmwareVersion": "00350022",
                "JoinConfigVersion_i": "160426"
            },
            "sEndpt": {
                "DeviceType": 769,
                "Endpoint_i": 9
            },
            "sBasicS": {
                "ModelIdentifier": "FC600",
                "ManufactureName": "SALUS",
                "ApplicationVersion_d": 1,
                "StackVersion_d": 87,
                "PowerSource": 1,
                "HardwareVersion": "2"
            },
            "sComm": {
                "HoldType": 7,
                "Debug_d": "+2000+200020080?002102402102400101D000G3283BE274291BE27G3283BE274291BE27",
                "TimeFormat24Hour": 1,
                "AutoCoolingSetpoint_x100": 2400,
                "CoolingFanDelay": 0,
                "AutoHeatingSetpoint_x100": 2100,
                "HoldType_a": 7,
                "ShortCycleProtection": 300
            },
            "sZDOInfo": {
                "JoinConfigEnd": 1,
                "OnlineStatus_i": 1,
                "ConfigureReportResponse": "0204090000000000000100",
                "GatewayNodeDSN_i": "VR00ZN000561360"
            },
            "sFanCoil": {
                "DeviceSetting": "001030501001006032100030000000000800000010000611100000007FFF0000000000",
                "CompleteSetup": 15,
                "FanCoilType": 0,
                "S1ComTerminals": 0,
                "WindowIconEnable": 1,
                "HeatCoolSelection": 0,
                "S2ComTerminals": 0
            },
            "sTherS": {
                "CoolingSetpoint_x100_a": 2400,
                "LocalTemperature_x100": 2400,
                "RunningMode": 0,
                "CoolingSetpoint_x100": 2400,
                "TempCalibration_x10": 0,
                "HeatingSetpoint_x100": 800,
                "ErrorTherSTempSensorShort": 0,
                "Ocupancy": 0,
                "HeatingSetpoint_x100_a": 800,
                "SystemMode": 4,
                "OperationMode": 0,
                "MinCoolSetpoint_x100": 500,
                "MinHeatSetpoint_x100": 500,
                "MaxCoolSetpoint_x100": 4000,
                "MaxHeatSetpoint_x100": 4000,
                "RunningState": 0,
                "SystemMode_a": 4,
                "UnocCoolingSetpoint_x100": 3000,
                "ErrorTherSCompressor": 0,
                "ACErrorCode_d": 0,
                "ErrorInWallSwitchReleased": 0,
                "ErrorTherSOutdSensorShort": 0,
                "ErrorTherSOutdSensor": 0,
                "ErrorTherSTempSensor": 0,
                "UnocHeatingSetpoint_x100": 1500
            },
            "sScheS": {
                "ScheduleEnable": 0
            }
        }
    ]
}

DEBUG:pyit600:Gateway response: {
    "status": "success",
    "id": [
        {
            "DeviceL": {
                "ModelIdentifier_i": "SAU2AG1-ZC",
                "DeviceType": 200,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "000100040003001100050008000b00100033",
                "DeviceSubType": 0,
                "DeviceEndpointNum_i": 1,
                "UnquieID": "0000000000000000"
            },
            "data": {
                "DeviceType": 200,
                "Endpoint": 0,
                "UniID": "0000000000000000"
            },
            "sEndpt": {
                "DeviceType": 0,
                "Endpoint_i": 0
            },
            "sZDO": {
                "DeviceName": "{\"deviceName\":\"SALUS HA\",\"ShortID_d\":0}",
                "LeaveNetwork": 0,
                "ProtocalType_i": 2,
                "FirmwareVersion": "20200115",
                "MACAddress": "001e5e0902149a96",
                "ShortID_d": 0,
                "LeaveRequest_d": 0
            },
            "sCoord": {
                "TimeFormat24Hour": 1,
                "PANID_d": 29486,
                "Channel_d": 15,
                "IdentifyInProgress_i": 0,
                "Form_d": 1,
                "ErrorCoordUART": 0,
                "PermitJoinState_d": 0,
                "PermitJoinTime_i": 0,
                "ReceiveZigbeeCommand_d": "7c0f5304fc9b270900087e03800098"
            },
            "sBasicS": {
                "ModelIdentifier": "SAU2AG1-ZC",
                "HardwareVersion": "197"
            },
            "sZDOInfo": {
                "OnlineStatus_i": 1,
                "GatewayNodeDSN_i": "VR00ZN000561360"
            }
        },
        {
            "data": {
                "DeviceType": 300,
                "Endpoint": 0,
                "UniID": "0000000000000000"
            },
            "sDebug": {
                "LocalDebugMsg_d": "net down:1,add fail:0,update fail:0,node status fail:0,prop nak:0,confirm_status_fail:0,status_partial_success:0,err_conn:0,err_app:0,err_unkwn:0,dests_ads:0,dests_lan:0",
                "AylaHeartBeatFrequency": 0,
                "OtherDebugMsg_d": "del device euid:001e5e090223649d, shortid: 0x0357, debug_code:3"
            },
            "DeviceL": {
                "ModelIdentifier_i": "SAU2AG1-GW",
                "DeviceType": 300,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "00010002000b000c001e00310033",
                "DeviceSubType": 0,
                "DeviceEndpointNum_i": 1,
                "UnquieID": "0000000000000000"
            },
            "sGateway": {
                "GatewaySoftwareVersion": "020141201211",
                "NetworkWiFiMAC": "00:1e:5e:01:66:3a",
                "LEDMode": 1,
                "NetworkWiFiIP": "",
                "NetworkLANMAC": "00:1e:5e:01:66:3b",
                "NetworkLANIP": "192.168.1.13",
                "KeyState_i": 0,
                "NetworkSSID": "fdb783604bdf1a2e4d6a78802c91ab7b",
                "ModelIdentifier": "UGE600",
                "NetworkPassword": "fdb783604bdf1a2e4d6a78802c91ab7b",
                "NetworkLANSubnet": "255.255.255.0",
                "NetworkSecDNS": "8.8.8.8",
                "LANConnected_d": 1,
                "IsRtcRight_i": 1,
                "DisableLocalMode": 0,
                "LocalModeAccessCode": "2ca44efc0c3316b53e65c02b8307f5093e49f27a99073224599c206bd24bcc94",
                "WiFiConnected_d": 0,
                "NetworkPriDNS": "192.168.1.1",
                "IsSdCardNormal_i": 0,
                "TimeZone": "Europe/Amsterdam",
                "AylaConnected_i": 1,
                "NetworkLANRouterAddr": "192.168.1.1",
                "PhoneLocation": "",
                "WiFiMode": 0,
                "DeviceTimeZone_i": 3600,
                "EnableNetworkReset": 0,
                "GatewayHardwareVersion": "197",
                "DSTEnable_i": 1,
                "TimeOffset_i": 0,
                "WirelessAPpassword": "9c3cb00e4683b5986e8579bb4943c290",
                "NetworkLANMode": 1,
                "TimeStatus_i": 2
            },
            "sAWSIoT": {
                "CertARN": "   ",
                "CertsStatus": 0
            },
            "status": "success",
            "Product": {
                "Mode": 1,
                "Model": "SAL2BG1"
            },
            "sAyla_i": {
                "aylaConfigStatus": 1,
                "aylaNetWorkStatus": 1,
                "aylaDeviceID": "AC000W000616783",
                "aylaSetUTCTimeStatus": 1,
                "aylaTimeConfig": "0,1,60,1616893200",
                "aylaGateWayDsn": "VR00ZN000561360"
            }
        },
        {
            "sTherUIS": {
                "TemperatureDisplayMode": 0,
                "LockKey": 0
            },
            "DeviceL": {
                "ModelIdentifier_i": "FC600",
                "ClusterIDList_i": "00000003000400050201020202040402fc04fc06fc09000a0019#",
                "DeviceType": 100,
                "DeviceSubType": 769,
                "getModelIdentifierFlag_i": 1,
                "AttributeList": "00010010000300110033000500080019001c001d001a00210022002a000b",
                "DeviceEndpointNum_i": 1,
                "UnquieID": "001e5e090223649d"
            },
            "data": {
                "DeviceType": 100,
                "Endpoint": 9,
                "UniID": "001e5e090223649d"
            },
            "sFanS": {
                "FanMode": 5,
                "FanMode_a": 5
            },
            "sZDO": {
                "ProtocalType_i": 2,
                "DeviceName": "{\"deviceName\":\"FC600 HA\",\"ShortID_d\":10139}",
                "LeaveNetwork": 0,
                "MACAddress": "001e5e090223649d",
                "ShortID_d": 10139,
                "LeaveRequest_d": 0,
                "FirmwareVersion": "00350022",
                "JoinConfigVersion_i": "160426"
            },
            "sEndpt": {
                "DeviceType": 769,
                "Endpoint_i": 9
            },
            "sBasicS": {
                "ModelIdentifier": "FC600",
                "ManufactureName": "SALUS",
                "ApplicationVersion_d": 1,
                "StackVersion_d": 87,
                "PowerSource": 1,
                "HardwareVersion": "2"
            },
            "sComm": {
                "HoldType": 7,
                "Debug_d": "+2000+200020080?002102402102400101D000G3283BE274291BE27G3283BE274291BE27",
                "TimeFormat24Hour": 1,
                "AutoCoolingSetpoint_x100": 2400,
                "CoolingFanDelay": 0,
                "AutoHeatingSetpoint_x100": 2100,
                "HoldType_a": 7,
                "ShortCycleProtection": 300
            },
            "sZDOInfo": {
                "JoinConfigEnd": 1,
                "OnlineStatus_i": 1,
                "ConfigureReportResponse": "0204090000000000000100",
                "GatewayNodeDSN_i": "VR00ZN000561360"
            },
            "sFanCoil": {
                "DeviceSetting": "001030501001006032100030000000000800000010000611100000007FFF0000000000",
                "CompleteSetup": 15,
                "FanCoilType": 0,
                "S1ComTerminals": 0,
                "WindowIconEnable": 1,
                "HeatCoolSelection": 0,
                "S2ComTerminals": 0
            },
            "sTherS": {
                "CoolingSetpoint_x100_a": 2400,
                "LocalTemperature_x100": 2400,
                "RunningMode": 0,
                "CoolingSetpoint_x100": 2400,
                "TempCalibration_x10": 0,
                "HeatingSetpoint_x100": 800,
                "ErrorTherSTempSensorShort": 0,
                "Ocupancy": 0,
                "HeatingSetpoint_x100_a": 800,
                "SystemMode": 4,
                "OperationMode": 0,
                "MinCoolSetpoint_x100": 500,
                "MinHeatSetpoint_x100": 500,
                "MaxCoolSetpoint_x100": 4000,
                "MaxHeatSetpoint_x100": 4000,
                "RunningState": 0,
                "SystemMode_a": 4,
                "UnocCoolingSetpoint_x100": 3000,
                "ErrorTherSCompressor": 0,
                "ACErrorCode_d": 0,
                "ErrorInWallSwitchReleased": 0,
                "ErrorTherSOutdSensorShort": 0,
                "ErrorTherSOutdSensor": 0,
                "ErrorTherSTempSensor": 0,
                "UnocHeatingSetpoint_x100": 1500
            },
            "sScheS": {
                "ScheduleEnable": 0
            }
        }
    ]
}


```


#### @George-andrew commented at 2021-03-31T13:58:59Z

@jvitkauskas any update on this topic?

#### @jvitkauskas commented at 2021-04-04T17:30:13Z

Hi, @George-andrew I have some questions:

1. How does salus app lets you to set temperatures? Are there two temperatures to set (heating and cooling) or you are allowed to set one currently used based on the "SystemMode"?
2. Can you confirm that FC600 does not show humidity data?
3. What kind of actions are available in the app besides setting the temperature(s)?

#### @George-andrew commented at 2021-04-06T07:46:45Z

@jvitkauskas 

1. Possibility only set one current temperature on Salus SH (SmartHome), please see below gif how it looks. 
![FC600](https://user-images.githubusercontent.com/67461821/113676454-bcc55880-96bc-11eb-8a96-47718464a89d.gif)

2. FC600 hasn't a humidity sensor.  

3. Below availability actions for Fan-Coil thermostat : 
Set FAN speed, 
Heat/Cool,  
Follow Schedule, 
Schedule Override, 
Permanent Hold, 
ECO,  
OFF,
Lock key,


Many thanks for your support 


#### @MatthewAger commented at 2021-07-14T19:43:28Z

Hi, I have 4 FC600 controllers (2 currently installed - how can I help get this over the line to be supported?

#### @jvitkauskas commented at 2021-10-06T20:06:08Z

Closing this since support is present in version 0.3

---

## #3: iT600 gateway rejected 'read' command with content '{'requestAttr': 'deviceid', 'id': []}'

- URL: https://github.com/epoplavskis/pyit600/issues/3
- State: closed
- Author: @d0d0oo
- Created: 2020-09-08T21:19:11Z
- Updated: 2020-10-10T07:02:38Z
- Labels: none

### Issue body

Hi, when I launch main.py with demo application and trying to connect to my UGE600 gateway I get error during "read" request.  Trace log at the bottom. 
The same thing when I try to integrate with home-assistant. There is a issue about that in homeassistant_salus project: https://github.com/konradb3/homeassistant_salus/issues/2
Unfortunately I do not have any python experience and will be glad if someone can help figure out what is wrong.

System information:
- Host system: Windows 10
- Python 3.8.3
- Salus UGE600 gateway
- UGE600 software version: 020140200226
- UGE600 coordinator version: 20200115
- ZigBee chanel: 15
- Thermostat connected: TS600 (the one and only active component)
- There are other salus components mapped to UGE600 but they are turned off right now so there are warnings in app,
- UGE600 has ip from router DHCP, 192.168.1.15 via wifi only,
- UGE600 is reachable from salus it600 app.
- http://192.168.1.15 shows only empty single select and "Refresh ID List" button.

Trace log after launching main.py:
```
C:\Projekty\Python_sandbox\it600>python main.py --host 192.168.1.15 --euid 001E5E0########
DEBUG:pyit600:Trying to connect to gateway at 192.168.1.15
ERROR:pyit600:read failed: {'requestAttr': 'deviceid', 'id': []}
--- Logging error ---
Traceback (most recent call last):
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 280, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: iT600 gateway rejected 'read' command with content '{'requestAttr': 'deviceid', 'id': []}'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Python38\lib\logging\__init__.py", line 1081, in emit
    msg = self.format(record)
  File "C:\Python38\lib\logging\__init__.py", line 925, in format
    return fmt.format(record)
  File "C:\Python38\lib\logging\__init__.py", line 664, in format
    record.message = record.getMessage()
  File "C:\Python38\lib\logging\__init__.py", line 369, in getMessage
    msg = msg % self.args
TypeError: not all arguments converted during string formatting
Call stack:
  File "main.py", line 78, in <module>
    asyncio.run(main())
  File "C:\Python38\lib\asyncio\runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "C:\Python38\lib\asyncio\base_events.py", line 603, in run_until_complete
    self.run_forever()
  File "C:\Python38\lib\asyncio\windows_events.py", line 316, in run_forever
    super().run_forever()
  File "C:\Python38\lib\asyncio\base_events.py", line 570, in run_forever
    self._run_once()
  File "C:\Python38\lib\asyncio\base_events.py", line 1859, in _run_once
    handle._run()
  File "C:\Python38\lib\asyncio\events.py", line 81, in _run
    self._context.run(self._callback, *self._args)
  File "main.py", line 62, in main
    await gateway.poll_status(send_callback=True)
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 115, in poll_status
    status = await self._make_encrypted_request(
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 291, in _make_encrypted_request
    _LOGGER.error("Exception. %s / %s", type(e), repr(e.args), e)
Message: 'Exception. %s / %s'
Arguments: (<class 'pyit600.exceptions.IT600CommandError'>, '("iT600 gateway rejected \'read\' command with content \'{\'requestAttr\': \'deviceid\', \'id\': []}\'",)', IT600CommandError("iT600 gateway rejected 'read' command with content '{'requestAttr': 'deviceid', 'id': []}'"))
Traceback (most recent call last):
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 280, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: iT600 gateway rejected 'read' command with content '{'requestAttr': 'deviceid', 'id': []}'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "main.py", line 78, in <module>
    asyncio.run(main())
  File "C:\Python38\lib\asyncio\runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "C:\Python38\lib\asyncio\base_events.py", line 616, in run_until_complete
    return future.result()
  File "main.py", line 62, in main
    await gateway.poll_status(send_callback=True)
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 115, in poll_status
    status = await self._make_encrypted_request(
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 292, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: Unknown error occurred while communicating with iT600 gateway
```

### Conversation

#### @jvitkauskas commented at 2020-09-08T21:31:11Z

I guess that my project does not support TS600 thermostats. I have added request/response debugging to the demo `main.py`. Can you pull latest master and run it with `--debug` and send me the output? You can redact things you don't like. I only need the response to `{"requestAttr": "readall"}` request.

I am guessing the problem will be here: https://github.com/jvitkauskas/pyit600/blob/master/pyit600/gateway.py#L114 (your thermostat is probably not of a `it600ThermHW` kind)

~I should also probably modify a code that it won't try to send any requests if no supported thermostats are found.~

#### @d0d0oo commented at 2020-09-08T22:16:00Z

I've just send you logs. I thought even if there is unsupported equipment it will be listed somewhere :)

#### @jvitkauskas commented at 2020-09-08T22:23:32Z

Can you try running `main.py` from `ts600` branch and see if it will work and set your thermostat to 21 degrees? https://github.com/jvitkauskas/pyit600/tree/ts600

#### @d0d0oo commented at 2020-09-09T07:12:32Z

So this is a log from new branch for ts600 after execute main.py trying to change temperature. A listed device id is the right id for ts600 thermostat. I don't understand why this key is incorrect...

```
C:\Projekty\Python_sandbox\it600>python main.py --host 192.168.1.15 --euid 001E5E0XXXXXXXX
DEBUG:pyit600:Trying to connect to gateway at 192.168.1.15
Got callback for device id: 001e5e09023f74cc
Traceback (most recent call last):
  File "main.py", line 90, in <module>
    asyncio.run(main())
  File "C:\Python38\lib\asyncio\runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "C:\Python38\lib\asyncio\base_events.py", line 616, in run_until_complete
    return future.result()
  File "main.py", line 70, in main
    await gateway.poll_status(send_callback=True)
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 142, in poll_status
    current_temperature=th["LocalTemperature_x100"] / 100,
KeyError: 'LocalTemperature_x100'
```

#### @jvitkauskas commented at 2020-09-09T08:33:01Z

Ok, it seems like the temperature control is different for that thermostat. I'll help you find out what's needed later. In the meanwhile, can you send me the screenshot of the mobile app showing the thermostat control screen?

#### @d0d0oo commented at 2020-09-09T08:57:00Z

Here you go. Thermostat is paired with one smart relay and three window sensors but right now their are not connected.
![Screenshot_2020-09-09-10-48-13-322_com salus connect solution](https://user-images.githubusercontent.com/70240088/92577624-23030d80-f28b-11ea-8dab-46d47c970d8f.png)
![Screenshot_2020-09-09-10-49-02-541_com salus connect solution](https://user-images.githubusercontent.com/70240088/92577638-25fdfe00-f28b-11ea-8381-1e224b9106b8.png)



#### @d0d0oo commented at 2020-09-10T21:16:13Z

I've just run main.py several times and get two different responses. One shows error indicating probably connection error (?), and at the next shot I've got probably correct temperature change - my thermostat is configured to max temp 20oC and main.py is trying set 21oC. Despite this temperature changed from 13,5oC to 20oC (which is max). Checked it with different values and it works. The only change during last two days was that I disconnected UGE600 from power.
What is interesting the connection error occurs because I had opened website (http://<UGE600_IP>) with "Refresh Id List" button which is sending some read requests all the time. When I closed it I could control thermostat temperature from main.py .
~~I will try get some test with other values.~~
I've tested all three methods:
- set_climate_device_preset(device_id, preset)
Works well with three constants but I need to do more tests with changing temperature during "Follow Schedule". When you change temperature during this preset thermostat should set it and change preset to "Untill HH:mm". Sometimes it changes temperature according to current schedule position just after few seconds. I have exactly the same problem with Salus Application.
- set_climate_device_temperature(device_id, setpoint_celsius)
Works as it should.
- set_climate_device_mode(device_id, mode)
I do not know what is for. When set to "off" it acts like set_climate_device_preset(device_id, "Off") , when set to "heat it" acts like set_climate_device_preset(device_id, "Follow Schedule")

1. Correct temperature change:
```
C:\Projekty\Python_sandbox\it600>python main.py --host 192.168.1.15 --euid 001E5EXXXXXXXX
DEBUG:pyit600:Trying to connect to gateway at 192.168.1.15
Got callback for device id: 001e5e09023f74cc
DEBUG:pyit600:Refreshed 1 climate devices
All climate devices:
{'001e5e09023f74cc': ClimateDevice(available=True, name='My', unique_id='001e5e09023f74cc', temperature_unit='°C', precision=0.5, current_temperature=22.5, target_temperature=13.5, max_temp=20.0, min_temp=5.0, hvac_mode='heat', hvac_action='idle', hvac_modes=['off', 'heat'], preset_mode='Permanent Hold', preset_modes=['Follow Schedule', 'Permanent Hold', 'Off'], supported_features=17, device_class='temperature', data={'DeviceType': 100, 'UniID': '001e5e09023f74cc', 'Endpoint': 9})}
Climate device 001e5e09023f74cc status:
ClimateDevice(available=True, name='My', unique_id='001e5e09023f74cc', temperature_unit='°C', precision=0.5, current_temperature=22.5, target_temperature=13.5, max_temp=20.0, min_temp=5.0, hvac_mode='heat', hvac_action='idle', hvac_modes=['off', 'heat'], preset_mode='Permanent Hold', preset_modes=['Follow Schedule', 'Permanent Hold', 'Off'], supported_features=17, device_class='temperature', data={'DeviceType': 100, 'UniID': '001e5e09023f74cc', 'Endpoint': 9})
Setting heating device 001e5e09023f74cc temperature to 21 degrees celsius
```
2. Strange error with connection (did not restart UGE600):
```
C:\Projekty\Python_sandbox\it600>python main.py --host 192.168.1.15 --euid 001E5E09XXXXXXXX
DEBUG:pyit600:Trying to connect to gateway at 192.168.1.15
--- Logging error ---
Traceback (most recent call last):
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 278, in _make_encrypted_request
    resp = await self._session.post(
  File "C:\Python38\lib\site-packages\aiohttp\client.py", line 504, in _request
    await resp.start(conn)
  File "C:\Python38\lib\site-packages\aiohttp\client_reqrep.py", line 847, in start
    message, payload = await self._protocol.read()  # type: ignore  # noqa
  File "C:\Python38\lib\site-packages\aiohttp\streams.py", line 591, in read
    await self._waiter
aiohttp.client_exceptions.ServerDisconnectedError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Python38\lib\logging\__init__.py", line 1081, in emit
    msg = self.format(record)
  File "C:\Python38\lib\logging\__init__.py", line 925, in format
    return fmt.format(record)
  File "C:\Python38\lib\logging\__init__.py", line 664, in format
    record.message = record.getMessage()
  File "C:\Python38\lib\logging\__init__.py", line 369, in getMessage
    msg = msg % self.args
TypeError: not all arguments converted during string formatting
Call stack:
  File "main.py", line 90, in <module>
    asyncio.run(main())
  File "C:\Python38\lib\asyncio\runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "C:\Python38\lib\asyncio\base_events.py", line 603, in run_until_complete
    self.run_forever()
  File "C:\Python38\lib\asyncio\windows_events.py", line 316, in run_forever
    super().run_forever()
  File "C:\Python38\lib\asyncio\base_events.py", line 570, in run_forever
    self._run_once()
  File "C:\Python38\lib\asyncio\base_events.py", line 1859, in _run_once
    handle._run()
  File "C:\Python38\lib\asyncio\events.py", line 81, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 306, in _make_encrypted_request
    _LOGGER.error("Exception. %s / %s", type(e), repr(e.args), e)
Message: 'Exception. %s / %s'
Arguments: (<class 'aiohttp.client_exceptions.ServerDisconnectedError'>, '()', ServerDisconnectedError())
Traceback (most recent call last):
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 278, in _make_encrypted_request
    resp = await self._session.post(
  File "C:\Python38\lib\site-packages\aiohttp\client.py", line 504, in _request
    await resp.start(conn)
  File "C:\Python38\lib\site-packages\aiohttp\client_reqrep.py", line 847, in start
    message, payload = await self._protocol.read()  # type: ignore  # noqa
  File "C:\Python38\lib\site-packages\aiohttp\streams.py", line 591, in read
    await self._waiter
aiohttp.client_exceptions.ServerDisconnectedError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "main.py", line 90, in <module>
    asyncio.run(main())
  File "C:\Python38\lib\asyncio\runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "C:\Python38\lib\asyncio\base_events.py", line 616, in run_until_complete
    return future.result()
  File "main.py", line 60, in main
    await gateway.connect()
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 69, in connect
    all_devices = await self._make_encrypted_request(
  File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 307, in _make_encrypted_request
    raise IT600CommandError(
pyit600.exceptions.IT600CommandError: Unknown error occurred while communicating with iT600 gateway
```

#### @d0d0oo commented at 2020-09-11T07:16:55Z

> 
> 
> So this is a log from new branch for ts600 after execute main.py trying to change temperature. A listed device id is the right id for ts600 thermostat. I don't understand why this key is incorrect...
> 
> ```
> C:\Projekty\Python_sandbox\it600>python main.py --host 192.168.1.15 --euid 001E5E0XXXXXXXX
> DEBUG:pyit600:Trying to connect to gateway at 192.168.1.15
> Got callback for device id: 001e5e09023f74cc
> Traceback (most recent call last):
>   File "main.py", line 90, in <module>
>     asyncio.run(main())
>   File "C:\Python38\lib\asyncio\runners.py", line 43, in run
>     return loop.run_until_complete(main)
>   File "C:\Python38\lib\asyncio\base_events.py", line 616, in run_until_complete
>     return future.result()
>   File "main.py", line 70, in main
>     await gateway.poll_status(send_callback=True)
>   File "C:\Python38\lib\site-packages\pyit600\gateway.py", line 142, in poll_status
>     current_temperature=th["LocalTemperature_x100"] / 100,
> KeyError: 'LocalTemperature_x100'
> ```
Unfortunately, the above error started reappearing. After restarting the UGE600, everything works as I wrote in the previous comment. Wonder what's going on with this UGE600 gateway...

#### @jvitkauskas commented at 2020-09-14T18:47:19Z

I recommend not using UGE600 website as it sends unencrypted requests which backend does not understand. Furthermore, I think the gateway strategy is to delay and not to send any response on incorrect data, so you might be unnecessarily DDoSing your gateway.

You are correct that `set_climate_device_mode` is redundant. I have included it just because home assistant API has a similar method.

Did that strange error occur when you have visited UGE600 website?

#### @dyrvigk commented at 2020-09-15T08:58:42Z

here is log after doing what you asked and run main.py with python3  

sudo apt update
sudo apt install git python3 python3-pip
git clone https://github.com/jvitkauskas/pyit600.git
cd pyit600
pip3 install .
python3 main.py --host YOUR_GATEWAYS_IP_ADDRESS_HERE --euid YOUR_GATEWAYS_EUID_HERE --debug

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"sZDOInfo":{"GatewayNodeDSN_i":"VR00ZN000093518","OnlineStatus_i":1,"JoinConfigEnd":1},"data":{"Endpoint":9,"DeviceType":100,"UniID":"001e5e09025f4c40"},"sZDO":{"JoinConfigVersion_i":"190629","ProtocalType_i":1,"FirmwareVersion":"0000001D","MACAddress":"001e5e09025f4c40","ShortID_d":61919,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Køkken\",\"ShortID_d\":61919}"},"sScheS":{"HeatSchedule3":"0effffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd","ScheduleEnable":2,"HeatSchedule1":"0e010600210023001900ffff2100ffff2100ffff1800ffff2100dd0600210023001900ffff2100ffff2100ffff1800ffff2100ffffffffffffffffffffffff","HeatSchedule2":"0effffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":64,"DeviceType":100,"UnquieID":"001e5e09025f4c40","AttributeList":"0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SQ610RF"},"sBasicS":{"ModelIdentifier":"SQ610RF","HardwareVersion":"2"},"sEndpt":{"DeviceType":64,"Endpoint_i":9},"sIT600D":{"DeviceIndex":32,"SyncResponseVersion_d":"0000001D","ConnectType_i":3},"sIT600TH":{"Error07":0,"HeatingSetpoint_x100_a":2700,"Error21":0,"Status_d":"71a50d0225500000012700210021000404013030303000004802ffffffffffffffffffffffff010003870005003500030104bccb00000200000000ffffffffffffffffffffffffffffffffff1c","ProgramOperationMode":0,"Error04":0,"Error03":0,"Error01":0,"AutoHeatingSetpoint_x100_a":2100,"Error02":0,"LockKey":0,"Error08":0,"Error06":0,"CoolingSetpoint_x100":2700,"Error09":0,"Error23":0,"SystemMode":4,"Error22":0,"AutoCoolingSetpoint_x100_a":2100,"Error24":0,"Error25":0,"LocalTemperature_x100":2550,"Error30":0,"Error31":0,"Error32":0,"SystemMode_a":4,"CloudySetpoint_x100":0,"PairedTRVShortID":"FFFFFFFFFFFFFFFFFFFFFFFF","HeatingSetpoint_x100":2700,"SunnySetpoint_x100":48,"AutoCoolingSetpoint_x100":2100,"AutoHeatingSetpoint_x100":2100,"RunningState":1,"RunningMode":4,"PairedWCNumber":102,"ScheduleType":1,"HoldType":2,"TimeFormat24Hour":1,"CoolingSetpoint_x100_a":2700,"HoldType_a":2,"LockKey_a":0},"status":"success"},{"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":0,"DeviceType":200,"UniID":"0000000000000000"},"sZDO":{"ProtocalType_i":2,"FirmwareVersion":"20200115","MACAddress":"001e5e0902134bab","ShortID_d":0,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"VR00ZN000093517\",\"ShortID_d\":0}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":200,"UnquieID":"0000000000000000","AttributeList":"000100040003001100050008000b001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-ZC"},"sEndpt":{"DeviceType":0,"Endpoint_i":0},"sCoord":{"PermitJoinState_d":0,"Channel_d":24,"PANID_d":27580,"Form_d":1,"ErrorCoordUART":0,"TimeFormat24Hour":1,"IdentifyInProgress_i":0},"sBasicS":{"ModelIdentifier":"SAU2AG1-ZC","HardwareVersion":"197"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/39a1449c-8dba-472f-add8-c76b1c511f71/SAU2AG1-ZC_20200115.tar.gz","OTAFirmwareVersion_d":"20200115","OTAStatus_d":0,"endPoint_i":0}},{"data":{"Endpoint":0,"DeviceType":300,"UniID":"0000000000000000"},"sGateway":{"NetworkWiFiIP":"","GatewaySoftwareVersion":"020140200226","GatewayHardwareVersion":"197","NetworkLANMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","LocationMode_C":"","NetworkPriDNS":"192.168.1.1","NetworkLANIP":"192.168.1.122","LANConnected_d":1,"TimeStatus_i":2,"NetworkLANMAC":"00:1e:5e:00:eb:65","KeyState_i":0,"DSTEnable_i":1,"NetworkWiFiMAC":"00:1e:5e:00:eb:64","NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","EnableNetworkReset":0,"WirelessAPpassword":"fdc8db1e464cc8d31676eab97ad74ce1","WiFiConnected_d":0,"DeviceTimeZone_i":3600,"IsRtcRight_i":1,"AylaConnected_i":1,"IsSdCardNormal_i":0,"NetworkLANSubnet":"255.255.255.0","LEDMode":1,"NetworkLANRouterAddr":"192.168.1.1","NetworkSecDNS":"","PhoneLocation":"","ModelIdentifier":"UGE600","LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509145fadc2bcee00a248f12b2676c2f399","WiFiMode":0,"DisableLocalMode":0,"TimeZone":"Europe/Copenhagen","TimeOffset_i":1,"Sunset":"1600191761","Sunrise":"1600145917","OutdoorTemperature":1100.0},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":300,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-GW"},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAL2BG1","AylaHeartBeatFrequency":0},"Product":{"Mode":1,"Model":"SAL2BG1"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/ca6c916a-aae2-41c3-a051-e9ed920c3c8d/SAU2AG1-GW_020140200226.tar.gz","OTAFirmwareVersion_d":"020140200226","OTAStatus_d":0,"endPoint_i":0},"sAyla_i":{"aylaConfigStatus":1,"aylaNetWorkStatus":1,"aylaDeviceID":"AC000W000531357","aylaGateWayDsn":"VR00ZN000093518","aylaTimeConfig":"1,1,60,1603587600","aylaSetUTCTimeStatus":1}}]}

DEBUG:pyit600:Gateway request: POST http://192.168.1.122:80/deviceid/read
{"requestAttr": "deviceid", "id": [{"data": {"Endpoint": 9, "DeviceType": 100, "UniID": "001e5e09025f4c40"}}]}

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"sZDOInfo":{"GatewayNodeDSN_i":"VR00ZN000093518","OnlineStatus_i":1,"JoinConfigEnd":1},"data":{"Endpoint":9,"DeviceType":100,"UniID":"001e5e09025f4c40"},"sZDO":{"JoinConfigVersion_i":"190629","ProtocalType_i":1,"FirmwareVersion":"0000001D","MACAddress":"001e5e09025f4c40","ShortID_d":61919,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"Køkken\",\"ShortID_d\":61919}"},"sScheS":{"HeatSchedule3":"0effffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd","ScheduleEnable":2,"HeatSchedule1":"0e010600210023001900ffff2100ffff2100ffff1800ffff2100dd0600210023001900ffff2100ffff2100ffff1800ffff2100ffffffffffffffffffffffff","HeatSchedule2":"0effffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":64,"DeviceType":100,"UnquieID":"001e5e09025f4c40","AttributeList":"0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SQ610RF"},"sBasicS":{"ModelIdentifier":"SQ610RF","HardwareVersion":"2"},"sEndpt":{"DeviceType":64,"Endpoint_i":9},"sIT600D":{"DeviceIndex":32,"SyncResponseVersion_d":"0000001D","ConnectType_i":3},"sIT600TH":{"Error07":0,"HeatingSetpoint_x100_a":2700,"Error21":0,"Status_d":"71a50d0225500000012700210021000404013030303000004802ffffffffffffffffffffffff010003870005003500030104bccb00000200000000ffffffffffffffffffffffffffffffffff1c","ProgramOperationMode":0,"Error04":0,"Error03":0,"Error01":0,"AutoHeatingSetpoint_x100_a":2100,"Error02":0,"LockKey":0,"Error08":0,"Error06":0,"CoolingSetpoint_x100":2700,"Error09":0,"Error23":0,"SystemMode":4,"Error22":0,"AutoCoolingSetpoint_x100_a":2100,"Error24":0,"Error25":0,"LocalTemperature_x100":2550,"Error30":0,"Error31":0,"Error32":0,"SystemMode_a":4,"CloudySetpoint_x100":0,"PairedTRVShortID":"FFFFFFFFFFFFFFFFFFFFFFFF","HeatingSetpoint_x100":2700,"SunnySetpoint_x100":48,"AutoCoolingSetpoint_x100":2100,"AutoHeatingSetpoint_x100":2100,"RunningState":1,"RunningMode":4,"PairedWCNumber":102,"ScheduleType":1,"HoldType":2,"TimeFormat24Hour":1,"CoolingSetpoint_x100_a":2700,"HoldType_a":2,"LockKey_a":0},"status":"success"}]}

Traceback (most recent call last):
  File "main.py", line 90, in <module>
    asyncio.run(main())
  File "/usr/lib/python3.8/asyncio/runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.8/asyncio/base_events.py", line 616, in run_until_complete
    return future.result()
  File "main.py", line 70, in main
    await gateway.poll_status(send_callback=True)
  File "/home/kenn/pyit600/pyit600/gateway.py", line 142, in poll_status
    max_temp=th["MaxHeatSetpoint_x100"] / 100,
KeyError: 'MaxHeatSetpoint_x100'

kenn

#### @dyrvigk commented at 2020-09-15T09:00:44Z

all the temperatures in the log file are correct and acording to termostat sq610RF

kenn

#### @jvitkauskas commented at 2020-09-15T10:27:18Z

@dyrvigk what is the maximum and the minimum temperature you can set your thermostat to? Do you have it configurable in Salus App?

#### @dyrvigk commented at 2020-09-15T10:37:46Z

Yes

From 5-35 degree c

tir. 15. sep. 2020 12.27 skrev Julius Vitkauskas <notifications@github.com>:

> @dyrvigk <https://github.com/dyrvigk> what is the maximum and the minimum
> temperature you can set your thermostat to? Do you have it configurable in
> Salus App?
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/jvitkauskas/pyit600/issues/3#issuecomment-692625419>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AG7RHTBKT7ILTJ4MDHRDHD3SF46RJANCNFSM4RAQ3PXQ>
> .
>


#### @jvitkauskas commented at 2020-09-15T14:07:56Z

@dyrvigk I have made some fallback values for min/max temperature. Get the latest files and try again.

#### @dyrvigk commented at 2020-09-15T16:06:34Z

Hi Now it looks like something happens 

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":0,"DeviceType":200,"UniID":"0000000000000000"},"sZDO":{"ProtocalType_i":2,"FirmwareVersion":"20200115","MACAddress":"001e5e0902134bab","ShortID_d":0,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"VR00ZN000093517\",\"ShortID_d\":0}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":200,"UnquieID":"0000000000000000","AttributeList":"000100040003001100050008000b001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-ZC"},"sEndpt":{"DeviceType":0,"Endpoint_i":0},"sCoord":{"PANID_d":27580,"PermitJoinState_d":0,"Channel_d":24,"PermitJoinTime_i":0,"ReceiveZigbeeCommand_d":"7c0fb809fc25640900087e00800080","Form_d":1,"ErrorCoordUART":0,"TimeFormat24Hour":1,"IdentifyInProgress_i":0},"sBasicS":{"ModelIdentifier":"SAU2AG1-ZC","HardwareVersion":"197"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/39a1449c-8dba-472f-add8-c76b1c511f71/SAU2AG1-ZC_20200115.tar.gz","OTAFirmwareVersion_d":"20200115","OTAStatus_d":0,"endPoint_i":0}},{"data":{"Endpoint":0,"DeviceType":300,"UniID":"0000000000000000"},"sGateway":{"NetworkWiFiIP":"","GatewaySoftwareVersion":"020140200226","GatewayHardwareVersion":"197","NetworkLANMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","LocationMode_C":"","NetworkPriDNS":"192.168.1.1","NetworkLANIP":"192.168.1.122","LANConnected_d":1,"TimeStatus_i":2,"NetworkLANMAC":"00:1e:5e:00:eb:65","KeyState_i":0,"DSTEnable_i":1,"NetworkWiFiMAC":"00:1e:5e:00:eb:64","NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","EnableNetworkReset":0,"WirelessAPpassword":"fdc8db1e464cc8d31676eab97ad74ce1","WiFiConnected_d":0,"DeviceTimeZone_i":3600,"IsRtcRight_i":1,"AylaConnected_i":1,"IsSdCardNormal_i":0,"NetworkLANSubnet":"255.255.255.0","LEDMode":1,"NetworkLANRouterAddr":"192.168.1.1","NetworkSecDNS":"","PhoneLocation":"","ModelIdentifier":"UGE600","LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509145fadc2bcee00a248f12b2676c2f399","WiFiMode":0,"DisableLocalMode":0,"TimeZone":"Europe/Copenhagen","TimeOffset_i":1,"Sunset":"1600191761","Sunrise":"1600145917","OutdoorTemperature":2400.0},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":300,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-GW"},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAL2BG1","AylaHeartBeatFrequency":0,"OtherDebugMsg_d":"del device euid:001e5e09025f4c40, shortid: 0x2c08, debug_code:1"},"Product":{"Mode":1,"Model":"SAL2BG1"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/ca6c916a-aae2-41c3-a051-e9ed920c3c8d/SAU2AG1-GW_020140200226.tar.gz","OTAFirmwareVersion_d":"020140200226","OTAStatus_d":0,"endPoint_i":0},"sAyla_i":{"aylaConfigStatus":1,"aylaNetWorkStatus":1,"aylaDeviceID":"AC000W000531357","aylaGateWayDsn":"VR00ZN000093518","aylaTimeConfig":"1,1,60,1603587600","aylaSetUTCTimeStatus":1}},{"sZDOInfo":{"JoinConfigEnd":1,"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":9,"DeviceType":100,"UniID":"001e5e09025f4c40"},"sScheS":{"HeatSchedule3":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd","ScheduleEnable":1,"HeatSchedule1":"03010600210023001900ffff2100ffff2100ffff2100ffff2100dd0600210023001900ffff2100ffff2100ffff2100ffff2100ffffffffffffffffffffffff","HeatSchedule2":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"},"sZDO":{"JoinConfigVersion_i":"190629","ProtocalType_i":1,"FirmwareVersion":"0000001D","MACAddress":"001e5e09025f4c40","ShortID_d":25637,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"SQ610RF  Quantum rumtermostat 1\",\"ShortID_d\":25637}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":64,"DeviceType":100,"UnquieID":"001e5e09025f4c40","AttributeList":"0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SQ610RF"},"sBasicS":{"ModelIdentifier":"SQ610RF","HardwareVersion":"2"},"sEndpt":{"DeviceType":64,"Endpoint_i":9},"sIT600D":{"DeviceIndex":32,"SyncResponseVersion_d":"0000001D","ConnectType_i":3},"sIT600TH":{"Status_2_d":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","SunnySetpoint_x100":52,"AutoCoolingSetpoint_x100":2100,"Error07":0,"HeatingSetpoint_x100_a":2100,"Error21":0,"Status_d":"710b0d0028500000012100210021000400003030303000005202ffffffffffffffffffffffff010003860005003500030104cccf00000000000000ffffffffffffffffffffffffffffffffff1c","ProgramOperationMode":0,"MaxHeatSetpoint_x100_a":3500,"Error04":0,"Error03":0,"Error01":0,"AutoHeatingSetpoint_x100_a":2100,"Error02":0,"LockKey":0,"Error08":0,"Error06":0,"CoolingSetpoint_x100":2100,"OUTSensorType":0,"Error09":0,"Error23":0,"MaxHeatSetpoint_x100":3500,"SystemMode":4,"Error22":0,"AutoCoolingSetpoint_x100_a":2100,"HeatingControl":1,"Error24":0,"Error25":0,"MinCoolSetpoint_x100":500,"Schedule":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","LocalTemperature_x100":2850,"Error30":0,"Error31":0,"Error32":0,"SystemMode_a":4,"CloudySetpoint_x100":0,"PairedTRVShortID":"FFFFFFFFFFFFFFFFFFFFFFFF","CoolingControl":0,"HeatingSetpoint_x100":2100,"AutoHeatingSetpoint_x100":2100,"RunningState":0,"RunningMode":0,"PairedWCNumber":102,"ScheduleType":1,"HoldType":0,"OUTSensorProbe":0,"TimeFormat24Hour":1,"MinHeatSetpoint_x100":500,"MaxCoolSetpoint_x100":3500,"MinCoolSetpoint_x100_a":500,"CoolingSetpoint_x100_a":2100,"HoldType_a":0,"LockKey_a":0,"TemperatureDisplayMode":0},"sIT600I":{"CommandResponse_d":"42323000"}}]}

DEBUG:pyit600:Gateway request: POST http://192.168.1.122:80/deviceid/read
{"requestAttr": "readall"}

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"sZDOInfo":{"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":0,"DeviceType":200,"UniID":"0000000000000000"},"sZDO":{"ProtocalType_i":2,"FirmwareVersion":"20200115","MACAddress":"001e5e0902134bab","ShortID_d":0,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"VR00ZN000093517\",\"ShortID_d\":0}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":200,"UnquieID":"0000000000000000","AttributeList":"000100040003001100050008000b001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-ZC"},"sEndpt":{"DeviceType":0,"Endpoint_i":0},"sCoord":{"PANID_d":27580,"PermitJoinState_d":0,"Channel_d":24,"PermitJoinTime_i":0,"ReceiveZigbeeCommand_d":"7c0fb809fc25640900087e00800080","Form_d":1,"ErrorCoordUART":0,"TimeFormat24Hour":1,"IdentifyInProgress_i":0},"sBasicS":{"ModelIdentifier":"SAU2AG1-ZC","HardwareVersion":"197"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/39a1449c-8dba-472f-add8-c76b1c511f71/SAU2AG1-ZC_20200115.tar.gz","OTAFirmwareVersion_d":"20200115","OTAStatus_d":0,"endPoint_i":0}},{"data":{"Endpoint":0,"DeviceType":300,"UniID":"0000000000000000"},"sGateway":{"NetworkWiFiIP":"","GatewaySoftwareVersion":"020140200226","GatewayHardwareVersion":"197","NetworkLANMode":1,"NetworkSSID":"fdb783604bdf1a2e4d6a78802c91ab7b","LocationMode_C":"","NetworkPriDNS":"192.168.1.1","NetworkLANIP":"192.168.1.122","LANConnected_d":1,"TimeStatus_i":2,"NetworkLANMAC":"00:1e:5e:00:eb:65","KeyState_i":0,"DSTEnable_i":1,"NetworkWiFiMAC":"00:1e:5e:00:eb:64","NetworkPassword":"fdb783604bdf1a2e4d6a78802c91ab7b","EnableNetworkReset":0,"WirelessAPpassword":"fdc8db1e464cc8d31676eab97ad74ce1","WiFiConnected_d":0,"DeviceTimeZone_i":3600,"IsRtcRight_i":1,"AylaConnected_i":1,"IsSdCardNormal_i":0,"NetworkLANSubnet":"255.255.255.0","LEDMode":1,"NetworkLANRouterAddr":"192.168.1.1","NetworkSecDNS":"","PhoneLocation":"","ModelIdentifier":"UGE600","LocalModeAccessCode":"2ca44efc0c3316b53e65c02b8307f509145fadc2bcee00a248f12b2676c2f399","WiFiMode":0,"DisableLocalMode":0,"TimeZone":"Europe/Copenhagen","TimeOffset_i":1,"Sunset":"1600191761","Sunrise":"1600145917","OutdoorTemperature":2400.0},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":0,"DeviceType":300,"UnquieID":"0000000000000000","AttributeList":"00010002000b000c001e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SAU2AG1-GW"},"sDebug":{"LocalDebugMsg_d":"Model ID is: SAL2BG1","AylaHeartBeatFrequency":0,"OtherDebugMsg_d":"del device euid:001e5e09025f4c40, shortid: 0x2c08, debug_code:1"},"Product":{"Mode":1,"Model":"SAL2BG1"},"sOTA":{"OTAFirmwareURL_d":"http://eu.salusconnect.io/download/firmware/ca6c916a-aae2-41c3-a051-e9ed920c3c8d/SAU2AG1-GW_020140200226.tar.gz","OTAFirmwareVersion_d":"020140200226","OTAStatus_d":0,"endPoint_i":0},"sAyla_i":{"aylaConfigStatus":1,"aylaNetWorkStatus":1,"aylaDeviceID":"AC000W000531357","aylaGateWayDsn":"VR00ZN000093518","aylaTimeConfig":"1,1,60,1603587600","aylaSetUTCTimeStatus":1}},{"sZDOInfo":{"JoinConfigEnd":1,"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":9,"DeviceType":100,"UniID":"001e5e09025f4c40"},"sScheS":{"HeatSchedule3":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd","ScheduleEnable":1,"HeatSchedule1":"03010600210023001900ffff2100ffff2100ffff2100ffff2100dd0600210023001900ffff2100ffff2100ffff2100ffff2100ffffffffffffffffffffffff","HeatSchedule2":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"},"sZDO":{"JoinConfigVersion_i":"190629","ProtocalType_i":1,"FirmwareVersion":"0000001D","MACAddress":"001e5e09025f4c40","ShortID_d":25637,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"SQ610RF  Quantum rumtermostat 1\",\"ShortID_d\":25637}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":64,"DeviceType":100,"UnquieID":"001e5e09025f4c40","AttributeList":"0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SQ610RF"},"sBasicS":{"ModelIdentifier":"SQ610RF","HardwareVersion":"2"},"sEndpt":{"DeviceType":64,"Endpoint_i":9},"sIT600D":{"DeviceIndex":32,"SyncResponseVersion_d":"0000001D","ConnectType_i":3},"sIT600TH":{"Status_2_d":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","SunnySetpoint_x100":52,"AutoCoolingSetpoint_x100":2100,"Error07":0,"HeatingSetpoint_x100_a":2100,"Error21":0,"Status_d":"710b0d0028500000012100210021000400003030303000005202ffffffffffffffffffffffff010003860005003500030104cccf00000000000000ffffffffffffffffffffffffffffffffff1c","ProgramOperationMode":0,"MaxHeatSetpoint_x100_a":3500,"Error04":0,"Error03":0,"Error01":0,"AutoHeatingSetpoint_x100_a":2100,"Error02":0,"LockKey":0,"Error08":0,"Error06":0,"CoolingSetpoint_x100":2100,"OUTSensorType":0,"Error09":0,"Error23":0,"MaxHeatSetpoint_x100":3500,"SystemMode":4,"Error22":0,"AutoCoolingSetpoint_x100_a":2100,"HeatingControl":1,"Error24":0,"Error25":0,"MinCoolSetpoint_x100":500,"Schedule":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","LocalTemperature_x100":2850,"Error30":0,"Error31":0,"Error32":0,"SystemMode_a":4,"CloudySetpoint_x100":0,"PairedTRVShortID":"FFFFFFFFFFFFFFFFFFFFFFFF","CoolingControl":0,"HeatingSetpoint_x100":2100,"AutoHeatingSetpoint_x100":2100,"RunningState":0,"RunningMode":0,"PairedWCNumber":102,"ScheduleType":1,"HoldType":0,"OUTSensorProbe":0,"TimeFormat24Hour":1,"MinHeatSetpoint_x100":500,"MaxCoolSetpoint_x100":3500,"MinCoolSetpoint_x100_a":500,"CoolingSetpoint_x100_a":2100,"HoldType_a":0,"LockKey_a":0,"TemperatureDisplayMode":0},"sIT600I":{"CommandResponse_d":"42323000"}}]}

DEBUG:pyit600:Gateway request: POST http://192.168.1.122:80/deviceid/read
{"requestAttr": "deviceid", "id": [{"data": {"Endpoint": 9, "DeviceType": 100, "UniID": "001e5e09025f4c40"}}]}

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"sZDOInfo":{"JoinConfigEnd":1,"OnlineStatus_i":1,"GatewayNodeDSN_i":"VR00ZN000093518"},"data":{"Endpoint":9,"DeviceType":100,"UniID":"001e5e09025f4c40"},"sScheS":{"HeatSchedule3":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd","ScheduleEnable":1,"HeatSchedule1":"03010600210023001900ffff2100ffff2100ffff2100ffff2100dd0600210023001900ffff2100ffff2100ffff2100ffff2100ffffffffffffffffffffffff","HeatSchedule2":"03ffffffffffffffffffffffffffffffffffffffffffffffffddffffffffffffffffffffffffffffffffffffffffffffffffdd"},"sZDO":{"JoinConfigVersion_i":"190629","ProtocalType_i":1,"FirmwareVersion":"0000001D","MACAddress":"001e5e09025f4c40","ShortID_d":25637,"LeaveNetwork":0,"LeaveRequest_d":0,"DeviceName":"{\"deviceName\":\"SQ610RF  Quantum rumtermostat 1\",\"ShortID_d\":25637}"},"DeviceL":{"DeviceEndpointNum_i":1,"getModelIdentifierFlag_i":1,"DeviceSubType":64,"DeviceType":100,"UnquieID":"001e5e09025f4c40","AttributeList":"0001000500080010000b000a0028000300110012002a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","ModelIdentifier_i":"SQ610RF"},"sBasicS":{"ModelIdentifier":"SQ610RF","HardwareVersion":"2"},"sEndpt":{"DeviceType":64,"Endpoint_i":9},"sIT600D":{"DeviceIndex":32,"SyncResponseVersion_d":"0000001D","ConnectType_i":3},"sIT600TH":{"Status_2_d":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","SunnySetpoint_x100":52,"AutoCoolingSetpoint_x100":2100,"Error07":0,"HeatingSetpoint_x100_a":2100,"Error21":0,"Status_d":"710b0d0028500000012100210021000400003030303000005202ffffffffffffffffffffffff010003860005003500030104cccf00000000000000ffffffffffffffffffffffffffffffffff1c","ProgramOperationMode":0,"MaxHeatSetpoint_x100_a":3500,"Error04":0,"Error03":0,"Error01":0,"AutoHeatingSetpoint_x100_a":2100,"Error02":0,"LockKey":0,"Error08":0,"Error06":0,"CoolingSetpoint_x100":2100,"OUTSensorType":0,"Error09":0,"Error23":0,"MaxHeatSetpoint_x100":3500,"SystemMode":4,"Error22":0,"AutoCoolingSetpoint_x100_a":2100,"HeatingControl":1,"Error24":0,"Error25":0,"MinCoolSetpoint_x100":500,"Schedule":"7201010000010500350000000301040027001000060035000500350005000100000001018000000001ff010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","LocalTemperature_x100":2850,"Error30":0,"Error31":0,"Error32":0,"SystemMode_a":4,"CloudySetpoint_x100":0,"PairedTRVShortID":"FFFFFFFFFFFFFFFFFFFFFFFF","CoolingControl":0,"HeatingSetpoint_x100":2100,"AutoHeatingSetpoint_x100":2100,"RunningState":0,"RunningMode":0,"PairedWCNumber":102,"ScheduleType":1,"HoldType":0,"OUTSensorProbe":0,"TimeFormat24Hour":1,"MinHeatSetpoint_x100":500,"MaxCoolSetpoint_x100":3500,"MinCoolSetpoint_x100_a":500,"CoolingSetpoint_x100_a":2100,"HoldType_a":0,"LockKey_a":0,"TemperatureDisplayMode":0},"sIT600I":{"CommandResponse_d":"42323000"},"status":"success"}]}

Got callback for device id: 001e5e09025f4c40
DEBUG:pyit600:Refreshed 1 climate devices
All climate devices:
{'001e5e09025f4c40': ClimateDevice(available=True, name='SQ610RF  Quantum rumtermostat 1', unique_id='001e5e09025f4c40', temperature_unit='°C', precision=0.5, current_temperature=28.5, target_temperature=21.0, max_temp=35.0, min_temp=5.0, hvac_mode='heat', hvac_action='idle', hvac_modes=['off', 'heat'], preset_mode='Follow Schedule', preset_modes=['Follow Schedule', 'Permanent Hold', 'Off'], supported_features=17, device_class='temperature', data={'Endpoint': 9, 'DeviceType': 100, 'UniID': '001e5e09025f4c40'})}
Climate device 001e5e09025f4c40 status:
ClimateDevice(available=True, name='SQ610RF  Quantum rumtermostat 1', unique_id='001e5e09025f4c40', temperature_unit='°C', precision=0.5, current_temperature=28.5, target_temperature=21.0, max_temp=35.0, min_temp=5.0, hvac_mode='heat', hvac_action='idle', hvac_modes=['off', 'heat'], preset_mode='Follow Schedule', preset_modes=['Follow Schedule', 'Permanent Hold', 'Off'], supported_features=17, device_class='temperature', data={'Endpoint': 9, 'DeviceType': 100, 'UniID': '001e5e09025f4c40'})
Setting heating device 001e5e09025f4c40 temperature to 21 degrees celsius
DEBUG:pyit600:Gateway request: POST http://192.168.1.122:80/deviceid/write
{"requestAttr": "write", "id": [{"data": {"Endpoint": 9, "DeviceType": 100, "UniID": "001e5e09025f4c40"}, "sIT600TH": {"SetHeatingSetpoint_x100": 2100}}]}

DEBUG:pyit600:Gateway response:
{"status":"success","id":[{"status":"success","data":{"Devicetype":100,"Endpoint":9,"UniID":"001e5e09025f4c40\t"}}]}

kenn

#### @jvitkauskas commented at 2020-09-15T17:18:09Z

@dyrvigk Try adding custom component from my fork to home assistant https://github.com/jvitkauskas/homeassistant_salus

You might need to create `custom_components` folder if it does not exist in `/config`

#### @dyrvigk commented at 2020-09-15T19:27:01Z

now it works  in homeassistant 

do yoy know if it is possibel to get battery status and maby also humidity  read and how 

i will now try to se if the salus vs20wrf  also works also salus same function exatly as the other but with 4 aaa batteries instead of rechargeable 

thanks a lot 
kenn

#### @dyrvigk commented at 2020-09-15T19:58:04Z

other one also working 

#### @d0d0oo commented at 2020-09-15T21:56:21Z

> 
> 
> I recommend not using UGE600 website as it sends unencrypted requests which backend does not understand. Furthermore, I think the gateway strategy is to delay and not to send any response on incorrect data, so you might be unnecessarily DDoSing your gateway.
> 
> You are correct that `set_climate_device_mode` is redundant. I have included it just because home assistant API has a similar method.
> 
> Did that strange error occur when you have visited UGE600 website?

I would have to make some all day tests with that error. I think it occurs even if do not access UGE600 website, but... I will have to try again.

Strange thing is I added printing some fields from "th" object just before place where error occurs and values were correct despite the error.

As far as "set_climate_device_mode" is concerned I have mentioned that the state of thermostat action/mode is not displayed correctly in HA. I think this method could be for forcing thermostat to start heating or not. In TS600 I recognized two fields representing this state:

- "RunningState" (128 is off, 129 is heating)
- "RunningMode" (0 is off, 2(?) is heating)

This is a place which could be corrected in integration with HA with this model.

#### @jvitkauskas commented at 2020-09-16T20:55:07Z

Sorry, didn't see your message. I have fixed RunningState in version 0.0.6. So you can update that in manifest.json or use newer file(s) from my fork https://github.com/jvitkauskas/homeassistant_salus

#### @dyrvigk commented at 2020-09-16T21:09:46Z

Thanks

i will try that

kenn

<https://www.avast.com/sig-email?utm_medium=email&utm_source=link&utm_campaign=sig-email&utm_content=webmail>
Virusfri.
www.avast.com
<https://www.avast.com/sig-email?utm_medium=email&utm_source=link&utm_campaign=sig-email&utm_content=webmail>
<#DAB4FAD8-2DD7-40BB-A1B8-4E2AA1F9FDF2>

Em qua., 16 de set. de 2020 às 22:55, Julius Vitkauskas <
notifications@github.com> escreveu:

> Sorry, didn't see your message. I have fixed RunningState in version
> 0.0.6. So you can update that in manifest.json or use newer file(s) from my
> fork https://github.com/jvitkauskas/homeassistant_salus
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/jvitkauskas/pyit600/issues/3#issuecomment-693660164>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AG7RHTFDNZJOC26AJ6MATL3SGEQ3VANCNFSM4RAQ3PXQ>
> .
>


#### @jvitkauskas commented at 2020-09-17T23:17:07Z

@dyrvigk does Salus app show humidity and battery status?

#### @dyrvigk commented at 2020-09-18T10:22:09Z

hi
yes it does

kenn

Em sex., 18 de set. de 2020 às 01:17, Julius Vitkauskas <
notifications@github.com> escreveu:

> @dyrvigk <https://github.com/dyrvigk> does Salus app show the humidity
> and battery status?
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/jvitkauskas/pyit600/issues/3#issuecomment-694549634>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AG7RHTHVWNFUHW6BEPBDZBTSGKKIFANCNFSM4RAQ3PXQ>
> .
>


#### @jvitkauskas commented at 2020-10-03T17:03:22Z

@dyrvigk can you provide me the output and write down the corresponding humidity and battery status? I need several samples to be able to compare the data and find out where it does report it.

#### @dyrvigk commented at 2020-10-10T07:02:38Z

Hi sorry that i dident get back to you on this work has been holding me up i will come back to you later if that is ok 

kenn

---

## #1: Home Assistant support

- URL: https://github.com/epoplavskis/pyit600/issues/1
- State: closed
- Author: @mindvisionro
- Created: 2020-05-02T09:58:23Z
- Updated: 2020-06-24T11:39:33Z
- Labels: bug, enhancement

### Issue body

Hello, congratulations on your efforts!  Everything you have done so far is very helpful, I have been trying for a long time to integrate this system in the home assistant.  I own the salus system with thermostats vs30 do you think they can be integrated in the home assistant?

### Conversation

#### @mindvisionro commented at 2020-05-04T19:04:57Z

> 
> 
> Hello, congratulations on your efforts! Everything you have done so far is very helpful, I have been trying for a long time to integrate this system in the home assistant. I own the salus system with thermostats vs30 do you think they can be integrated in the home assistant?

>main.py --host ip --euid euid
DEBUG:pyit600:Trying to connect to gateway at id
All climate devices:
{}

It seems is doesn't see my thermostats :(

#### @jvitkauskas commented at 2020-05-05T22:05:28Z

Hi, I was also working on Home Assistant, but didn't have time to finish it.

There might be some differences as I have VS20WRF/VS20BRF thermostats.

You can try playing with this filter in case it just filters out your thermostats:
https://github.com/jvitkauskas/pyit600/blob/003b18ec48720f07f1e573516bdcbc62203ccfef/pyit600/gateway.py#L112

Alternatively you can try sending me the data which is returned in "all_devices" variable for your system here: https://github.com/jvitkauskas/pyit600/blob/003b18ec48720f07f1e573516bdcbc62203ccfef/pyit600/gateway.py#L67

To get it just add `print(repr(all_devices))` or something like that below that line and you should be able to see it then.

You can mail me if you are not comfortable posting it here and/or you can edit some possibly sensitive data (mac addresses?) if you want.

#### @jvitkauskas commented at 2020-06-24T11:38:44Z

Hi, it seems I have forgot to include `await gateway.poll_status()` in the demo. It is added now. Also someone has created homeassistant plugin https://github.com/konradb3/homeassistant_salus 
