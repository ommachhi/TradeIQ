from __future__ import annotations

from datetime import timedelta

from db.database import get_connection
from utils.helpers import utc_iso, utc_now


def _normalize_user_row(row):
    data = dict(row) if row else None
    if not data:
        return None
    full_name = data.get("full_name") or data.get("name") or ""
    data["full_name"] = full_name
    data["name"] = full_name
    return data


def _row_to_dict(row):
    return _normalize_user_row(row)


def _rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_user_by_email(email: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, full_name, email, password_hash, mobile, country, experience, role, created_at FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, full_name, email, password_hash, mobile, country, experience, role, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_dict(row)


def create_user(
    full_name: str,
    email: str,
    password_hash: str,
    mobile: str,
    country: str,
    experience: str,
    role: str = "user",
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (
                full_name, email, password_hash, mobile, country,
                experience, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name.strip(),
                email.strip().lower(),
                password_hash,
                mobile.strip(),
                country.strip(),
                experience.strip(),
                role,
            ),
        )
        connection.commit()
        return cursor.lastrowid


def update_user_profile(user_id: int, full_name: str, mobile: str, country: str, experience: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET full_name = ?, mobile = ?, country = ?, experience = ?
            WHERE id = ?
            """,
            (full_name.strip(), mobile.strip(), country.strip(), experience.strip(), user_id),
        )
        connection.commit()


def update_user_password(email: str, password_hash: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, email.strip().lower()),
        )
        connection.commit()


def touch_last_login(user_id: int) -> None:
    return None


def record_login_attempt(email: str, success: bool) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO login_attempts (email, attempted_at, success) VALUES (?, ?, ?)",
            (email.strip().lower(), utc_iso(), int(success)),
        )
        connection.commit()


def count_recent_failed_logins(email: str, window_minutes: int) -> int:
    cutoff = (utc_now() - timedelta(minutes=window_minutes)).isoformat()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS attempts
            FROM login_attempts
            WHERE email = ? AND success = 0 AND attempted_at >= ?
            """,
            (email.strip().lower(), cutoff),
        ).fetchone()
    return int(row["attempts"]) if row else 0


def list_users():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, full_name, email, role, mobile, country, experience, created_at
            FROM users
            ORDER BY created_at DESC
            """
        ).fetchall()
    return _rows_to_dicts(rows)


def list_recent_users(limit: int = 10):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, full_name, email, role, country, experience, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_user_growth(days: int = 30):
    cutoff = (utc_now() - timedelta(days=days)).isoformat()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT substr(created_at, 1, 10) AS date, COUNT(*) AS users
            FROM users
            WHERE created_at >= ?
            GROUP BY substr(created_at, 1, 10)
            ORDER BY date ASC
            """,
            (cutoff,),
        ).fetchall()
    return _rows_to_dicts(rows)


def upsert_watchlist_item(user_id: int, symbol: str, alert_price: float | None = None) -> None:
    timestamp = utc_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO watchlist (user_id, symbol, alert_price, added_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, symbol)
            DO UPDATE SET alert_price = COALESCE(excluded.alert_price, watchlist.alert_price)
            """,
            (user_id, symbol.upper(), alert_price, timestamp),
        )
        connection.commit()


def remove_watchlist_item(user_id: int, symbol: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM watchlist WHERE user_id = ? AND symbol = ?",
            (user_id, symbol.upper()),
        )
        connection.commit()


def list_watchlist(user_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
            (user_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def add_portfolio_holding(user_id: int, symbol: str, quantity: float, buy_price: float, buy_date: str) -> None:
    timestamp = utc_iso()
    symbol = symbol.upper()
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT quantity, buy_price, buy_date FROM portfolio WHERE user_id = ? AND symbol = ?",
            (user_id, symbol),
        ).fetchone()
        if existing:
            total_quantity = float(existing["quantity"]) + quantity
            total_cost = (float(existing["quantity"]) * float(existing["buy_price"])) + (quantity * buy_price)
            average_price = total_cost / total_quantity if total_quantity else buy_price
            connection.execute(
                """
                UPDATE portfolio
                SET quantity = ?, buy_price = ?, buy_date = ?, updated_at = ?
                WHERE user_id = ? AND symbol = ?
                """,
                (total_quantity, average_price, buy_date, timestamp, user_id, symbol),
            )
        else:
            connection.execute(
                """
                INSERT INTO portfolio (
                    user_id, symbol, quantity, buy_price, buy_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, symbol, quantity, buy_price, buy_date, timestamp, timestamp),
            )
        connection.execute(
            """
            INSERT INTO portfolio_transactions (
                user_id, symbol, quantity, buy_price, trade_date, action, created_at
            ) VALUES (?, ?, ?, ?, ?, 'BUY', ?)
            """,
            (user_id, symbol, quantity, buy_price, buy_date, timestamp),
        )
        connection.commit()


