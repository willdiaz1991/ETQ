import json
import os
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from domain.models.printing import PrintAuditEntry, PrintDecision

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class PrintAuditRepository:
    def __init__(self, database_path: Optional[Path] = None):
        configured_path = os.environ.get("PRINT_AUDIT_DB_PATH")
        self.database_path = database_path or (
            Path(configured_path) if configured_path else BACKEND_ROOT / "data" / "printing_audit.sqlite3"
        )

    def record_attempt(self, decision: PrintDecision) -> PrintAuditEntry:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._create_table(connection)
            previously_printed = self._has_successful_print(connection, decision.lpn)
            decision = replace(decision, is_reprint=previously_printed)
            event_type = "REJECTED" if not decision.approved else "REPRINT" if previously_printed else "PRINT"
            entry = PrintAuditEntry(
                request_id=str(uuid4()),
                requested_at=datetime.now(timezone.utc).isoformat(),
                lpn=decision.lpn,
                etq_id=decision.etq_id,
                zone=decision.zone,
                requested_by=decision.requested_by,
                approved=decision.approved,
                event_type=event_type,
                is_reprint=previously_printed,
                reasons=decision.reasons,
            )
            connection.execute(
                """
                INSERT INTO print_audit (
                    request_id, requested_at, lpn, etq_id, zone, requested_by,
                    approved, event_type, is_reprint, reasons
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.request_id,
                    entry.requested_at,
                    entry.lpn,
                    entry.etq_id,
                    entry.zone,
                    entry.requested_by,
                    int(entry.approved),
                    entry.event_type,
                    int(entry.is_reprint),
                    json.dumps(entry.reasons, ensure_ascii=False),
                ),
            )
        return entry

    def list_history(self, lpn: Optional[str] = None, limit: int = 100) -> List[PrintAuditEntry]:
        with self._connect() as connection:
            self._create_table(connection)
            if lpn:
                rows = connection.execute(
                    """
                    SELECT request_id, requested_at, lpn, etq_id, zone, requested_by,
                           approved, event_type, is_reprint, reasons
                    FROM print_audit
                    WHERE lower(lpn) = lower(?)
                    ORDER BY requested_at DESC, rowid DESC
                    LIMIT ?
                    """,
                    (lpn.strip(), limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT request_id, requested_at, lpn, etq_id, zone, requested_by,
                           approved, event_type, is_reprint, reasons
                    FROM print_audit
                    ORDER BY requested_at DESC, rowid DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            PrintAuditEntry(
                request_id=row["request_id"],
                requested_at=row["requested_at"],
                lpn=row["lpn"],
                etq_id=row["etq_id"],
                zone=row["zone"],
                requested_by=row["requested_by"],
                approved=bool(row["approved"]),
                event_type=row["event_type"],
                is_reprint=bool(row["is_reprint"]),
                reasons=tuple(json.loads(row["reasons"])),
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _create_table(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS print_audit (
                request_id TEXT PRIMARY KEY,
                requested_at TEXT NOT NULL,
                lpn TEXT NOT NULL,
                etq_id TEXT,
                zone TEXT,
                requested_by TEXT,
                approved INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                is_reprint INTEGER NOT NULL,
                reasons TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _has_successful_print(connection: sqlite3.Connection, lpn: str) -> bool:
        row = connection.execute(
            "SELECT EXISTS(SELECT 1 FROM print_audit WHERE lower(lpn) = lower(?) AND approved = 1)",
            (lpn,),
        ).fetchone()
        return bool(row[0])
