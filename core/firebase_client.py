"""
Firebase Firestore client.
Falls back to in-memory demo store if credentials are unavailable.
"""
import os, uuid
from datetime import datetime, timezone
from django.conf import settings

_db = None
_demo_mode = False

# SQLite database configuration and schemas
SCHEMAS = {
    'users': {
        'columns': [
            ('id', 'TEXT PRIMARY KEY'),
            ('name', 'TEXT'),
            ('email', 'TEXT'),
            ('password_hash', 'TEXT'),
            ('degree', 'TEXT'),
            ('country_goal', 'TEXT'),
            ('points', 'INTEGER'),
            ('level', 'INTEGER'),
            ('streak', 'INTEGER'),
            ('journey_stage', 'TEXT'),
            ('created_at', 'TEXT'),
            ('json_data', 'TEXT')
        ]
    },
    'assessments': {
        'columns': [
            ('id', 'TEXT PRIMARY KEY'),
            ('profile_score', 'INTEGER'),
            ('generated_at', 'TEXT'),
            ('json_data', 'TEXT')
        ]
    },
    'loan_applications': {
        'columns': [
            ('id', 'TEXT PRIMARY KEY'),
            ('status', 'TEXT'),
            ('current_step', 'INTEGER'),
            ('json_data', 'TEXT')
        ]
    },
    'chat_history': {
        'columns': [
            ('id', 'TEXT PRIMARY KEY'),
            ('uid', 'TEXT'),
            ('role', 'TEXT'),
            ('content', 'TEXT'),
            ('_created', 'TEXT'),
            ('json_data', 'TEXT')
        ]
    }
}

import sqlite3
import json
from contextlib import contextmanager

@contextmanager
def get_db_conn():
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

def get_schema(collection):
    if collection in SCHEMAS:
        return SCHEMAS[collection]
    return {
        'columns': [
            ('id', 'TEXT PRIMARY KEY'),
            ('json_data', 'TEXT')
        ]
    }

def init_sqlite():
    with get_db_conn() as conn:
        cursor = conn.cursor()
        for collection, schema in SCHEMAS.items():
            cols_def = ", ".join(f"{name} {col_type}" for name, col_type in schema['columns'])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {collection} ({cols_def})")
        conn.commit()
    print("[StudyBridge] (OK) SQLite fallback database initialized")

def init_firebase():
    global _db, _demo_mode
    creds_path = os.path.join(settings.BASE_DIR, settings.FIREBASE_CREDENTIALS_PATH)
    if not os.path.exists(creds_path) or not settings.FIREBASE_PROJECT_ID:
        print("[StudyBridge] (!!) Firebase credentials not found — running in DEMO MODE")
        _demo_mode = True
        init_sqlite()
        return
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[StudyBridge] (OK) Firebase Firestore connected")
    except Exception as e:
        print(f"[StudyBridge] (!!) Firebase init failed ({e}) — DEMO MODE")
        _demo_mode = True
        init_sqlite()


def _now():
    return datetime.now(timezone.utc).isoformat()


def is_demo_mode():
    return _demo_mode


# ── Generic CRUD ──────────────────────────────────────────────────────────────

def set_doc(collection, doc_id, data):
    data['_updated'] = _now()
    if _demo_mode:
        try:
            with get_db_conn() as conn:
                cursor = conn.cursor()
                schema = get_schema(collection)
                
                # Ensure the table exists
                cols_def = ", ".join(f"{name} {col_type}" for name, col_type in schema['columns'])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {collection} ({cols_def})")
                
                # Fetch existing data for merge
                cursor.execute(f"SELECT json_data FROM {collection} WHERE id = ?", (doc_id,))
                row = cursor.fetchone()
                existing_data = {}
                if row:
                    existing_data = json.loads(row[0])
                
                merged_data = {**existing_data, **data}
                
                # Populate columns based on schema
                cols = []
                placeholders = []
                values = []
                for name, _ in schema['columns']:
                    cols.append(name)
                    placeholders.append("?")
                    if name == 'json_data':
                        values.append(json.dumps(merged_data))
                    else:
                        val = merged_data.get(name)
                        if val is None and name == 'id':
                            val = doc_id
                        values.append(val)
                
                sql = f"INSERT OR REPLACE INTO {collection} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, values)
                conn.commit()
            return True
        except Exception as e:
            print(f"SQLite set_doc error for collection {collection}: {e}")
            return False
    try:
        _db.collection(collection).document(doc_id).set(data, merge=True)
        return True
    except Exception as e:
        print(f"Firebase set_doc error: {e}")
        return False


def get_doc(collection, doc_id):
    if _demo_mode:
        try:
            with get_db_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT json_data FROM {collection} WHERE id = ?", (doc_id,))
                row = cursor.fetchone()
                return json.loads(row[0]) if row else None
        except sqlite3.OperationalError:
            return None
        except Exception as e:
            print(f"SQLite get_doc error for collection {collection}: {e}")
            return None
    try:
        doc = _db.collection(collection).document(doc_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Firebase get_doc error: {e}")
        return None


def add_doc(collection, data):
    doc_id = str(uuid.uuid4())
    data['id'] = doc_id
    data['_created'] = _now()
    set_doc(collection, doc_id, data)
    return doc_id


def query_docs(collection, field, op, value, limit=30):
    if _demo_mode:
        try:
            with get_db_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT json_data FROM {collection}")
                rows = cursor.fetchall()
            
            items = [json.loads(row[0]) for row in rows]
            
            # Apply filtering
            if op == '==':
                items = [i for i in items if i.get(field) == value]
            elif op == '>':
                items = [i for i in items if i.get(field) > value]
            elif op == '<':
                items = [i for i in items if i.get(field) < value]
            elif op == '>=':
                items = [i for i in items if i.get(field) >= value]
            elif op == '<=':
                items = [i for i in items if i.get(field) <= value]
            elif op == '!=':
                items = [i for i in items if i.get(field) != value]
                
            return items[:limit]
        except sqlite3.OperationalError:
            return []
        except Exception as e:
            print(f"SQLite query_docs error for collection {collection}: {e}")
            return []
    try:
        from google.cloud.firestore_v1.base_query import FieldFilter
        docs = (_db.collection(collection)
                .where(filter=FieldFilter(field, op, value))
                .limit(limit).stream())
        return [d.to_dict() for d in docs]
    except Exception as e:
        print(f"Firebase query error: {e}")
        return []


# ── Domain helpers ────────────────────────────────────────────────────────────

def get_user_profile(uid):       return get_doc('users', uid)
def save_user_profile(uid, d):   return set_doc('users', uid, d)
def get_assessment(uid):         return get_doc('assessments', uid)
def save_assessment(uid, d):     return set_doc('assessments', uid, d)
def get_loan_application(uid):   return get_doc('loan_applications', uid)
def save_loan_application(uid, d): return set_doc('loan_applications', uid, d)


def add_chat_message(uid, role, content):
    return add_doc('chat_history', {'uid': uid, 'role': role, 'content': content})


def get_chat_history(uid, limit=20):
    msgs = query_docs('chat_history', 'uid', '==', uid, limit=limit)
    msgs.sort(key=lambda x: x.get('_created', ''))
    return msgs
