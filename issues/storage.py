import json
import os

from django.conf import settings

REPORTERS_FILE = os.path.join(settings.DATA_DIR, 'reporters.json')
ISSUES_FILE = os.path.join(settings.DATA_DIR, 'issues.json')


def _read(file_path):
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def _write(file_path, records):
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(records, f, indent=2)


def read_reporters():
    return _read(REPORTERS_FILE)


def write_reporters(records):
    _write(REPORTERS_FILE, records)


def read_issues():
    return _read(ISSUES_FILE)


def write_issues(records):
    _write(ISSUES_FILE, records)


def next_id(records):
    if not records:
        return 1
    return max(record['id'] for record in records) + 1
