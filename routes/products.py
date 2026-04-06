from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db
import math

bp = Blueprint('products', __name__, url_prefix='/products')
PER_PAGE = 20


@bp.route('/')
def index():
    db = get_db()
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '')
    supplier_id = request.args.get('supplier_id', '')
    status = request.args.get('status', '')
    page = max(1, int(request.args.get('page', 1)))

    where = ['p.is_active = 1']
    params = []

    if search:
        where.append('(p.name LIKE ? OR p.reference LIKE ?)')
        params += [f'%{search}%', f'%{search}%']
    if category_id:
        where.append('p.category_id = ?')
        params.append(category_id)
    if supplier_id:
        where.append('p.supplier_id = ?')
        params.append(supplier_id)
    if status == 'low':
        where.append('p.quantity > 0 AND p.quantity <= p.min_threshold')
    elif status == 'out':
        where.append('p.quantity <= 0')
    elif status == 'ok':
        where.append('p.quantity > p.min_threshold')

    where_clause = 'WHERE ' + ' AND '.join(where)

    total = db.execute(f'SELECT COUNT(*) as c FROM products p {where_clause}', params).fetchone()['c']
    pages = max(1, math.ceil(total / PER_PAGE))
    offset = (page - 1) * PER_PAGE

    products = db.execute(f'''
        SELECT p.*, c.name as category_name, c.color as category_color, s.name as supplier_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        {where_clause}
        ORDER BY p.name
        LIMIT ? OFFSET ?
    ''', params + [PER_PAGE, offset]).fetchall()

    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()

    return render_template('products/index.html',
                           products=[dict(p) for p in products],
                           categories=categories, suppliers=suppliers,
                           search=search, category_id=category_id, supplier_id=supplier_id,
                           status=status, page=page, pages=pages, total=total)


@bp.route('/<int:id>')
def detail(id):
    db = get_db()
    product = db.execute('''
        SELECT p.*, c.name as category_name, s.name as supplier_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.id = ?
    ''', (id,)).fetchone()
    if not product:
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('products.index'))

    movements = db.execute('''
        SELECT * FROM movements WHERE product_id = ? ORDER BY movement_date DESC LIMIT 20
    ''', (id,)).fetchall()

    return render_template('products/detail.html', product=product, movements=movements)


@bp.route('/create', methods=['POST'])
def create():
    db = get_db()
    fields = ['name', 'reference', 'category_id', 'supplier_id', 'unit', 'location', 'expiry_date', 'notes']
    data = {f: request.form.get(f, '').strip() or None for f in fields}
    min_threshold = float(request.form.get('min_threshold', 5) or 5)

    if not data['name']:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('products.index'))

    try:
        db.execute('''INSERT INTO products (name, reference, category_id, supplier_id, unit, min_threshold, location, expiry_date, notes)
                      VALUES (:name, :reference, :category_id, :supplier_id,
                              COALESCE(:unit, 'unité'), :min_threshold, :location, :expiry_date, :notes)''',
                   {**data, 'min_threshold': min_threshold})
        db.commit()
        flash(f'Produit "{data["name"]}" créé.', 'success')
    except Exception as e:
        flash(f'Erreur: référence déjà existante ou données invalides.', 'danger')

    return redirect(url_for('products.index'))


@bp.route('/<int:id>/edit', methods=['POST'])
def edit(id):
    db = get_db()
    fields = ['name', 'reference', 'category_id', 'supplier_id', 'unit', 'location', 'expiry_date', 'notes']
    data = {f: request.form.get(f, '').strip() or None for f in fields}
    min_threshold = float(request.form.get('min_threshold', 5) or 5)

    if not data['name']:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('products.index'))

    try:
        db.execute('''UPDATE products SET name=:name, reference=:reference, category_id=:category_id,
                      supplier_id=:supplier_id, unit=COALESCE(:unit,'unité'), min_threshold=:min_threshold,
                      location=:location, expiry_date=:expiry_date, notes=:notes, updated_at=CURRENT_TIMESTAMP
                      WHERE id=:id''',
                   {**data, 'min_threshold': min_threshold, 'id': id})
        db.commit()
        flash('Produit mis à jour.', 'success')
    except Exception:
        flash('Erreur: référence déjà utilisée.', 'danger')

    return redirect(url_for('products.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    db = get_db()
    db.execute('UPDATE products SET is_active=0 WHERE id=?', (id,))
    db.commit()
    flash('Produit archivé.', 'success')
    return redirect(url_for('products.index'))
