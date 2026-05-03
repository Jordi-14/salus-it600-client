# Upstream Issues Status

Companion status matrix for [upstream-issues.md](upstream-issues.md).

`upstream-issues.md` is an exported historical record from
`epoplavskis/pyit600`. Keep that export intact. Use this file for local
maintainer tracking.

Last reviewed: 2026-05-02.

## Status Labels

- `Solved locally`: fixed in `salus-it600-client`.
- `Closed upstream`: the exported upstream issue is already closed.
- `Backlog`: still open upstream and not confirmed fixed here.
- `Needs verification`: code may cover the case, but the exact issue report has
  not been retested.
- `Not actionable`: question, sale, ownership, or historical note.

## Status Matrix

| Issue | Upstream state | Local status | Notes |
| --- | --- | --- | --- |
| [#48 UG800 stopped working after firmware update](https://github.com/epoplavskis/pyit600/issues/48) | open | Backlog | New UG800 firmware report; needs protocol validation. |
| [#47 UG800 stopped working after firmware update](https://github.com/epoplavskis/pyit600/issues/47) | closed | Closed upstream | Duplicate or abandoned report. |
| [#46 Compatibility with UG800](https://github.com/epoplavskis/pyit600/issues/46) | open | Needs verification | Current client has newer protocol support, but this report needs real UG800 firmware validation. |
| [#45 Is a gateway required?](https://github.com/epoplavskis/pyit600/issues/45) | open | Not actionable | General product/architecture question. |
| [#44 Problem with Salus FC600NH](https://github.com/epoplavskis/pyit600/issues/44) | open | Solved locally | FC600NH setpoint write rejection; separate from FC600 fan mode. Told user to try our fork and tell us if it works there. |
| [#43 Smoke sensors are not seen as binary_sensors](https://github.com/epoplavskis/pyit600/issues/43) | open | Needs verification | Current parser handles `sIASZS` binary devices, but this exact smoke report needs retesting. Told the user to test our fork and make a PR there. |
| [#41 Debugging gateway communication error](https://github.com/epoplavskis/pyit600/issues/41) | open | Backlog | Gateway read/connect failure. |
| [#40 Can KL08RF output be controlled?](https://github.com/epoplavskis/pyit600/issues/40) | open | Backlog | Command support not implemented. |
| [#39 HA not controlling Salus Thermostats](https://github.com/epoplavskis/pyit600/issues/39) | closed | Closed upstream | Historical. |
| [#38 Notice of transfer of ownership](https://github.com/epoplavskis/pyit600/issues/38) | closed | Not actionable | Project ownership note. |
| [#37 Selling my Salus devices on eBay](https://github.com/epoplavskis/pyit600/issues/37) | closed | Not actionable | Personal sale note. |
| [#36 Maintainer wanted](https://github.com/epoplavskis/pyit600/issues/36) | closed | Not actionable | Historical maintenance note. |
| [#35 Selling my Salus devices on eBay](https://github.com/epoplavskis/pyit600/issues/35) | closed | Not actionable | Personal sale note. |
| [#34 SyntaxError: async with outside async function](https://github.com/epoplavskis/pyit600/issues/34) | closed | Closed upstream | User resolved by using the correct entrypoint. |
| [#32 Unable to write fan mode to UGE600 for FC600 device](https://github.com/epoplavskis/pyit600/issues/32) | open | Solved locally | Fixed in `salus-it600-client 0.4.6`: FC600 fan mode writes now use `sFanS.SetFanMode`. Told the user to try our fork. |
| [#31 Salus SQ610(WB) SmartThings device handler](https://github.com/epoplavskis/pyit600/issues/31) | closed | Not actionable | SmartThings request, outside this client scope. |
| [#30 Integration of pyit600 to fhem is also available](https://github.com/epoplavskis/pyit600/issues/30) | closed | Not actionable | Integration announcement. |
| [#28 Support for AWRT10RT thermostat, wiring center](https://github.com/epoplavskis/pyit600/issues/28) | open | Backlog | Device support request. |
| [#27 Support for ECM600](https://github.com/epoplavskis/pyit600/issues/27) | open | Backlog | Electric monitor support request. Told the user to test our fork. |
| [#26 SQ610 works!](https://github.com/epoplavskis/pyit600/issues/26) | closed | Closed upstream | Positive report/historical reference. |
| [#25 EUID seems invalid](https://github.com/epoplavskis/pyit600/issues/25) | closed | Closed upstream | Historical EUID troubleshooting. |
| [#21 Upstreaming into HA](https://github.com/epoplavskis/pyit600/issues/21) | closed | Not actionable | Historical project direction. |
| [#20 ITG500/IT500 request/investigation](https://github.com/epoplavskis/pyit600/issues/20) | closed | Closed upstream | Historical investigation. |
| [#16 Humidity and battery stats from SQ610RF](https://github.com/epoplavskis/pyit600/issues/16) | open | Needs verification | Current client exposes several SQ610 humidity/battery paths, but the old report needs retesting. |
| [#15 OS600](https://github.com/epoplavskis/pyit600/issues/15) | closed | Closed upstream | Historical device request. |
| [#11 Support a new device SPE600](https://github.com/epoplavskis/pyit600/issues/11) | closed | Closed upstream | SPE600 support exists in current device parsing. |
| [#7 FC600 users wanted](https://github.com/epoplavskis/pyit600/issues/7) | closed | Closed upstream | Historical data-gathering issue. |
| [#3 Gateway rejected read deviceid empty list](https://github.com/epoplavskis/pyit600/issues/3) | closed | Closed upstream | Historical protocol issue. |
| [#1 Home Assistant support](https://github.com/epoplavskis/pyit600/issues/1) | closed | Closed upstream | Historical integration bootstrap issue. |

## Cross-Repo Links

- Client issue #32 corresponds to Home Assistant integration issue
  `epoplavskis/homeassistant_salus#46`.
- The client fix is released in `salus-it600-client 0.4.6`.
- Home Assistant should consume the fix by requiring
  `salus-it600-client==0.4.6` or newer.
