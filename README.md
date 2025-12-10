# Scripts

A collection of utility scripts for use across home network and hosted servers.

## Available Scripts

### stats.py

Collects server statistics and outputs them to JSON for HTTP serving.

**Collected metrics:**
- System info (hostname, platform, uptime)
- CPU usage and details
- Memory and swap usage
- Disk usage and I/O
- Network statistics
- Load averages

**Requirements:**
- Python 2.7 or Python 3.x
- psutil library

**Setup:**

For Python 2.7:
```bash
pip install 'psutil>=5.6.0,<6.0.0'
python stats.py
```

For Python 3.x:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python stats.py
```

**Output:**
Generates `server_stats.json` in the current directory.

**Automated updates:**
Add to crontab for periodic updates:
```bash
*/5 * * * * cd /path/to/scripts && python stats.py
```

## Contributing

This is a personal utility repository. Add scripts as needed, keeping them simple and self-contained.
