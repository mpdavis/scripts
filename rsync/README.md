# Rsync Webhook Service

A lightweight webhook service that triggers rsync commands. Built with Flask and includes request queuing to prevent concurrent rsync executions.

## Features

- Simple HTTP webhook endpoint for triggering rsync
- Request queuing (prevents multiple simultaneous rsync operations)
- Status endpoint for monitoring
- Logging to file and console

## Configuration

Edit `config.py` to customize:

- **RSYNC_COMMAND**: The rsync command to execute (modify source/destination paths)
- **HOST/PORT**: Web server binding (default: 0.0.0.0:8080)
- **LOG_FILE/LOG_LEVEL**: Logging configuration

Example rsync command:
```python
RSYNC_COMMAND = [
    'rsync',
    '-avz',
    '--delete',
    '/source/path/',
    'user@remote:/destination/path/'
]
```

## Installation and Setup

### Quick Start (Development)

Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the service:
```bash
python webhook.py
```

### Production Installation (systemd service)

For production use, install as a systemd service for automatic startup and restarts:

```bash
# See INSTALL.md for detailed instructions
sudo cp rsync-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rsync-webhook
sudo systemctl start rsync-webhook
```

**See [INSTALL.md](INSTALL.md) for complete installation and service management instructions.**

## API Endpoints

### POST /webhook
Triggers an rsync operation. Queues the request if rsync is already running.

**Request:**
```bash
curl -X POST http://localhost:8080/webhook
```

**Response:**
```json
{
  "success": true,
  "message": "Rsync task queued",
  "task": {
    "task_id": 1,
    "timestamp": "2025-12-10T12:00:00",
    "status": "queued"
  },
  "queue_size": 1
}
```

### GET /status
Get current service status and queue information.

**Request:**
```bash
curl http://localhost:8080/status
```

**Response:**
```json
{
  "current_task": {
    "task_id": 1,
    "status": "running",
    "timestamp": "2025-12-10T12:00:00"
  },
  "queue_size": 0,
  "total_tasks_processed": 5
}
```

### GET /health
Health check endpoint.

**Request:**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Integration Examples

### Trigger from another service
```bash
# Simple POST request
curl -X POST http://your-server:8080/webhook

# From a cron job
*/30 * * * * curl -X POST http://localhost:8080/webhook

# From a script
#!/bin/bash
response=$(curl -s -X POST http://localhost:8080/webhook)
echo "Rsync triggered: $response"
```

### Using with other automation tools
```yaml
# GitHub Actions example
- name: Trigger rsync webhook
  run: |
    curl -X POST http://your-server:8080/webhook
```

## Logging

Logs are written to:
- Console (stdout/stderr)
- `rsync_webhook.log` file

Logs include:
- Webhook requests received
- Task queue status
- Rsync command execution details
- Success/failure results

## Production Considerations

Since this webhook has no authentication, consider:

1. **Network isolation**: Run in a trusted network or VPN
2. **Firewall rules**: Restrict access to known IPs
3. **Reverse proxy**: Use nginx/Caddy with SSL (recommended)

## Troubleshooting

**Rsync fails with permission errors:**
- Ensure the process has access to source/destination paths
- Check file permissions and ownership

**SSH key not working:**
- Check SSH key permissions (should be 600 for private keys)
- Test SSH connection manually first
- Ensure SSH keys are in the correct location (~/.ssh/)

**Webhook not responding:**
- Check if the service is running: `ps aux | grep webhook`
- Verify the port is accessible: `curl http://localhost:8080/health`
- Check logs: `tail -f rsync_webhook.log`
