from flask import Blueprint, jsonify, request
from database.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/products/search')
def products_search():
    q = request.args.get('q', '').strip()
    db = get_db()
    products = db.execute('''
        SELECT id, name, reference, quantity, unit
        FROM products WHERE is_active=1 AND (name LIKE ? OR reference LIKE ?)
        ORDER BY name LIMIT 10
    ''', (f'%{q}%', f'%{q}%')).fetchall()
    return jsonify([dict(p) for p in products])


@bp.route('/products/<int:id>/stock')
def product_stock(id):
    db = get_db()
    p = db.execute('SELECT id, name, quantity, unit FROM products WHERE id=?', (id,)).fetchone()
    if not p:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(p))


@bp.route('/alerts/count')
def alerts_count():
    db = get_db()
    count = db.execute('''
        SELECT COUNT(*) as c FROM products
        WHERE quantity <= min_threshold AND is_active=1
    ''').fetchone()['c']
    return jsonify({'count': count})


@bp.route('/dashboard/chart-data')
def chart_data():
    db = get_db()
    rows = db.execute('''
        SELECT date(movement_date) as day,
               SUM(CASE WHEN movement_type='entry' THEN quantity ELSE 0 END) as entries,
               SUM(CASE WHEN movement_type='exit'  THEN quantity ELSE 0 END) as exits
        FROM movements
        WHERE movement_date >= date('now', '-30 days')
        GROUP BY date(movement_date)
        ORDER BY day ASC
    ''').fetchall()
    return jsonify([dict(r) for r in rows])
