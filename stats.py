#!/usr/bin/env python2
"""
Server Statistics Collection Script
Collects various system statistics and writes them to a JSON file.
"""

from __future__ import print_function
import argparse
import json
import os
import platform
import socket
import subprocess
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Error: psutil library is required. Install with: pip install psutil")
    exit(1)


def get_cpu_stats():
    """Get CPU statistics."""
    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "count_physical": psutil.cpu_count(logical=False),
        "count_logical": psutil.cpu_count(logical=True),
        "frequency": {
            "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "min": psutil.cpu_freq().min if psutil.cpu_freq() else None,
            "max": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        } if psutil.cpu_freq() else None,
        "per_cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
    }


def get_directory_size(path):
    """Calculate total size of a directory using du command."""
    try:
        # Use du -sB GB for Linux systems
        result = subprocess.Popen(
            ['du', '-sB', 'GB', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = result.communicate()

        # Output format: "123GB /path/to/dir"
        output = stdout.decode().split()[0]
        # Remove 'GB' suffix and convert to float
        size_gb = float(output.rstrip('GB'))
        size_bytes = int(size_gb * (1024.0 ** 3))

        return {
            "total_bytes": size_bytes,
            "total_mb": round(size_gb * 1024, 2),
            "total_gb": round(size_gb, 2),
        }
    except (OSError, ValueError, IndexError) as e:
        return {
            "total_bytes": 0,
            "total_mb": 0.0,
            "total_gb": 0.0,
            "error": str(e)
        }


def get_disk_stats():
    """Get disk statistics."""
    home_dir = os.path.expanduser("~")

    return {
        "home_directory": {
            "path": home_dir,
            "usage": get_directory_size(home_dir)
        }
    }

def get_system_info():
    """Get general system information."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = (datetime.now() - boot_time).total_seconds()

    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "boot_time": boot_time.isoformat(),
        "uptime_seconds": uptime_seconds,
    }


def get_load_average():
    """Get system load average (Unix-like systems only)."""
    try:
        load1, load5, load15 = psutil.getloadavg()
        return {
            "1min": load1,
            "5min": load5,
            "15min": load15,
        }
    except (AttributeError, OSError):
        return None


def collect_all_stats():
    """Collect all server statistics."""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "cpu": get_cpu_stats(),
        "disk": get_disk_stats(),
        "load_average": get_load_average(),
    }


def main():
    """Main function to collect stats and write to JSON file."""
    parser = argparse.ArgumentParser(
        description='Collect server statistics and write to JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        default='server_stats.json',
        help='Output file path (default: server_stats.json)'
    )

    args = parser.parse_args()
    output_file = args.output

    try:
        stats = collect_all_stats()

        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        abs_path = os.path.abspath(output_file)
        file_size = os.path.getsize(output_file)
        print("Statistics written to {0}".format(abs_path))
        print("File size: {0} bytes".format(file_size))

    except Exception as e:
        print("Error collecting or writing statistics: {0}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
