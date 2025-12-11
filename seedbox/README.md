# Seedbox Utilities

Collection of utilities for seedbox automation and monitoring.

## Scripts

### stats.py

Collects seedbox server statistics and outputs them to JSON for HTTP serving.

**Features:**
- Disk usage tracking (home directory and mountpoint stats)
- JSON output format
- Python 2.7 and 3.x compatible
- Configurable output path
- Designed for FeralHosting VPS environments

### trigger_rsync.py

Triggers the rsync webhook service (from the `rsync` package) to sync files.

**Features:**
- Python 2.7 and 3.x compatible
- Designed for qBittorrent integration
- Simple HTTP POST to webhook
- Logging of torrent information

## Requirements

- Python 2.7 or Python 3.x
- psutil library

## Installation

For Python 2.7 (FeralHosting VPS):
```bash
pip install 'psutil>=5.6.0,<6.0.0'
```

For Python 3.x:
```bash
pip install -r requirements.txt
```

Or with a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Basic usage with default output:
```bash
python stats.py
```

This creates `server_stats.json` in the current directory.

Specify custom output path:
```bash
python stats.py -o /var/www/html/stats.json
python stats.py --output /path/to/custom.json
```

## Automated Updates

Add to crontab for periodic updates:

```bash
# Update every 5 minutes to default location
*/5 * * * * cd /path/to/scripts/seedbox && python stats.py

# Update to web server directory
*/5 * * * * cd /path/to/scripts/seedbox && python stats.py -o /var/www/html/stats.json
```

## Output Format

Example output:
```json
{
  "timestamp": "2025-12-10T12:00:00.000000",
  "disk": {
    "home_directory": {
      "path": "/home/username",
      "usage": {
        "total_bytes": 107374182400,
        "total_mb": 102400.0,
        "total_gb": 100.0
      }
    }
  }
}
```

## Collected Metrics

- **timestamp**: ISO 8601 formatted timestamp of collection
- **disk.home_directory**: Home directory disk usage
  - `path`: Absolute path to home directory
  - `usage.total_bytes`: Total size in bytes
  - `usage.total_mb`: Total size in megabytes
  - `usage.total_gb`: Total size in gigabytes

## Environment Notes

This script is designed to run on FeralHosting VPS slots where:
- Python 2.7 is the default Python installation
- Limited system permissions (non-root)
- Home directory statistics are most relevant

---

## Rsync Webhook Trigger

The `trigger_rsync.py` script is designed to be called from qBittorrent when torrents complete, triggering an rsync operation via the webhook service.

### Configuration

The webhook URL is configured in `trigger_rsync.py`:

```python
WEBHOOK_URL = "https://rsync.mpdavis.com/webhook"
```

Change this if you're using a different webhook endpoint.

### qBittorrent Setup

1. Open qBittorrent settings: **Tools > Options**
2. Navigate to: **Downloads** tab
3. Enable: **Run external program on torrent completion**
4. Enter the command:

```bash
/path/to/scripts/seedbox/trigger_rsync.py "%N" "%L" "%F"
```

Replace `/path/to/scripts/` with the actual path to your scripts directory.

**Parameters passed to script:**
- `%N` - Torrent name
- `%L` - Category
- `%F` - Content path (file or directory)

### Manual Testing

Test the trigger script manually:

```bash
# Basic test
python trigger_rsync.py

# Test with torrent info
python trigger_rsync.py "Ubuntu-22.04.iso" "Linux" "/downloads/Ubuntu-22.04.iso"
```

### How It Works

1. qBittorrent completes a torrent download
2. qBittorrent runs `trigger_rsync.py` with torrent details
3. Script makes HTTP POST to the rsync webhook
4. Webhook queues an rsync job to sync the files
5. Script logs the result

### Troubleshooting

**Webhook not reachable:**
- Verify the webhook URL in `trigger_rsync.py`
- Check if the rsync webhook service is running
- Test connectivity: `curl https://rsync.mpdavis.com/health`
- Verify reverse proxy is configured correctly

**Script not executing from qBittorrent:**
- Check the script path is correct
- Ensure the script is executable: `chmod +x trigger_rsync.py`
- Check qBittorrent logs for errors

**Permission errors:**
- Ensure qBittorrent user has execute permissions on the script
- Check Python is in the PATH for the qBittorrent user

### Logs

The script outputs to stdout/stderr, which qBittorrent captures in its execution log:

```
============================================================
Triggering rsync webhook
============================================================
Torrent name: Ubuntu-22.04.iso
Category: Linux
Save path: /downloads/Ubuntu-22.04.iso
Webhook URL: https://rsync.mpdavis.com/webhook
------------------------------------------------------------
SUCCESS: Webhook triggered successfully
Response: {"success": true, "message": "Rsync task queued", ...}
============================================================
```
