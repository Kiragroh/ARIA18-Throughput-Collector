import hashlib
import json
import sqlite3
from importlib.metadata import version
from pathlib import Path
from . import VERSION


def cache_key(path, profile):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    digest.update(json.dumps(profile.as_dict(),sort_keys=True).encode())
    digest.update(VERSION.encode())
    for package in ("pandas","numpy","openpyxl"):
        digest.update(version(package).encode())
    for source in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    return digest.hexdigest()


def get(path,key):
    if not path.exists():
        return None
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS aggregate_cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        row = db.execute("SELECT payload FROM aggregate_cache WHERE key=?",(key,)).fetchone()
    return json.loads(row[0]) if row else None


def put(path,key,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS aggregate_cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        db.execute("INSERT OR REPLACE INTO aggregate_cache VALUES (?,?)",
                   (key,json.dumps(data,allow_nan=False)))
