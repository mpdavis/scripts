# Scripts

A collection of utility scripts and services for home network automation and server management.

## Repository Structure

This repository is organized into separate Python packages, each with its own dependencies and documentation:

```
scripts/
├── seedbox/        # Seedbox statistics collection (Python 2.7/3.x)
└── rsync/          # Rsync webhook service (Python 3.x)
```

## Packages

### seedbox

Utilities for FeralHosting VPS seedbox automation and monitoring.

**Features:**
- Disk usage statistics collection (stats.py)
- qBittorrent webhook trigger for rsync (trigger_rsync.py)
- JSON output for HTTP serving
- Python 2.7 and 3.x compatible

**Quick start:**
```bash
cd seedbox
pip install -r requirements.txt

# Collect stats
python stats.py

# Configure qBittorrent to trigger rsync on completion
# The webhook URL is pre-configured as https://rsync.mpdavis.com/webhook
# Add to qBittorrent: Tools > Options > Downloads > Run external program:
# /path/to/seedbox/trigger_rsync.py "%N" "%L" "%F"
```

See [seedbox/README.md](seedbox/) for detailed documentation.

---

### rsync

Lightweight webhook service for triggering rsync commands with request queuing.

**Features:**
- HTTP webhook endpoint for triggering rsync
- Request queuing (prevents concurrent operations)
- Status monitoring endpoints
- Python 3.x only

**Quick start:**
```bash
cd rsync

# Edit config.py to set your rsync command
pip install -r requirements.txt
python webhook.py

# For production: install as systemd service (see rsync/INSTALL.md)
sudo systemctl enable rsync-webhook
sudo systemctl start rsync-webhook
```

See [rsync/README.md](rsync/) and [rsync/INSTALL.md](rsync/INSTALL.md) for detailed documentation.

---

## Development

Each package is self-contained with its own:
- `requirements.txt` - Python dependencies
- `README.md` - Package-specific documentation
- `__init__.py` - Package initialization

## Contributing

This is a personal utility repository. Add new packages and scripts as needed, keeping them modular and self-contained.
