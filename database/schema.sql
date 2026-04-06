-- Supprimer les tables si elles existent
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS movements;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS categories;

-- Catégories de produits
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT '#3B82F6',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fournisseurs
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Produits / Réactifs
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    reference TEXT UNIQUE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    unit TEXT NOT NULL DEFAULT 'unité',
    quantity REAL NOT NULL DEFAULT 0,
    min_threshold REAL NOT NULL DEFAULT 5,
    location TEXT,
    expiry_date DATE,
    notes TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Mouvements de stock
CREATE TABLE movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    movement_type TEXT NOT NULL CHECK(movement_type IN ('entry', 'exit')),
    quantity REAL NOT NULL CHECK(quantity > 0),
    reason TEXT DEFAULT 'Manuel',
    user_name TEXT NOT NULL DEFAULT 'Système',
    notes TEXT,
    movement_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alertes
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('low_stock', 'out_of_stock', 'expiry_soon')),
    message TEXT,
    is_resolved INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);

-- Trigger: mise à jour quantité sur entrée
CREATE TRIGGER update_qty_on_entry
AFTER INSERT ON movements
WHEN NEW.movement_type = 'entry'
BEGIN
    UPDATE products
    SET quantity = quantity + NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.product_id;
END;

-- Trigger: mise à jour quantité sur sortie
CREATE TRIGGER update_qty_on_exit
AFTER INSERT ON movements
WHEN NEW.movement_type = 'exit'
BEGIN
    UPDATE products
    SET quantity = quantity - NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.product_id;
END;

-- Trigger: alerte stock bas après mouvement de sortie
CREATE TRIGGER auto_alert_low_stock
AFTER UPDATE OF quantity ON products
WHEN NEW.quantity <= NEW.min_threshold AND NEW.quantity > 0
BEGIN
    INSERT OR IGNORE INTO alerts (product_id, alert_type, message)
    SELECT NEW.id, 'low_stock', 'Stock bas: ' || NEW.name || ' (' || CAST(NEW.quantity AS TEXT) || ' ' || NEW.unit || ' restant(s))'
    WHERE NOT EXISTS (
        SELECT 1 FROM alerts
        WHERE product_id = NEW.id AND alert_type = 'low_stock' AND is_resolved = 0
    );
END;

-- Trigger: alerte rupture de stock
CREATE TRIGGER auto_alert_out_of_stock
AFTER UPDATE OF quantity ON products
WHEN NEW.quantity <= 0
BEGIN
    UPDATE alerts SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
    WHERE product_id = NEW.id AND alert_type = 'low_stock' AND is_resolved = 0;

    INSERT OR IGNORE INTO alerts (product_id, alert_type, message)
    SELECT NEW.id, 'out_of_stock', 'Rupture de stock: ' || NEW.name
    WHERE NOT EXISTS (
        SELECT 1 FROM alerts
        WHERE product_id = NEW.id AND alert_type = 'out_of_stock' AND is_resolved = 0
    );
END;

-- Index pour performances
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_movements_product ON movements(product_id);
CREATE INDEX idx_movements_date ON movements(movement_date);
CREATE INDEX idx_alerts_product ON alerts(product_id);
