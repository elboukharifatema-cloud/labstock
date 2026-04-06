from flask import Blueprint, render_template
from database.db import get_db

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    db = get_db()

    # KPIs
    kpis = db.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN quantity = 0 THEN 1 ELSE 0 END) as out_of_stock,
            SUM(CASE WHEN quantity > 0 AND quantity <= min_threshold THEN 1 ELSE 0 END) as low_stock,
            SUM(CASE WHEN quantity > min_threshold THEN 1 ELSE 0 END) as ok_stock
        FROM products WHERE is_active = 1
    ''').fetchone()

    # Mouvements récents
    recent_movements = db.execute('''
        SELECT m.*, p.name as product_name, p.unit
        FROM movements m
        JOIN products p ON m.product_id = p.id
        ORDER BY m.movement_date DESC LIMIT 10
    ''').fetchall()

    # Produits en alerte
    low_stock_products = db.execute('''
        SELECT p.name, p.quantity, p.min_threshold, p.unit, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.quantity <= p.min_threshold AND p.is_active = 1
        ORDER BY CAST(p.quantity AS REAL) / p.min_threshold ASC
        LIMIT 5
    ''').fetchall()

    # Statistiques par catégorie
    category_stats = db.execute('''
        SELECT c.name, c.color, COUNT(p.id) as product_count,
               SUM(CASE WHEN p.quantity <= p.min_threshold THEN 1 ELSE 0 END) as alert_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id AND p.is_active = 1
        GROUP BY c.id, c.name, c.color
        ORDER BY product_count DESC
    ''').fetchall()

    # Mouvements des 7 derniers jours pour le graphique
    chart_data = db.execute('''
        SELECT
            date(movement_date) as day,
            SUM(CASE WHEN movement_type = 'entry' THEN quantity ELSE 0 END) as entries,
            SUM(CASE WHEN movement_type = 'exit' THEN quantity ELSE 0 END) as exits
        FROM movements
        WHERE movement_date >= date('now', '-7 days')
        GROUP BY date(movement_date)
        ORDER BY day ASC
    ''').fetchall()

    return render_template('dashboard/index.html',
                           kpis=kpis,
                           recent_movements=recent_movements,
                           low_stock_products=low_stock_products,
                           category_stats=category_stats,
                           chart_data=[dict(r) for r in chart_data])
