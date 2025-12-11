# Scripts

A collection of utility scripts for use across home network and hosted servers.

## Environment

- Scripts are run on my FeralHosting VPS slot. 
- Python 2.7 is already installed and should be preferred.
- 

## Available Scripts

### stats.py

Collects server statistics and outputs them to JSON for HTTP serving.

**Collected metrics:**
- Disk usage (home directory and mountpoint stats)

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

**Usage:**
```bash
# Use default output file (server_stats.json)
python stats.py

# Specify custom output path
python stats.py -o /var/www/html/stats.json
python stats.py --output /path/to/custom.json
```

**Automated updates:**
Add to crontab for periodic updates:
```bash
# Update every 5 minutes to default location
*/5 * * * * cd /path/to/scripts && python stats.py

# Update to web server directory
*/5 * * * * cd /path/to/scripts && python stats.py -o /var/www/html/stats.json
```

## Contributing

This is a personal utility repository. Add scripts as needed, keeping them simple and self-contained.
