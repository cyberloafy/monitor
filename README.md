### Brief
**Monitor is a lightweight minimalistic 
console application for monitoring your device' 
resources usage in real-time. It tracks:**
> - `↑ Packets` `(Δ)`
> - `↓ Packets` `(Δ)`
> - `↑ Bytes` `(Δ)`
> - `↓ Bytes` `(Δ)`
> - `CPU`
> - `Memory`

- `(Δ)` - shown as `unit/refresh-rate-in-seconds`  
- `↑` - sent  
- `↓` - received  

---

### Appearance
```shell
                               ...:..:.:::.:..:...                                
                      .:.: REAL-TIME RESOURCES MONITOR :.:.                       
                             (Refresh rate is 1000ms)                             

 |    ↑ Packets |    ↓ Packets |     ↑ Bytes |     ↓ Bytes |      CPU |   Memory | 
 | ------------ | ------------ | ----------- | ----------- | -------- | -------- | 
 |     12.51k ▼ |       453  ▲ |    1.9 MB ▼ |  569.0 B  ▲ |  25.3% ▲ |  41.8% ▼ | 
```

---

### Installation
The script may be run on any device, that can run [python3](https://www.python.org/)  

Save the content of [monitor.py](https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py) 
to a file (named monitor.py if you wish) and run as shown in Usage section.

To download the file via terminal you may use:
```shell
$ curl https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py > monitor.py
```
(Should work on Linux, MacOS, and Windows 10)

Then install the requirement:
```shell
$ pip install psutil
```

---

### Usage
```shell
$ python3 monitor.py
```
#### Custom refresh rate
```shell
$ python3 monitor.py -r MILLISECONDS
```
e.g.
```shell
$ python3 monitor.py -r 500
```

---

### Convenience
Optionally, you may create an alias for running the script:  
```shell
alias monitor="python3 monitor.py"
```  
So the script could be run as following:  
```shell
$ monitor
```   
More info on aliases and making them permanent here: https://linuxize.com/post/how-to-create-bash-aliases/
