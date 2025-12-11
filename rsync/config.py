"""
Configuration for rsync webhook service.
"""

# Rsync command to execute when webhook is triggered
# Modify this to match your specific rsync needs
RSYNC_COMMAND = [
    'rsync',
    '-avz',  # archive mode, verbose, compress
    '--progress',
    '/path/to/source/',
    '/path/to/destination/'
]

# Web server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8080

# Logging configuration
LOG_FILE = 'rsync_webhook.log'
LOG_LEVEL = 'INFO'