def remove_portfolio_holding(user_id: int, holding_id: int) -> None:
    with get_connection() as connection:
        holding = connection.execute(
            "SELECT symbol, quantity, buy_price, buy_date FROM portfolio WHERE id = ? AND user_id = ?",
            (holding_id, user_id),
        ).fetchone()
        if holding:
            connection.execute(
                """
                INSERT INTO portfolio_transactions (
                    user_id, symbol, quantity, buy_price, trade_date, action, created_at
                ) VALUES (?, ?, ?, ?, ?, 'REMOVE', ?)
                """,
                (
                    user_id,
                    holding["symbol"],
                    holding["quantity"],
                    holding["buy_price"],
                    holding["buy_date"],
                    utc_iso(),
                ),
            )
            connection.execute(
                "DELETE FROM portfolio WHERE id = ? AND user_id = ?",
                (holding_id, user_id),
            )
            connection.commit()


def list_portfolio_holdings(user_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM portfolio WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def list_portfolio_transactions(user_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT symbol, quantity, buy_price, trade_date, action, created_at
            FROM portfolio_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def add_alert(user_id: int, symbol: str, target_price: float, condition: str = "above") -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO alerts (user_id, symbol, target_price, condition, status, created_at)
            VALUES (?, ?, ?, ?, 'active', ?)
            """,
            (user_id, symbol.upper(), target_price, condition, utc_iso()),
        )
        connection.commit()


def list_alerts(user_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM alerts WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def remove_alert(user_id: int, alert_id: int) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM alerts WHERE user_id = ? AND id = ?",
            (user_id, alert_id),
        )
        connection.commit()


def log_prediction(
    user_id: int | None,
    symbol: str,
    model_name: str,
    horizon_label: str,
    current_price: float,
    predicted_price: float,
    confidence: float | None,
    signal: str,
    trend: str,
    volatility: float | None,
    metrics: dict | None = None,
    notes: str | None = None,
) -> None:
    metrics = metrics or {}
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO prediction_logs (
                user_id, symbol, model_name, horizon_label, current_price, predicted_price,
                confidence, signal, trend, volatility, rmse, mae, r2, accuracy, created_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                symbol.upper(),
                model_name,
                horizon_label,
                current_price,
                predicted_price,
                confidence,
                signal,
                trend,
                volatility,
                metrics.get("rmse"),
                metrics.get("mae"),
                metrics.get("r2"),
                metrics.get("accuracy"),
                utc_iso(),
                notes,
            ),
        )
        connection.commit()


def list_prediction_logs(user_id: int | None = None, limit: int = 100):
    query = """
        SELECT prediction_logs.*, users.name AS user_name
        FROM prediction_logs
        LEFT JOIN users ON users.id = prediction_logs.user_id
    """
    params: tuple = ()
    if user_id is not None:
        query += " WHERE prediction_logs.user_id = ?"
        params = (user_id,)
    query += " ORDER BY created_at DESC LIMIT ?"
    params += (limit,)
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return _rows_to_dicts(rows)


def get_model_accuracy_summary():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                model_name AS model,
                AVG(rmse) AS rmse,
                AVG(mae) AS mae,
                AVG(r2) AS r2,
                AVG(accuracy) AS accuracy
            FROM prediction_logs
            GROUP BY model_name
            ORDER BY model_name ASC
            """
        ).fetchall()
    return _rows_to_dicts(rows)


def log_api_usage(endpoint: str, symbol: str | None, status_code: int, response_time_ms: float | None) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO api_usage (endpoint, symbol, status_code, response_time_ms, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (endpoint, symbol, status_code, response_time_ms, utc_iso()),
        )
        connection.commit()


def get_api_usage_summary(days: int = 7):
    cutoff = (utc_now() - timedelta(days=days)).isoformat()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT endpoint, COUNT(*) AS calls, AVG(response_time_ms) AS avg_response_ms
            FROM api_usage
            WHERE created_at >= ?
            GROUP BY endpoint
            ORDER BY calls DESC
            """,
            (cutoff,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_symbol_api_usage(days: int = 7):
    cutoff = (utc_now() - timedelta(days=days)).isoformat()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT COALESCE(symbol, 'N/A') AS symbol, COUNT(*) AS calls
            FROM api_usage
            WHERE created_at >= ?
            GROUP BY COALESCE(symbol, 'N/A')
            ORDER BY calls DESC
            LIMIT 20
            """,
            (cutoff,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_dashboard_counts():
    today = utc_now().date().isoformat()
    with get_connection() as connection:
        total_users = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        active_today = connection.execute(
            "SELECT COUNT(*) AS count FROM users WHERE last_login_at LIKE ?",
            (f"{today}%",),
        ).fetchone()["count"]
        predictions = connection.execute("SELECT COUNT(*) AS count FROM prediction_logs").fetchone()["count"]
        api_calls = connection.execute(
            "SELECT COUNT(*) AS count FROM api_usage WHERE created_at LIKE ?",
            (f"{today}%",),
        ).fetchone()["count"]
    return {
        "total_users": int(total_users),
        "active_today": int(active_today),
        "predictions": int(predictions),
        "api_calls": int(api_calls),
    }
