#!/usr/bin/env python
"""
Trigger Rsync Webhook

Script to trigger the rsync webhook service.
Designed to be called from qBittorrent when a torrent completes.

Logs are written to ~/trigger_rsync.log

Usage:
    python trigger_rsync.py

qBittorrent integration:
    Tools > Options > Downloads > Run external program on torrent completion:
    /path/to/scripts/seedbox/trigger_rsync.py "%N" "%L" "%F"
"""

from __future__ import print_function
import sys
import os
import logging
from datetime import datetime

# Configuration
WEBHOOK_URL = "https://home.mpdavis.com/sync/webhook"
LOG_FILE = os.path.expanduser("~/trigger_rsync.log")

# For Python 2.7/3.x compatibility
try:
    # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # Python 2
    from urllib2 import Request, urlopen, URLError, HTTPError


def setup_logging():
    """Configure logging to write to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def trigger_webhook(torrent_name=None, category=None, save_path=None):
    """Trigger the rsync webhook."""

    logging.info("=" * 60)
    logging.info("Triggering rsync webhook")

    if torrent_name:
        logging.info("Torrent name: {}".format(torrent_name))
    if category:
        logging.info("Category: {}".format(category))
    if save_path:
        logging.info("Save path: {}".format(save_path))

    logging.info("Webhook URL: {}".format(WEBHOOK_URL))

    try:
        request = Request(WEBHOOK_URL)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'

        response = urlopen(request, timeout=10)
        response_data = response.read().decode('utf-8')

        logging.info("SUCCESS: Webhook triggered successfully")
        logging.info("Response: {}".format(response_data))
        logging.info("=" * 60)
        return 0

    except HTTPError as e:
        logging.error("HTTP Error {}".format(e.code))
        logging.error("Response: {}".format(e.read().decode('utf-8')))
        logging.info("=" * 60)
        return 1

    except URLError as e:
        logging.error("Failed to reach webhook server")
        logging.error("Reason: {}".format(e.reason))
        logging.info("=" * 60)
        return 1

    except Exception as e:
        logging.error("Unexpected error")
        logging.error("Error: {}".format(str(e)))
        logging.info("=" * 60)
        return 1


def main():
    """Main function to handle command line arguments."""

    # Set up logging
    setup_logging()

    # qBittorrent passes these parameters:
    # %N - Torrent name
    # %L - Category
    # %F - Content path (same as root path for multifile torrent)
    # %R - Root path (first torrent subdirectory path)
    # %D - Save path
    # %C - Number of files
    # %Z - Torrent size (bytes)
    # %T - Current tracker
    # %I - Info hash

    torrent_name = sys.argv[1] if len(sys.argv) > 1 else None
    category = sys.argv[2] if len(sys.argv) > 2 else None
    save_path = sys.argv[3] if len(sys.argv) > 3 else None

    return trigger_webhook(torrent_name, category, save_path)


if __name__ == "__main__":
    sys.exit(main())
