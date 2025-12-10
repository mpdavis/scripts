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


def get_memory_stats():
    """Get memory statistics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "virtual": {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
        }
    }


def get_disk_stats():
    """Get disk statistics."""
    partitions = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            })
        except (OSError, IOError):
            continue

    disk_io = psutil.disk_io_counters()
    return {
        "partitions": partitions,
        "io": {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
        } if disk_io else None,
    }


def get_network_stats():
    """Get network statistics."""
    net_io = psutil.net_io_counters()

    interfaces = {}
    for interface, addrs in psutil.net_if_addrs().items():
        interfaces[interface] = []
        for addr in addrs:
            interfaces[interface].append({
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
            })

    return {
        "io": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout,
            "drops_in": net_io.dropin,
            "drops_out": net_io.dropout,
        },
        "interfaces": interfaces,
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
        "memory": get_memory_stats(),
        "disk": get_disk_stats(),
        "network": get_network_stats(),
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
