
from flask import Flask, render_template, jsonify, request, session # type: ignore
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
app.permanent_session_lifetime = timedelta(days=7)

# --- Simulated data stores (in-memory) ---
# Default admin user
USERS = {
    "admin@glamora.com": {"name": "Admin", "email": "admin@glamora.com", "password": "admin", "role": "admin"}
}

# Products (match the cards in index.html by id)
PRODUCTS = {
    "1": {"id": "1", "name": "Labial Matte", "price": 18.00, "image": "img/BASE MEDIA COBERTURA.jpg"},
    "2": {"id": "2", "name": "Paleta de Sombras", "price": 45.00, "image": "product2.png"},
    "3": {"id": "3", "name": "Base Fluida", "price": 35.00, "image": "product3.png"},
    "4": {"id": "4", "name": "Máscara Volumen", "price": 22.00, "image": "product4.png"},
}

# --- Helpers ---
def get_cart():
    return session.setdefault("cart", {})

def cart_summary(cart):
    items = []
    subtotal = 0.0
    total_qty = 0
    for pid, qty in cart.items():
        prod = PRODUCTS.get(pid)
        if not prod:
            continue
        line_total = prod["price"] * qty
        subtotal += line_total
        total_qty += qty
        items.append({
            "id": prod["id"],
            "name": prod["name"],
            "price": prod["price"],
            "image": prod["image"],
            "quantity": qty,
        })
    return {"items": items, "subtotal": round(subtotal, 2), "count": total_qty}

# --- Pages ---
@app.route("/")
def index():
    # Lista de imágenes y datos para las tarjetas
    img_files = [
        'BASE MEDIA COBERTURA.jpg','BASE QUEEN.webp','BASE TRENDY.webp','BASE.jpg','BB CREAM.jpg','BRONZER.jpg','CONTORNO TRENDY.webp','CORRECOTR TRENDY.webp','CORRECTOR BLOM.png','CORRECTOR MAGIC.webp','CORRECTOR OJERA.webp','CORRECTOR VITAMINA E.jpg','CORRECTOR.jpg','DELINEADOR COLOR.webp','DELINEADOR LIQUIDO.jpg','DELINEADOR PLUMON.webp','DELINEADOR PROFESIONAL.webp','DELINEADOR.jpg','FIJADOR TRENDY CEJAS.webp','GEL 2 EN 1 CEJAS.jpg','GEL FIJADPR CEJAS.webp','ILIMINADOR POLVO.jpg','ILUMINADOR CREMA.jpg','ILUMINADOR LIQUI TRENDY.webp','ILUMINADOR LIQUIDO.jpg','ILUMINADOR TRENDY.webp','KIT LIP GLOSS.webp','LIP GLOSS ATENEA.webp','LIP GLOSS MYK.webp','LIP GLOSS TREND.webp','LIP GLOSS TRENDY.webp','PALETA CONTORNOS.jpg','PALETA SOMBRAS.jpg','PALETA.jpg','PESTAÑA SERENITY.jpg','PESTAÑINA LASH.jpg','PESTAÑINA PROSA.webp','PESTAÑINA.jpg','RUBOR CREMA.jpg','RUBOR LIQUID.jpg','RUBOR POLVO.jpg','RUBOR PRIMAVERA.webp','RUBOR STAR.webp','SOMBR SAFARI.webp','SOMBRA CHOCOLATE.webp','SOMBRAS BLOSSOM.webp','TINTA BLOOM.png','TINTA ESCARCHA.webp','TINTA.jpg','TINTA.png'
    ]
    productos = []
    for idx, img in enumerate(img_files, start=1):
        nombre = img.rsplit('.',1)[0].replace('_',' ').replace('-',' ')
        productos.append({
            'id': idx,
            'imagen': 'img/' + img,
            'nombre': nombre,
            'descripcion': f'Producto {idx}: {nombre}. Calidad y belleza garantizada.',
            'precio': f"${10 + idx * 2}.00"
        })
    return render_template("index.html", productos=productos)

# --- Auth API ---
@app.post("/api/register")
def api_register():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not name or not email or not password:
        return jsonify({"ok": False, "error": "Todos los campos son obligatorios."}), 400
    if email in USERS:
        return jsonify({"ok": False, "error": "Este correo ya está registrado."}), 400
    USERS[email] = {"name": name, "email": email, "password": password, "role": "user"}
    session["user"] = {"name": name, "email": email, "role": "user"}
    session.permanent = True
    return jsonify({"ok": True, "user": session["user"]})

@app.post("/api/login")
def api_login():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = USERS.get(email)
    if not user or user["password"] != password:
        return jsonify({"ok": False, "error": "Credenciales inválidas."}), 401

    session["user"] = {"name": user["name"], "email": user["email"], "role": user["role"]}
    session.permanent = True

    # Nuevo campo "redirect"
    redirect_url = "/admin" if user["role"] == "admin" else "/"
    return jsonify({
        "ok": True,
        "user": session["user"],
        "redirect": redirect_url
    })
    
@app.post("/api/logout")
def api_logout():
    session.pop("user", None)
    return jsonify({"ok": True})

@app.get("/api/session")
def api_session():
    return jsonify({"ok": True, "user": session.get("user")})

# --- Products API (optional) ---
@app.get("/api/products")
def api_products():
    return jsonify({"ok": True, "products": list(PRODUCTS.values())})

# --- Cart API ---
@app.get("/api/cart")
def api_cart():
    cart = get_cart()
    return jsonify({"ok": True, **cart_summary(cart)})

@app.post("/api/cart/add")
def api_cart_add():
    data = request.get_json(force=True)
    pid = str(data.get("id"))
    qty = int(data.get("quantity", 1))
    if pid not in PRODUCTS:
        return jsonify({"ok": False, "error": "Producto no encontrado."}), 404
    cart = get_cart()
    cart[pid] = cart.get(pid, 0) + max(1, qty)
    session["cart"] = cart
    return jsonify({"ok": True, **cart_summary(cart)})

@app.post("/api/cart/update")
def api_cart_update():
    data = request.get_json(force=True)
    pid = str(data.get("id"))
    action = data.get("action")
    cart = get_cart()
    if pid not in cart:
        return jsonify({"ok": False, "error": "El producto no está en el carrito."}), 404
    if action == "increase":
        cart[pid] += 1
    elif action == "decrease":
        cart[pid] -= 1
        if cart[pid] <= 0:
            cart.pop(pid, None)
    else:
        return jsonify({"ok": False, "error": "Acción no válida."}), 400
    session["cart"] = cart
    return jsonify({"ok": True, **cart_summary(cart)})

@app.post("/api/cart/remove")
def api_cart_remove():
    data = request.get_json(force=True)
    pid = str(data.get("id"))
    cart = get_cart()
    cart.pop(pid, None)
    session["cart"] = cart
    return jsonify({"ok": True, **cart_summary(cart)})

@app.post("/api/checkout")
def api_checkout():
    cart = get_cart()
    if not cart:
        return jsonify({"ok": False, "error": "Tu carrito está vacío."}), 400
    # Simulate checkout
    session["cart"] = {}
    return jsonify({"ok": True, "message": "¡Gracias por tu compra! Este es un sitio de demostración."})

if __name__ == "__main__":
    app.run(debug=True)
