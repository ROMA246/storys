from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from itertools import count

app = Flask(__name__, static_folder='static', template_folder='templates')

# -------------------------------
# Almacenamiento en memoria (demo)
# -------------------------------
_users = []
_obras = []
_user_id_seq = count(1)
_obra_id_seq = count(1)

# -------------------------------
# Funciones auxiliares
# -------------------------------
def seed():
    """Crea obras de ejemplo si no existen."""
    if not _obras:
        _obras.extend([
            {
                'id': next(_obra_id_seq),
                'titulo': 'El primer amanecer',
                'autor': 'Anónimo',
                'tipo': 'cuento',
                'contenido': 'Era una vez un amanecer que cambió todo...',
                'created_at': datetime.utcnow().isoformat(),
                'views': 12,
                'images': [],
                'premium': None,
                'status': 'publicada',
                'estilo': None
            },
            {
                'id': next(_obra_id_seq),
                'titulo': 'Reseña: Libro X',
                'autor': 'Lector1',
                'tipo': 'reseña',
                'contenido': 'Este libro ofrece una visión profunda...',
                'created_at': datetime.utcnow().isoformat(),
                'views': 5,
                'images': [],
                'premium': None,
                'status': 'publicada',
                'estilo': None
            }
        ])

def _premium_plans():
    return [
        {'id':'basic','title':'Premium 3 meses','months':3,'price':'$4.99',
         'summary':'Mejoras básicas: exportar PDF, portada personalizada, subir 3 imágenes.'},
        {'id':'plus','title':'Premium 9 meses','months':9,'price':'$12.99',
         'summary':'Todo de 3m + revisión profesional automática (básica), hasta 10 imágenes, estadísticas.'},
        {'id':'pro','title':'Premium 12 meses','months':12,'price':'$19.99',
         'summary':'Todo de 9m + promoción destacada, revisión avanzada, colaboraciones, herramientas avanzadas de formato.'}
    ]

def _premium_features(plan_id):
    plans = {p['id']: p for p in _premium_plans()}
    return plans.get(plan_id)

seed()

