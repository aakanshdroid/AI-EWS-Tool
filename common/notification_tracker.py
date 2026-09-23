import sqlite3
from pathlib import Path
from datetime import datetime


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Existing project database
DB_PATH = BASE_DIR / "data" / "ews_cm_database.db"


def initialize_notification_table():
    """
    Create the EWS notification history table if it does not exist.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ews_notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                borrower_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                risk_score REAL,
                risk_band TEXT,
                override_flag TEXT,
                first_detected TEXT NOT NULL,
                last_notified TEXT NOT NULL,
                notification_count INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1,
                UNIQUE(borrower_id, alert_type)
            )
            """
        )

        conn.commit()


def should_send_critical_alert(
    borrower_id,
    risk_score,
    risk_band,
    override_flag
):
    """
    Determine whether a Critical email should be sent.

    Returns:
        True  -> send email
        False -> suppress duplicate email
    """

    initialize_notification_table()

    alert_type = "CRITICAL"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT active
            FROM ews_notification_history
            WHERE borrower_id = ?
              AND alert_type = ?
            """,
            (str(borrower_id), alert_type)
        )

        record = cursor.fetchone()

        # No previous record:
        # this is a new Critical event.
        if record is None:
            return True

        # Already recorded as active:
        # suppress duplicate notification.
        if record[0] == 1:
            return False

        # Previously Critical but subsequently became
        # non-Critical. A new Critical event can notify again.
        return True


def record_critical_notification(
    borrower_id,
    risk_score,
    risk_band,
    override_flag
):
    """
    Record a successfully sent Critical notification.
    """

    initialize_notification_table()

    alert_type = "CRITICAL"
    now = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO ews_notification_history (
                borrower_id,
                alert_type,
                risk_score,
                risk_band,
                override_flag,
                first_detected,
                last_notified,
                notification_count,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)

            ON CONFLICT(borrower_id, alert_type)
            DO UPDATE SET
                risk_score = excluded.risk_score,
                risk_band = excluded.risk_band,
                override_flag = excluded.override_flag,
                last_notified = excluded.last_notified,
                notification_count =
                    ews_notification_history.notification_count + 1,
                active = 1
            """,
            (
                str(borrower_id),
                alert_type,
                risk_score,
                risk_band,
                override_flag,
                now,
                now
            )
        )

        conn.commit()


def mark_non_critical(borrower_ids):
    """
    Mark borrowers that are no longer Critical as inactive.

    This allows a fresh email if they become Critical again later.
    """

    initialize_notification_table()

    borrower_ids = {
        str(borrower_id)
        for borrower_id in borrower_ids
    }

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT DISTINCT borrower_id
            FROM ews_notification_history
            WHERE alert_type = 'CRITICAL'
              AND active = 1
            """
        )

        active_borrowers = {
            str(row[0])
            for row in cursor.fetchall()
        }

        for borrower_id in active_borrowers:
            if borrower_id not in borrower_ids:
                conn.execute(
                    """
                    UPDATE ews_notification_history
                    SET active = 0
                    WHERE borrower_id = ?
                      AND alert_type = 'CRITICAL'
                    """,
                    (borrower_id,)
                )

        conn.commit()


def notification_history_exists():
    """
    Check whether the notification history already contains
    any borrower records.

    Returns:
        True  -> notification history already exists
        False -> no notification history exists
    """

    initialize_notification_table()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT COUNT(*)
            FROM ews_notification_history
            """
        )

        count = cursor.fetchone()[0]

    return count > 0


def record_critical_baseline(
    borrower_id,
    risk_score,
    risk_band,
    override_flag
):
    """
    Record the current Critical state as a baseline.

    This does NOT represent an email notification.
    It establishes the initial state so that the first
    pipeline run does not generate bulk emails.
    """

    initialize_notification_table()

    alert_type = "CRITICAL"
    now = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO ews_notification_history (
                borrower_id,
                alert_type,
                risk_score,
                risk_band,
                override_flag,
                first_detected,
                last_notified,
                notification_count,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1)

            ON CONFLICT(borrower_id, alert_type)
            DO UPDATE SET
                risk_score = excluded.risk_score,
                risk_band = excluded.risk_band,
                override_flag = excluded.override_flag,
                active = 1
            """,
            (
                str(borrower_id),
                alert_type,
                risk_score,
                risk_band,
                override_flag,
                now,
                now
            )
        )

        conn.commit()