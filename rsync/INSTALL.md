# Installation as a System Service

This guide explains how to run the rsync webhook as a systemd service that starts automatically on boot and restarts on failure.

## Prerequisites

- Linux system with systemd (most modern distributions)
- Python 3.x installed
- sudo/root access

## Standard Installation Location

The recommended location is **`/opt/rsync-webhook/`** which follows the Filesystem Hierarchy Standard (FHS) for third-party applications.

## Installation Steps

### 1. Install to /opt

```bash
# Create installation directory
sudo mkdir -p /opt/rsync-webhook

# Copy files (from your cloned repository)
sudo cp -r /path/to/scripts/rsync/* /opt/rsync-webhook/

# Set ownership to your user
sudo chown -R $USER:$USER /opt/rsync-webhook

# Navigate to installation directory
cd /opt/rsync-webhook

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

The paths are pre-configured for the standard `/opt/rsync-webhook/` location.

**Example:**
```ini
User=michael
Group=michael
WorkingDirectory=/opt/rsync-webhook
Environment="PATH=/opt/rsync-webhook/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/rsync-webhook/venv/bin/python webhook.py
```

If you chose a different installation path, update WorkingDirectory, Environment PATH, and ExecStart accordingly.

### 5. Install the service

```bash
# Copy service file to systemd directory
sudo cp rsync-webhook.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable rsync-webhook

# Start the service now
sudo systemctl start rsync-webhook
```

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
curl http://localhost:8080/health

# Trigger webhook
curl -X POST http://localhost:8080/webhook

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

When you make changes to the webhook code or configuration:

```bash
# 1. Stop the service
sudo systemctl stop rsync-webhook

# 2. Make your changes
# Edit config.py, webhook.py, etc.

# 3. If you modified the service file:
sudo cp rsync-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload

# 4. Start the service
sudo systemctl start rsync-webhook

# 5. Verify it's running
sudo systemctl status rsync-webhook
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
| `/opt/rsync-webhook/` | **Recommended** - Production system service | Standard for third-party applications |
| `/usr/local/lib/rsync-webhook/` | Alternative production location | For locally compiled/installed software |
| `/home/user/rsync-webhook/` | Development or personal use | Not ideal for system services |
| `/srv/rsync-webhook/` | Service data directory | Sometimes used for web services |

For a production webhook service, **`/opt/rsync-webhook/`** is the most conventional choice.

## Alternative: Running with Screen/tmux (Not Recommended)

If you don't have systemd access, you can run the webhook in screen/tmux:

```bash
# Using screen
screen -S rsync-webhook
cd /opt/rsync-webhook
source venv/bin/activate
python webhook.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r rsync-webhook
```

However, this won't auto-restart on failure or survive system reboots.
