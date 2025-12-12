#!/usr/bin/env python
"""
Trigger Rsync Webhook

Script to trigger the rsync webhook service.
Designed to be called from qBittorrent when a torrent completes.

Usage:
    python trigger_rsync.py

qBittorrent integration:
    Tools > Options > Downloads > Run external program on torrent completion:
    /path/to/scripts/seedbox/trigger_rsync.py "%N" "%L" "%F"
"""

from __future__ import print_function
import sys
import os

# Configuration
WEBHOOK_URL = "https://home.mpdavis.com/sync/webhook"

# For Python 2.7/3.x compatibility
try:
    # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # Python 2
    from urllib2 import Request, urlopen, URLError, HTTPError


def trigger_webhook(torrent_name=None, category=None, save_path=None):
    """Trigger the rsync webhook."""

    print("=" * 60)
    print("Triggering rsync webhook")
    print("=" * 60)

    if torrent_name:
        print("Torrent name: {}".format(torrent_name))
    if category:
        print("Category: {}".format(category))
    if save_path:
        print("Save path: {}".format(save_path))

    print("Webhook URL: {}".format(WEBHOOK_URL))
    print("-" * 60)

    try:
        request = Request(WEBHOOK_URL)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'

        response = urlopen(request, timeout=10)
        response_data = response.read().decode('utf-8')

        print("SUCCESS: Webhook triggered successfully")
        print("Response: {}".format(response_data))
        print("=" * 60)
        return 0

    except HTTPError as e:
        print("ERROR: HTTP Error {}".format(e.code))
        print("Response: {}".format(e.read().decode('utf-8')))
        print("=" * 60)
        return 1

    except URLError as e:
        print("ERROR: Failed to reach webhook server")
        print("Reason: {}".format(e.reason))
        print("=" * 60)
        return 1

    except Exception as e:
        print("ERROR: Unexpected error")
        print("Error: {}".format(str(e)))
        print("=" * 60)
        return 1


def main():
    """Main function to handle command line arguments."""

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
