import os
import struct
import zlib
from flask import Flask
from config import DATABASE, SECRET_KEY
from database.db import init_app, get_db


def _make_png_icon(size, bg, fg):
    """Generate a simple medical-cross PNG icon in memory."""
    def chunk(name, data):
        crc = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', crc)
    cx = cy = size // 2
    r = size * 0.32
    hw = size * 0.08
    raw = b''
    for y in range(size):
        raw += b'\x00'
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** .5
            if dist <= size * 0.46:
                if (abs(dx) < hw and abs(dy) < r) or (abs(dy) < hw and abs(dx) < r):
                    raw += bytes(fg + (255,))
                else:
                    raw += bytes(bg + (255,))
            else:
                raw += b'\x00\x00\x00\x00'
    comp = zlib.compress(raw, 6)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', comp)
            + chunk(b'IEND', b''))


def _generate_icons():
    icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    for sz in [192, 512]:
        path = os.path.join(icons_dir, f'icon-{sz}.png')
        if not os.path.exists(path):
            with open(path, 'wb') as f:
                f.write(_make_png_icon(sz, (30, 64, 175), (255, 255, 255)))


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['DATABASE'] = DATABASE
    app.config['SECRET_KEY'] = SECRET_KEY

    # Init DB
    init_app(app)

    # Blueprints
    from routes.dashboard  import bp as dashboard_bp
    from routes.products   import bp as products_bp
    from routes.categories import bp as categories_bp
    from routes.suppliers  import bp as suppliers_bp
    from routes.movements  import bp as movements_bp
    from routes.alerts     import bp as alerts_bp
    from routes.api        import bp as api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(movements_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(api_bp)

    # Context processor: low-stock count for navbar badge
    @app.context_processor
    def inject_alert_count():
        try:
            db = get_db()
            count = db.execute(
                'SELECT COUNT(*) as c FROM products WHERE quantity <= min_threshold AND is_active=1'
            ).fetchone()['c']
        except Exception:
            count = 0
        return {'alert_count': count}

    # Auto-init DB and icons on first run
    with app.app_context():
        os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
        if not os.path.exists(app.config['DATABASE']):
            from database.db import init_db
            init_db()
    _generate_icons()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
