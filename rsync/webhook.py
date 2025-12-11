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

from flask import Flask, request, jsonify

from config import RSYNC_COMMAND, HOST, PORT, LOG_FILE, LOG_LEVEL

# Initialize Flask app
app = Flask(__name__)

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

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'result': self.result,
            'error': self.error
        }


def execute_rsync(task):
    """Execute the rsync command."""
    global current_task

    with task_lock:
        current_task = task
        task.status = 'running'

    logger.info(f"Starting rsync task {task.task_id}")
    logger.info(f"Command: {' '.join(RSYNC_COMMAND)}")

    try:
        result = subprocess.run(
            RSYNC_COMMAND,
            capture_output=True,
            text=True,
            check=True
        )

        task.status = 'completed'
        task.result = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        logger.info(f"Task {task.task_id} completed successfully")

    except subprocess.CalledProcessError as e:
        task.status = 'failed'
        task.error = {
            'message': str(e),
            'stdout': e.stdout,
            'stderr': e.stderr,
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


@app.route('/webhook', methods=['POST'])
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


@app.route('/status', methods=['GET'])
def status():
    """Get current status of the webhook service."""
    with task_lock:
        current = current_task.to_dict() if current_task else None

    return jsonify({
        'current_task': current,
        'queue_size': task_queue.qsize(),
        'total_tasks_processed': task_counter
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    logger.info(f"Starting rsync webhook service on {HOST}:{PORT}")
    logger.info(f"Rsync command: {' '.join(RSYNC_COMMAND)}")

    try:
        app.run(host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        task_queue.put(None)  # Signal worker to stop
        worker_thread.join(timeout=5)
