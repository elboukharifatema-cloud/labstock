from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db

bp = Blueprint('categories', __name__, url_prefix='/categories')


@bp.route('/')
def index():
    db = get_db()
    categories = db.execute('''
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id AND p.is_active = 1
        GROUP BY c.id ORDER BY c.name
    ''').fetchall()
    return render_template('categories/index.html', categories=[dict(c) for c in categories])


@bp.route('/create', methods=['POST'])
def create():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '#3B82F6')

    if not name:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('categories.index'))

    db = get_db()
    try:
        db.execute('INSERT INTO categories (name, description, color) VALUES (?, ?, ?)',
                   (name, description, color))
        db.commit()
        flash(f'Catégorie "{name}" créée avec succès.', 'success')
    except Exception:
        flash(f'La catégorie "{name}" existe déjà.', 'danger')

    return redirect(url_for('categories.index'))


@bp.route('/<int:id>/edit', methods=['POST'])
def edit(id):
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '#3B82F6')

    if not name:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('categories.index'))

    db = get_db()
    try:
        db.execute('UPDATE categories SET name=?, description=?, color=? WHERE id=?',
                   (name, description, color, id))
        db.commit()
        flash(f'Catégorie mise à jour.', 'success')
    except Exception:
        flash('Ce nom de catégorie existe déjà.', 'danger')

    return redirect(url_for('categories.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    db = get_db()
    count = db.execute('SELECT COUNT(*) as c FROM products WHERE category_id=? AND is_active=1', (id,)).fetchone()['c']
    if count > 0:
        flash(f'Impossible: {count} produit(s) utilisent cette catégorie.', 'danger')
    else:
        db.execute('DELETE FROM categories WHERE id=?', (id,))
        db.commit()
        flash('Catégorie supprimée.', 'success')
    return redirect(url_for('categories.index'))
