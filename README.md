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
```bash
                               ...:..:.:::.:..:...                                
                      .:.: REAL-TIME RESOURCES MONITOR :.:.                       
                             (Refresh rate is 1000ms)                             

 |    ↑ Packets |    ↓ Packets |     ↑ Bytes |     ↓ Bytes |      CPU |   Memory | 
 | ------------ | ------------ | ----------- | ----------- | -------- | -------- | 
 |     12.51k ▼ |       453  ▲ |    1.9 MB ▼ |  569.0 B  ▲ |  25.3% ▲ |  41.8% ▼ | 
```

---

### Prerequisites
- [python 3](https://www.python.org/) (`apt-get install python3` on Linux) 
- [pip](https://pypi.org/project/pip/) (`apt-get install python3-pip` on Linux)
- [psutil](https://pypi.org/project/psutil/) - `pip3 install psutil`

> Note. In this guide `python3` and `pip3` commands are used.
> However, if your system says that there is no such commands
> despite you installed them, try `python` and `pip` instead.

---

### Installation
```bash
curl https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py > monitor.py
```

---

### Usage
```bash
python3 monitor.py
```
or
```bash
python3 monitor.py [OPTIONS]
```

---

### Options
- `-r MILLISECONDS, --rate MILLISECONDS` - custom refresh rate, 1000ms by default.
The refresh rate is displayed under the logo, if not in tiny mode.
- `-t, --tiny` - hide the logo so the output takes less space.
Is useful if you have multiple instances running
and want to save the screen space.
- `-f, --fancy` - enable colorful output. 
Statically colored logo.
Dynamically colored metrics of CPU and Memory: 
become red of above 85%, yellow - above 65%, else - white.
- `-b, --bits` - show in/out traffic in bits instead of bytes.
Technically multiplies the shown value by 8.
- `-u, --update` - tries to fetch the script from the repo, 
if there is a newer version available.  
Allows to make a backup of your current file before updating.  
Also, if your file up-to-date, but its content somehow
differs from the repo, you can roll back the changes,  
and optionally make a backup of your local changes before the rollback.

---

### Convenience
Optionally, you may create an alias for running the script:  
```bash
alias monitor="python3 monitor.py"
```  
So the script could be run as following:  
```bash
monitor
```   
More info on aliases and making them permanent here: https://linuxize.com/post/how-to-create-bash-aliases/