# -------------------------------
# Rutas principales
# -------------------------------
@app.route('/')
def index():
    top = sorted(_obras, key=lambda o: o['views'], reverse=True)[:5]
    return render_template('index.html', top_obras=top)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error = None
    if request.method == 'POST':
        nombre = request.form.get('nombre','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm = request.form.get('confirm_password','')
        if not nombre or not email or not password:
            error = "Completa todos los campos."
        elif password != confirm:
            error = "Las contraseñas no coinciden."
        elif any(u for u in _users if u['email'] == email):
            error = "Correo ya registrado."
        else:
            _users.append({'id': next(_user_id_seq), 'nombre': nombre, 'email': email, 'password': password})
            return redirect(url_for('index'))
    return render_template('registro.html', error=error)

@app.route('/obras')
def obras_page():
    return render_template('obras.html', obras=_obras)

# -------------------------------
# Crear obra
# -------------------------------
@app.route('/crear_obra', methods=['GET','POST'])
def crear_obra():
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        contenido = request.form.get('contenido','').strip()
        tipo = request.form.get('tipo','cuento').strip()
        autor = request.form.get('autor','Tú').strip()
        action = request.form.get('action', 'finish')

        if not titulo or not contenido:
            return render_template('crear_obra.html', error="Título y contenido requeridos.")

        obra = {
            'id': next(_obra_id_seq),
            'titulo': titulo,
            'autor': autor,
            'tipo': tipo,
            'contenido': contenido,
            'created_at': datetime.utcnow().isoformat(),
            'views': 0,
            'images': [],
            'premium': None,
            'status': 'borrador' if action == 'save' else 'publicada',
            'estilo': None
        }
        _obras.append(obra)

        if action == 'save':
            return render_template('crear_obra.html', mensaje="Obra guardada como borrador.", obra=obra)
        elif action == 'contact':
            return redirect(url_for('contacto'))
        else:
            return redirect(url_for('editar_obra', obra_id=obra['id']))

    return render_template('crear_obra.html')

# -------------------------------
# Editar obra
# -------------------------------
@app.route('/editar_obra', methods=['GET','POST'])
def editar_obra():
    obra_id = request.args.get('obra_id', type=int)
    if obra_id is None:
        return redirect(url_for('obras_page'))

    obra = next((o for o in _obras if o['id'] == obra_id), None)
    if not obra:
        return "Obra no encontrada", 404

    if request.method == 'POST':
        action = request.form.get('action')
        obra['titulo'] = request.form.get('titulo', obra['titulo'])
        obra['autor'] = request.form.get('autor', obra['autor'])
        obra['tipo'] = request.form.get('tipo', obra['tipo'])
        obra['contenido'] = request.form.get('contenido', obra['contenido'])
        return redirect(url_for('editar_obra', obra_id=obra_id))

    return render_template('editar_obra.html', obra=obra)

# -------------------------------
# Editar estilo de la obra
# -------------------------------
@app.route('/editar_obra_estilo', methods=['GET','POST'])
def editar_obra_estilo():
    obra_id = request.args.get('obra_id', type=int)
    obra = next((o for o in _obras if o['id'] == obra_id), None)
    if not obra:
        return "Obra no encontrada", 404

    if request.method == 'POST':
        font_color = request.form.get('font_color', '#000000')
        font_family = request.form.get('font_family', 'Inter')
        font_size = request.form.get('font_size', '16')
        background_color = request.form.get('background_color', '#ffffff')
        background_image = request.form.get('background_image', '').strip()

        obra['estilo'] = {
            'color_texto': font_color,
            'fuente': font_family,
            'tamano_letra': font_size,
            'color_fondo': background_color,
            'imagen_fondo': background_image
        }

        return redirect(url_for('editar_obra', obra_id=obra_id))

    return render_template('editar_obra_estilo.html', obra=obra, premium_plans=_premium_plans())

# -------------------------------
# Publicar obra desde Biblioteca
# -------------------------------
@app.route('/publicar_obra/<int:obra_id>', methods=['POST'])
def publicar_obra(obra_id):
    obra = next((o for o in _obras if o['id']==obra_id), None)
    if not obra:
        return "Obra no encontrada", 404
    obra['status'] = 'publicada'
    return redirect(url_for('obras_page'))

# -------------------------------
# Eliminar obra
# -------------------------------
@app.route('/eliminar_obra/<int:obra_id>', methods=['POST'])
def eliminar_obra(obra_id):
    obra = next((o for o in _obras if o['id'] == obra_id), None)
    if not obra:
        return "Obra no encontrada", 404
    _obras.remove(obra)
    return redirect(url_for('obras_page'))

# -------------------------------
# Otras páginas
# -------------------------------
@app.route('/terminos')
def terminos():
    return render_template('terminos.html')

@app.route('/privacidad')
def privacidad():
    return render_template('privacidad.html')

@app.route('/premium')
def premium():
    return render_template('premium.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# -------------------------------
# API JSON
# -------------------------------
@app.route('/api/obras', methods=['GET','POST'])
def api_obras():
    if request.method == 'GET':
        q = request.args.get('q','').lower()
        tipo = request.args.get('tipo','').lower()
        results = _obras
        if q:
            results = [o for o in results if q in o['titulo'].lower() or q in o['autor'].lower() or q in o['contenido'].lower()]
        if tipo:
            results = [o for o in results if o['tipo'].lower() == tipo]
        return jsonify([{
            'id': o['id'],
            'titulo': o['titulo'],
            'autor': o['autor'],
            'tipo': o['tipo'],
            'created_at': o['created_at'],
            'views': o.get('views',0)
        } for o in results])

    data = request.get_json() or {}
    titulo = data.get('titulo','').strip()
    contenido = data.get('contenido','').strip()
    tipo = data.get('tipo','cuento').strip()
    autor = data.get('autor','Tú').strip()
    if not titulo or not contenido:
        return jsonify({'error':'titulo y contenido requeridos'}), 400

    obra = {
        'id': next(_obra_id_seq),
        'titulo': titulo,
        'autor': autor,
        'tipo': tipo,
        'contenido': contenido,
        'created_at': datetime.utcnow().isoformat(),
        'views': 0,
        'images': [],
        'premium': None,
        'estilo': None
    }
    _obras.append(obra)
    return jsonify({'ok': True, 'obra': obra}), 201

@app.route('/api/obras/<int:obra_id>', methods=['GET','PUT','DELETE'])
def api_obra(obra_id):
    obra = next((o for o in _obras if o['id'] == obra_id), None)
    if not obra:
        return jsonify({'error':'no encontrado'}), 404

    if request.method == 'GET':
        obra['views'] = obra.get('views',0) + 1
        return jsonify(obra)

    if request.method == 'PUT':
        data = request.get_json() or {}
        obra['titulo'] = data.get('titulo', obra['titulo'])
        obra['contenido'] = data.get('contenido', obra['contenido'])
        obra['tipo'] = data.get('tipo', obra['tipo'])
        return jsonify({'ok': True, 'obra': obra})

    if request.method == 'DELETE':
        _obras.remove(obra)
        return jsonify({'ok': True})

# -------------------------------
# Ejecutar aplicación
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
