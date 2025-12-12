# Installation as a System Service

This guide explains how to run the rsync webhook as a systemd service that starts automatically on boot and restarts on failure.

## Prerequisites

- Linux system with systemd (most modern distributions)
- Python 3.x installed
- sudo/root access

## Standard Installation Location

The recommended location is **`/opt/scripts/rsync/`** which follows the Filesystem Hierarchy Standard (FHS) for third-party applications. This allows you to manage updates via git pull rather than copying files.

## Installation Steps

### 1. Clone repository to /opt

```bash
# Clone the repository directly to /opt
sudo git clone https://github.com/mpdavis/scripts.git /opt/scripts

# Set ownership to your user
sudo chown -R $USER:$USER /opt/scripts

# Navigate to rsync webhook directory
cd /opt/scripts/rsync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 2. Configure the webhook

Edit `config.py` to set your rsync command:

```python
RSYNC_COMMAND = [
    'rsync',
    '-avz',
    '--delete',
    '/source/path/',
    'user@remote:/destination/path/'
]
```

### 3. Create log directory

```bash
sudo mkdir -p /var/log/rsync-webhook
sudo chown $USER:$USER /var/log/rsync-webhook
```

### 4. Configure the systemd service

Edit `rsync-webhook.service` and update the username:

- Replace `YOUR_USERNAME` with your actual username (both User and Group)

The paths should point to `/opt/scripts/rsync/` location.

**Example:**
```ini
User=michael
Group=michael
WorkingDirectory=/opt/scripts/rsync
Environment="PATH=/opt/scripts/rsync/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/scripts/rsync/venv/bin/python webhook.py
```

If you chose a different installation path, update WorkingDirectory, Environment PATH, and ExecStart accordingly.

### 5. Install the service

```bash
# Create symlink to service file in systemd directory
sudo ln -s /opt/scripts/rsync/rsync-webhook.service /etc/systemd/system/rsync-webhook.service

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable rsync-webhook

# Start the service now
sudo systemctl start rsync-webhook
```

**Note:** Using a symlink instead of copying allows you to update the service file via git pull without manually copying it again.

## Managing the Service

### Check service status
```bash
sudo systemctl status rsync-webhook
```

### Start the service
```bash
sudo systemctl start rsync-webhook
```

### Stop the service
```bash
sudo systemctl stop rsync-webhook
```

### Restart the service
```bash
sudo systemctl restart rsync-webhook
```

### View logs
```bash
# Live tail of logs
sudo journalctl -u rsync-webhook -f

# Or view the log files directly
tail -f /var/log/rsync-webhook/webhook.log
tail -f /var/log/rsync-webhook/webhook-error.log
```

### Disable auto-start on boot
```bash
sudo systemctl disable rsync-webhook
```

## Testing

After starting the service, test it:

```bash
# Check service is running
sudo systemctl status rsync-webhook

# Test health endpoint
curl http://localhost:8080/sync/health

# Trigger webhook
curl -X POST http://localhost:8080/sync/webhook

# Check logs
sudo journalctl -u rsync-webhook -n 50
```

## Troubleshooting

### Service fails to start

Check the logs:
```bash
sudo journalctl -u rsync-webhook -n 100
```

Common issues:
- **Wrong paths**: Verify WorkingDirectory and ExecStart in the service file
- **Permission issues**: Ensure the user has access to the working directory
- **Port already in use**: Check if port 8080 is available (`sudo ss -tlnp | grep 8080`)
- **Missing dependencies**: Ensure Flask is installed in the venv

### Service crashes and doesn't restart

The service is configured to restart automatically with `Restart=always`. Check:
```bash
sudo systemctl status rsync-webhook
sudo journalctl -u rsync-webhook -n 100
```

### Can't access webhook from network

- Check firewall: `sudo ufw status` (allow port 8080 if needed)
- Verify the service is listening: `sudo ss -tlnp | grep 8080`
- Check reverse proxy configuration

## Updating the Service

When updates are pushed to the repository:

```bash
# Navigate to the repository
cd /opt/scripts

# Pull the latest changes
git pull

# If dependencies changed, update them
cd rsync
source venv/bin/activate
pip install -r requirements.txt
deactivate

# If the service file was modified, reload systemd
sudo systemctl daemon-reload

# Restart the service to apply changes
sudo systemctl restart rsync-webhook

# Verify it's running
sudo systemctl status rsync-webhook
```

**Quick update (most common case):**
```bash
cd /opt/scripts && git pull && sudo systemctl restart rsync-webhook
```

## Uninstalling

```bash
# Stop and disable the service
sudo systemctl stop rsync-webhook
sudo systemctl disable rsync-webhook

# Remove service file
sudo rm /etc/systemd/system/rsync-webhook.service

# Reload systemd
sudo systemctl daemon-reload
```

## Standard Installation Locations

Different paths you might see and when to use them:

| Path | Use Case | Notes |
|------|----------|-------|
| `/opt/scripts/rsync/` | **Recommended** - Production system service | Cloned from git, easy updates via pull |
| `/opt/rsync-webhook/` | Alternative - copied files | Standard for third-party apps, manual updates |
| `/usr/local/lib/rsync-webhook/` | Alternative production location | For locally compiled/installed software |
| `/home/user/scripts/rsync/` | Development or personal use | Not ideal for system services |
| `/srv/rsync-webhook/` | Service data directory | Sometimes used for web services |

For a production webhook service with git-based updates, **`/opt/scripts/rsync/`** is the recommended choice.

## Alternative: Running with Screen/tmux (Not Recommended)

If you don't have systemd access, you can run the webhook in screen/tmux:

```bash
# Using screen
screen -S rsync-webhook
cd /opt/scripts/rsync
source venv/bin/activate
python webhook.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r rsync-webhook
```

However, this won't auto-restart on failure or survive system reboots.
