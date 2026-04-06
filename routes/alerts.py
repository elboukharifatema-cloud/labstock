from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db
from config import LOW_STOCK_EXPIRY_DAYS

bp = Blueprint('alerts', __name__, url_prefix='/alerts')


@bp.route('/')
def index():
    db = get_db()

    low_stock = db.execute('''
        SELECT p.*, c.name as category_name,
               CAST(p.quantity AS REAL) / p.min_threshold as stock_ratio
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.quantity <= p.min_threshold AND p.is_active = 1
        ORDER BY stock_ratio ASC
    ''').fetchall()

    expiry_soon = db.execute(f'''
        SELECT p.*, c.name as category_name,
               CAST(julianday(p.expiry_date) - julianday('now') AS INTEGER) as days_left
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.expiry_date IS NOT NULL
          AND p.expiry_date <= date('now', '+{LOW_STOCK_EXPIRY_DAYS} days')
          AND p.is_active = 1
        ORDER BY p.expiry_date ASC
    ''').fetchall()

    return render_template('alerts/index.html', low_stock=low_stock, expiry_soon=expiry_soon)
