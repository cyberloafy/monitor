###Brief
**Monitor is a lightweight minimalistic 
console application for monitoring your device' 
resources usage in real-time. It tracks:**
> - `↑ Packets` `(Δ)`
> - `↓ Packets` `(Δ)`
> - `↑ Bytes` `(Δ)`
> - `↓ Bytes` `(Δ)`
> - `CPU`
> - `Memory`

`(Δ)` - shown as `unit/refresh-rate-in-seconds`  
`↑` - sent  
`↓` - received  
---
###Usage
```shell
$ python monitor.py
```
```shell
$ python3 monitor.py
```
---
###Custom refresh rate
```shell
$ python monitor.py -r 500
```
```shell
$ python monitor.py --rate 2000
```