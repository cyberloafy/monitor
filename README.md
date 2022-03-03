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

### Installation
The script requires python 3 to run: https://www.python.org/  

Save the content of [monitor.py](https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py) 
to a file (named monitor.py if you wish) and run as shown in Usage section.

To download the file via terminal you may use:
```shell
$ curl https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py > monitor.py
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
