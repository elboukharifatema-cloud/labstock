from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@bp.route('/')
def index():
    db = get_db()
    suppliers = db.execute('''
        SELECT s.*, COUNT(p.id) as product_count
        FROM suppliers s
        LEFT JOIN products p ON p.supplier_id = s.id AND p.is_active = 1
        GROUP BY s.id ORDER BY s.name
    ''').fetchall()
    return render_template('suppliers/index.html', suppliers=[dict(s) for s in suppliers])


@bp.route('/create', methods=['POST'])
def create():
    data = {k: request.form.get(k, '').strip() for k in ['name', 'contact_person', 'phone', 'email', 'address', 'notes']}
    if not data['name']:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('suppliers.index'))
    db = get_db()
    db.execute('INSERT INTO suppliers (name, contact_person, phone, email, address, notes) VALUES (?,?,?,?,?,?)',
               tuple(data.values()))
    db.commit()
    flash(f'Fournisseur "{data["name"]}" créé.', 'success')
    return redirect(url_for('suppliers.index'))


@bp.route('/<int:id>/edit', methods=['POST'])
def edit(id):
    data = {k: request.form.get(k, '').strip() for k in ['name', 'contact_person', 'phone', 'email', 'address', 'notes']}
    if not data['name']:
        flash('Le nom est obligatoire.', 'danger')
        return redirect(url_for('suppliers.index'))
    db = get_db()
    db.execute('UPDATE suppliers SET name=?, contact_person=?, phone=?, email=?, address=?, notes=? WHERE id=?',
               (*data.values(), id))
    db.commit()
    flash('Fournisseur mis à jour.', 'success')
    return redirect(url_for('suppliers.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    db = get_db()
    count = db.execute('SELECT COUNT(*) as c FROM products WHERE supplier_id=? AND is_active=1', (id,)).fetchone()['c']
    if count > 0:
        flash(f'Impossible: {count} produit(s) sont liés à ce fournisseur.', 'danger')
    else:
        db.execute('DELETE FROM suppliers WHERE id=?', (id,))
        db.commit()
        flash('Fournisseur supprimé.', 'success')
    return redirect(url_for('suppliers.index'))
