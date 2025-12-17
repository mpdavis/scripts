#!/usr/bin/env python3
"""
Rsync Webhook Service

A simple webhook server that triggers rsync commands.
Includes request queuing to prevent concurrent rsync executions.
"""

import logging
import subprocess
import threading
from datetime import datetime
from queue import Queue

from flask import Flask, request, jsonify, Blueprint

from config import RSYNC_COMMAND, HOST, PORT, LOG_FILE, LOG_LEVEL

# Initialize Flask app
app = Flask(__name__)

# Create a blueprint with the URL prefix for reverse proxy routing
api = Blueprint('api', __name__, url_prefix='/sync')

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Task queue for rsync commands
task_queue = Queue()
current_task = None
task_lock = threading.Lock()


class RsyncTask:
    """Represents an rsync task."""

    def __init__(self, task_id):
        self.task_id = task_id
        self.timestamp = datetime.now()
        self.status = 'queued'
        self.result = None
        self.error = None
        self.progress = {
            'percentage': 0,
            'transferred': '0',
            'rate': '0/s',
            'current_file': None
        }

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'progress': self.progress if self.status == 'running' else None
        }


def parse_rsync_progress(line, task):
    """Parse rsync progress output and update task progress."""
    import re

    # rsync --info=progress2 format:
    # "  1,234,567  12%  123.45kB/s    0:00:12"
    # or with file info:
    # "  1,234,567  12%  123.45kB/s    0:00:12  (xfr#1, to-chk=99/100)"

    # Try to match progress line
    match = re.search(r'\s+([\d,]+)\s+(\d+)%\s+([\d.]+[kMG]?B/s)', line)
    if match:
        transferred = match.group(1)
        percentage = int(match.group(2))
        rate = match.group(3)

        task.progress['transferred'] = transferred
        task.progress['percentage'] = percentage
        task.progress['rate'] = rate

        logger.debug(f"Task {task.task_id} progress: {percentage}% - {transferred} at {rate}")


def execute_rsync(task):
    """Execute the rsync command with real-time progress tracking."""
    global current_task

    with task_lock:
        current_task = task
        task.status = 'running'

    # Add progress flag to rsync command
    command = RSYNC_COMMAND + ['--info=progress2']

    logger.info(f"Starting rsync task {task.task_id}")
    logger.info(f"Command: {' '.join(command)}")

    stdout_lines = []
    stderr_lines = []

    try:
        # Use Popen for real-time output parsing
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Read output line by line
        for line in process.stdout:
            stdout_lines.append(line)

            # Parse progress information
            parse_rsync_progress(line, task)

            # Log non-progress lines
            if line.strip() and not line.strip().startswith((' ', '\r')):
                logger.info(f"Task {task.task_id}: {line.strip()}")

        # Wait for process to complete
        returncode = process.wait()

        if returncode == 0:
            task.status = 'completed'
            task.progress['percentage'] = 100
            task.result = {
                'stdout': ''.join(stdout_lines),
                'stderr': '',
                'returncode': returncode
            }
            logger.info(f"Task {task.task_id} completed successfully")
        else:
            raise subprocess.CalledProcessError(returncode, command, ''.join(stdout_lines))

    except subprocess.CalledProcessError as e:
        task.status = 'failed'
        task.error = {
            'message': str(e),
            'stdout': e.stdout if hasattr(e, 'stdout') else ''.join(stdout_lines),
            'stderr': e.stderr if hasattr(e, 'stderr') else '',
            'returncode': e.returncode
        }
        logger.error(f"Task {task.task_id} failed: {e}")

    except Exception as e:
        task.status = 'failed'
        task.error = {'message': str(e)}
        logger.error(f"Task {task.task_id} encountered an error: {e}")

    finally:
        with task_lock:
            current_task = None


def worker():
    """Background worker that processes rsync tasks from the queue."""
    logger.info("Worker thread started")

    while True:
        task = task_queue.get()

        if task is None:  # Shutdown signal
            break

        execute_rsync(task)
        task_queue.task_done()

    logger.info("Worker thread stopped")


# Start the worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

# Task counter for unique IDs
task_counter = 0
task_counter_lock = threading.Lock()


@api.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests."""
    global task_counter

    with task_counter_lock:
        task_counter += 1
        task_id = task_counter

    # Create and queue the task
    task = RsyncTask(task_id)
    task_queue.put(task)

    queue_size = task_queue.qsize()
    logger.info(f"Webhook triggered - Task {task_id} queued (queue size: {queue_size})")

    return jsonify({
        'success': True,
        'message': 'Rsync task queued',
        'task': task.to_dict(),
        'queue_size': queue_size
    }), 202


@api.route('/status', methods=['GET'])
def status():
    """Get current status of the webhook service."""
    with task_lock:
        current = current_task.to_dict() if current_task else None

    return jsonify({
        'current_task': current,
        'queue_size': task_queue.qsize(),
        'total_tasks_processed': task_counter
    })


@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


# Register the blueprint
app.register_blueprint(api)


if __name__ == '__main__':
    logger.info(f"Starting rsync webhook service on {HOST}:{PORT}")
    logger.info(f"Rsync command: {' '.join(RSYNC_COMMAND)}")

    try:
        app.run(host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        task_queue.put(None)  # Signal worker to stop
        worker_thread.join(timeout=5)
