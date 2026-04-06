from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db

bp = Blueprint('movements', __name__, url_prefix='/movements')

ENTRY_REASONS = ['Commande fournisseur', 'Retour article', 'Ajustement inventaire', 'Don / Transfert', 'Autre']
EXIT_REASONS  = ['Utilisation analyses', 'Périmé / jeté', 'Casse / perte', 'Transfert', 'Autre']


@bp.route('/')
def index():
    db = get_db()
    product_id = request.args.get('product_id', '')
    movement_type = request.args.get('movement_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    where = []
    params = []
    if product_id:
        where.append('m.product_id = ?')
        params.append(product_id)
    if movement_type:
        where.append('m.movement_type = ?')
        params.append(movement_type)
    if date_from:
        where.append('date(m.movement_date) >= ?')
        params.append(date_from)
    if date_to:
        where.append('date(m.movement_date) <= ?')
        params.append(date_to)

    where_clause = ('WHERE ' + ' AND '.join(where)) if where else ''

    movements = db.execute(f'''
        SELECT m.*, p.name as product_name, p.unit
        FROM movements m
        JOIN products p ON m.product_id = p.id
        {where_clause}
        ORDER BY m.movement_date DESC LIMIT 100
    ''', params).fetchall()

    products = db.execute('SELECT id, name FROM products WHERE is_active=1 ORDER BY name').fetchall()

    return render_template('movements/index.html',
                           movements=movements, products=products,
                           product_id=product_id, movement_type=movement_type,
                           date_from=date_from, date_to=date_to)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    db = get_db()
    products = db.execute('SELECT id, name, quantity, unit FROM products WHERE is_active=1 ORDER BY name').fetchall()

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        movement_type = request.form.get('movement_type')
        quantity_str = request.form.get('quantity', '0')
        reason = request.form.get('reason', '').strip()
        user_name = request.form.get('user_name', 'Utilisateur').strip()
        notes = request.form.get('notes', '').strip() or None

        try:
            quantity = float(quantity_str)
        except ValueError:
            flash('Quantité invalide.', 'danger')
            return render_template('movements/form.html', products=products,
                                   entry_reasons=ENTRY_REASONS, exit_reasons=EXIT_REASONS)

        if not product_id or not movement_type or quantity <= 0:
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return render_template('movements/form.html', products=products,
                                   entry_reasons=ENTRY_REASONS, exit_reasons=EXIT_REASONS)

        product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
        if not product:
            flash('Produit introuvable.', 'danger')
            return redirect(url_for('movements.create'))

        if movement_type == 'exit' and product['quantity'] < quantity:
            flash(f'Stock insuffisant. Disponible: {product["quantity"]} {product["unit"]}.', 'danger')
            return render_template('movements/form.html', products=products,
                                   entry_reasons=ENTRY_REASONS, exit_reasons=EXIT_REASONS)

        db.execute('''INSERT INTO movements (product_id, movement_type, quantity, reason, user_name, notes)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (product_id, movement_type, quantity, reason, user_name or 'Système', notes))
        db.commit()

        action = 'Entrée' if movement_type == 'entry' else 'Sortie'
        flash(f'{action} de {quantity} {product["unit"]} enregistrée pour "{product["name"]}".', 'success')
        return redirect(url_for('movements.index'))

    return render_template('movements/form.html', products=products,
                           entry_reasons=ENTRY_REASONS, exit_reasons=EXIT_REASONS)
