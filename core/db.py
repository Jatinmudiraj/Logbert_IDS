import sqlite3
import os
import json
from datetime import datetime

class IDSDatabase:
    def __init__(self, db_path="logbert_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                host TEXT,
                source_file TEXT,
                raw_log TEXT,
                normalized_log TEXT,
                template_id TEXT,
                anomaly_score REAL,
                severity TEXT,
                attack_type TEXT,
                reason TEXT
            )
        ''')
        
        # Evaluation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_version TEXT,
                precision REAL,
                recall REAL,
                f1_score REAL,
                false_positive_rate REAL,
                test_sequences INTEGER,
                anomalies_detected INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    def insert_anomaly(self, host, source_file, raw_log, normalized_log, template_id, score, severity, attack_type, reason):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO anomalies (timestamp, host, source_file, raw_log, normalized_log, template_id, anomaly_score, severity, attack_type, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ts, host, source_file, raw_log, normalized_log, template_id, score, severity, attack_type, reason))
        conn.commit()
        conn.close()

    def insert_evaluation(self, version, precision, recall, f1, fpr, total, detected):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO evaluations (timestamp, model_version, precision, recall, f1_score, false_positive_rate, test_sequences, anomalies_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ts, version, precision, recall, f1, fpr, total, detected))
        conn.commit()
        conn.close()

    def get_latest_anomalies(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM anomalies ORDER BY id DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
