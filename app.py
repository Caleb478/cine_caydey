from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_file
import mysql.connector
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import timedelta
from datetime import time
import matplotlib.pyplot as plt
import numpy as np
import os
from tempfile import NamedTemporaryFile

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flask'  # Necesario para sesiones

# Conexión a la base de datos
def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",  # Usuario por defecto en XAMPP es "root"
            password="123456",  # Contraseña por defecto en XAMPP es vacía
            database="dbcine" # Nombre de la DB
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
# para el login funcion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        # Comprobar si las credenciales son de administrador
        if usuario == 'manager' and contrasena == 'admin123':
            session['usuario'] = usuario
            return redirect('/admin')  # Redirigir al panel de administración
        
        # Comprobar las credenciales en la base de datos para usuarios normales
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM Usuarios WHERE Usuario = %s AND Contrasena = %s"
        cursor.execute(query, (usuario, contrasena))
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        if user:
            session['usuario'] = user['Usuario']
            return redirect('/')  # Redirigir al índice para usuarios normales
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect('/login')
    
    return render_template('login.html')
@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('admin.html') 

#para sesiones
@app.route('/admin/sesiones')
def admin_sesiones():
    if 'usuario' not in session:  # Verifica que el usuario esté logueado
        return redirect('/login')
    return render_template('sesiones.html')
#para volver a la pestaña peliculas
@app.route('/admin/peliculas')
def admin_peliculas():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('admin.html')

# para ir a usuarios
@app.route('/admin/usuarios')
def admin_usuarios():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('usuarios.html')
# Semanas
@app.route('/semanas')
def semanas():
    return render_template('semanas.html')

# Candy
@app.route('/candy')
def candy():
    return render_template('candybar.html')

@app.route('/')
def home():
    return render_template('index.html')

#para obtener peliculas
@app.route('/pelicula/<int:idPelicula>')
def obtener_pelicula(idPelicula):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    query = "SELECT * FROM Pelicula WHERE idPelicula = %s"  # Tabla correcta
    cursor.execute(query, (idPelicula,))
    pelicula = cursor.fetchone()

    cursor.close()
    conexion.close()

    return jsonify(pelicula)

#Obtener Seciones
# Ruta para obtener las sesiones de una película por su idPelicula
@app.route('/sesiones/<int:idPelicula>')
def obtener_sesiones(idPelicula):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    query = "SELECT * FROM Sesion WHERE idPelicula = %s"
    cursor.execute(query, (idPelicula,))
    sesiones = cursor.fetchall()

    # Convertimos timedelta a un formato serializable en JSON
    for sesion in sesiones:
        for key, value in sesion.items():
            if isinstance(value, timedelta):
                sesion[key] = str(value)  # Convertir a formato HH:MM:SS
                # O usa `sesion[key] = value.total_seconds()`

    cursor.close()
    conexion.close()

    return jsonify(sesiones)
# Ruta para registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        fecha_nac = request.form['fecha_nac']
        dni = request.form['dni']
        correo = request.form['correo']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conexion = conectar()
        cursor = conexion.cursor()
        query = """
        INSERT INTO Usuarios (DNI, Nombre, Apellidos, Fecha_Nac, Correo, Usuario, Contrasena, Fecha_Registro) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE())
        """
        cursor.execute(query, (dni, nombre, apellidos, fecha_nac, correo, usuario, contrasena))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Usuario registrado con éxito. Por favor, inicia sesión.')
        return redirect('/login')
    return render_template('register.html')

# Ruta para el índice (restringido a usuarios logueados)
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect('/login')
    
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT idPelicula, Titulo, Cartel FROM Pelicula")
    peliculas = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template('index.html', usuario=session['usuario'], peliculas=peliculas)


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

# Ruta para obtener las películas y sus sesiones
@app.route('/peliculas')
def peliculas():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.idPelicula, p.Titulo, s.Fecha, s.Hora 
        FROM Pelicula p 
        LEFT JOIN Sesion s ON p.idPelicula = s.idPelicula
    """)
    peliculas = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Agrupar sesiones por película
    peliculas_dict = {}
    for pelicula in peliculas:
        idPelicula = pelicula['idPelicula']
        if idPelicula not in peliculas_dict:
            peliculas_dict[idPelicula] = {
                'Titulo': pelicula['Titulo'],
                'Sesiones': []
            }
        
        # Formatear las fechas a cadenas
        formatted_fecha = pelicula['Fecha'].strftime('%Y-%m-%d') if pelicula['Fecha'] else None
        
        # Convertir timedelta a string
        if isinstance(pelicula['Hora'], timedelta):
            total_seconds = int(pelicula['Hora'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            formatted_hora = f"{hours:02}:{minutes:02}"
        else:
            formatted_hora = pelicula['Hora'].strftime('%H:%M') if pelicula['Hora'] else None

        peliculas_dict[idPelicula]['Sesiones'].append({
            'Fecha': formatted_fecha,
            'Hora': formatted_hora
        })

    return jsonify(list(peliculas_dict.values()))

@app.route('/reporte1')
def reporte1():
    # Crear el PDF
    pdf_path = 'reporte1.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Añadir el título
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Cine Caydey")
    
    # Añadir el logo
    c.drawImage("static/images/5.png", 400, 730, width=80, height=40)

    # Consulta SQL (reemplaza esto con tu consulta)
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Pelicula LIMIT 10")  # Ejemplo de consulta simple
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Añadir los resultados al PDF
    c.setFont("Helvetica", 12)
    y_position = 700
    for resultado in resultados:
        c.drawString(100, y_position, str(resultado))
        y_position -= 20  # Espaciado entre líneas

    c.save()

    return send_file(pdf_path, as_attachment=True)

@app.route('/reporte2')
def reporte2():
    # Crear el PDF
    pdf_path = 'reporte2.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Añadir el título
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Cine Caydey")
    
    # Añadir el logo
    c.drawImage("static/images/logo.jpeg", 400, 730, width=80, height=40)

    # Consulta SQL para obtener todas las películas y sus sesiones
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.Titulo, s.Fecha, s.Hora 
        FROM Pelicula p 
        LEFT JOIN Sesion s ON p.idPelicula = s.idPelicula
        ORDER BY p.Titulo;
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Añadir los resultados al PDF
    c.setFont("Helvetica", 12)
    y_position = 700
    c.drawString(100, y_position, "Películas y Sesiones:")
    y_position -= 20

    for resultado in resultados:
        pelicula_titulo = resultado[0]
        fecha = resultado[1].strftime('%Y-%m-%d') if resultado[1] else "Sin fecha"

        # Convertir timedelta a string
        if isinstance(resultado[2], timedelta):
            total_seconds = int(resultado[2].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            hora = f"{hours:02}:{minutes:02}"
        else:
            hora = resultado[2].strftime('%H:%M') if resultado[2] else "Sin hora"

        c.drawString(100, y_position, f"{pelicula_titulo} - Fecha: {fecha}, Hora: {hora}")
        y_position -= 20  # Espaciado entre líneas

    c.save()

    return send_file(pdf_path, as_attachment=True)

@app.route('/reporte3/<int:id_cliente>')
def reporte3(id_cliente):
    # Crear el PDF
    pdf_path = 'reporte3.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Añadir el título
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Cine Caydey")
    
    # Añadir el logo
    c.drawImage("static/images/logo.jpeg", 400, 730, width=80, height=40)

    # Consulta SQL para calcular el costo total y las entradas vendidas por usuario
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            U.Nombre, 
            SUM(E.Precio_Total) AS Costo_Total, 
            SUM(E.Numero_Entradas) AS Entradas_Vendidas
        FROM 
            Compra C
        JOIN 
            Entradas E ON C.idEntrada = E.idEntrada
        JOIN 
            Usuarios U ON C.idCliente = U.idCliente
        JOIN 
            Reservan R ON C.idCliente = R.idSesion
        JOIN 
            Sesion S ON R.idSesion = S.idSesion
        JOIN 
            Proyecta P ON S.idSesion = P.idSesion
        JOIN 
            Pelicula PE ON P.idPelicula = PE.idPelicula
        JOIN 
            Sala Sa ON R.idSala = Sa.idSala
        JOIN 
            Butaca B ON Sa.idSala = B.idSala
        WHERE 
            U.idCliente = %s
        GROUP BY 
            U.Nombre;
    """, (id_cliente,))
    
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Añadir los resultados al PDF
    c.setFont("Helvetica", 12)
    y_position = 700
    c.drawString(100, y_position, "Costo Total y Entradas Vendidas por Usuario:")
    y_position -= 20

    for resultado in resultados:
        nombre_usuario = resultado[0]
        costo_total = resultado[1] if resultado[1] is not None else 0
        entradas_vendidas = resultado[2] if resultado[2] is not None else 0
        c.drawString(100, y_position, f"Usuario: {nombre_usuario} - Costo Total: {costo_total:.2f} | Entradas Vendidas: {entradas_vendidas}")
        y_position -= 20  # Espaciado entre líneas

    c.save()

    return send_file(pdf_path, as_attachment=True)

@app.route('/reporte4')
def reporte4():
    # Crear el PDF
    pdf_path = 'reporte4.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Añadir el título
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Cine Caydey")
    
    # Añadir el logo
    c.drawImage("static/images/logo.jpeg", 400, 730, width=80, height=40)

    # Consulta SQL para obtener el número de entradas vendidas por película
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            PE.Titulo, 
            SUM(E.Numero_Entradas) AS EntradasVendidas
        FROM 
            Entradas E
        JOIN 
            Compra C ON E.idEntrada = C.idEntrada
        JOIN 
            Proyecta P ON C.idEntrada = E.idEntrada
        JOIN 
            Sesion S ON P.idSesion = S.idSesion
        JOIN 
            Pelicula PE ON P.idPelicula = PE.idPelicula
        GROUP BY 
            PE.Titulo;
    """)
    
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Añadir los resultados al PDF
    c.setFont("Helvetica", 12)
    y_position = 700
    c.drawString(100, y_position, "Entradas Vendidas por Película:")
    y_position -= 20

    titulos = []
    entradas_vendidas = []

    for resultado in resultados:
        titulo = resultado[0]
        entradas = resultado[1] if resultado[1] is not None else 0
        c.drawString(100, y_position, f"Pelicula: {titulo} - Entradas Vendidas: {entradas}")
        titulos.append(titulo)
        entradas_vendidas.append(entradas)
        y_position -= 20  # Espaciado entre líneas

    # Generar la gráfica
    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(titulos))
    plt.barh(y_pos, entradas_vendidas, align='center', alpha=0.5)
    plt.yticks(y_pos, titulos)
    plt.xlabel('Entradas Vendidas')
    plt.title('Entradas Vendidas por Película')

    # Guardar la gráfica en un archivo temporal
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        plt.savefig(temp_file.name, format='png')
        temp_file_path = temp_file.name
    plt.close()

    # Añadir la gráfica al PDF
    c.drawImage(temp_file_path, x=100, y=y_position - 200, width=400, height=200)  # Ajusta la posición y tamaño según sea necesario

    c.save()

    # Eliminar el archivo temporal
    os.remove(temp_file_path)

    return send_file(pdf_path, as_attachment=True)


@app.route('/reporte7')
def reporte7():
    # Crear el PDF
    pdf_path = 'reporte7.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Añadir el título
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Cine Caydey")
    
    # Añadir el logo
    c.drawImage("static/images/logo.jpeg", 400, 730, width=80, height=40)

    # Consulta SQL para obtener entradas vendidas por género en diferentes sesiones
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            PE.Genero,
            S.Fecha,
            SUM(E.Numero_Entradas) AS EntradasVendidas
        FROM 
            Entradas E
        JOIN 
            Compra C ON E.idEntrada = C.idEntrada
        JOIN 
            Proyecta P ON C.idEntrada = E.idEntrada
        JOIN 
            Sesion S ON P.idSesion = S.idSesion
        JOIN 
            Pelicula PE ON P.idPelicula = PE.idPelicula
        GROUP BY 
            PE.Genero, S.Fecha
        ORDER BY 
            S.Fecha, PE.Genero;
    """)
    
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Procesar los resultados para la gráfica
    generos = []
    fechas = []
    entradas_por_genero_y_fecha = {}

    for genero, fecha, entradas in resultados:
        if fecha not in fechas:
            fechas.append(fecha)
        if genero not in entradas_por_genero_y_fecha:
            entradas_por_genero_y_fecha[genero] = [0] * len(fechas)
            generos.append(genero)
        index = fechas.index(fecha)
        entradas_por_genero_y_fecha[genero][index] = entradas  # Cambiado a "=" para garantizar que solo se asignen valores existentes

    # Llenar las entradas con ceros donde no hay datos
    for genero in generos:
        entradas_por_genero_y_fecha[genero] = [entradas_por_genero_y_fecha[genero][i] if i < len(entradas_por_genero_y_fecha[genero]) else 0 for i in range(len(fechas))]

    # Crear la gráfica de barras
    bar_width = 0.15
    x = np.arange(len(fechas))
    
    plt.figure(figsize=(12, 6))
    for i, genero in enumerate(generos):
        plt.bar(x + i * bar_width, entradas_por_genero_y_fecha[genero], width=bar_width, label=genero)

    plt.xlabel('Fechas')
    plt.ylabel('Entradas Vendidas')
    plt.title('Entradas Vendidas por Género en Diferentes Sesiones')
    plt.xticks(x + bar_width * (len(generos) - 1) / 2, fechas, rotation=45)
    plt.legend(title='Géneros')
    
    # Guardar la gráfica en un archivo temporal
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        plt.savefig(temp_file.name, format='png')
        temp_file_path = temp_file.name
    plt.close()

    # Añadir la gráfica al PDF
    c.drawImage(temp_file_path, x=100, y=300, width=400, height=300)  # Ajusta la posición y tamaño según sea necesario

    c.save()

    # Eliminar el archivo temporal
    os.remove(temp_file_path)

    return send_file(pdf_path, as_attachment=True)

# codigo aumentado 19/1/25

@app.route('/obtener_peliculas', methods=['GET'])
def obtener_peliculas():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT idPelicula, Titulo FROM pelicula")
    peliculas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(peliculas)

@app.route('/obtener_sesiones/<int:idPelicula>', methods=['GET'])
def obtener_sesiones_por_pelicula(idPelicula):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    # Consulta para obtener sesiones
    cursor.execute("""
        SELECT idSesion, Fecha, Hora, idSala
        FROM sesion
        WHERE idPelicula = %s
    """, (idPelicula,))
    
    sesiones = cursor.fetchall()

    # Convertir campos de tiempo a cadenas
    for sesion in sesiones:
        sesion['Hora'] = str(sesion['Hora'])  # Asegurar que el tiempo sea serializable en JSON
    
    cursor.close()
    conexion.close()
    return jsonify(sesiones)

@app.route('/obtener_butacas/<int:idSala>', methods=['GET'])
def obtener_butacas(idSala):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT idButaca, Fila, Numero, Estado FROM butaca WHERE idSala = %s", (idSala,))
    butacas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(butacas)

# FUNCION PARA REALIZAR LA COMPRA
@app.route('/realizar_compra', methods=['POST'])
def realizar_compra():
    datos = request.json
    idCliente = session.get('usuario_id')  # ID del usuario logueado
    idSesion = datos['idSesion']
    idButacas = datos['idButacas']
    cantidad = len(idButacas)
    precio_por_boleto = 10.00  # Precio fijo por entrada
    precio_total = cantidad * precio_por_boleto

    conexion = conectar()
    cursor = conexion.cursor()

    # Insertar en entradas
    cursor.execute("INSERT INTO entradas (idCliente, Precio_Total, Numero_Entradas) VALUES (%s, %s, %s)", (idCliente, precio_total, cantidad))
    idEntrada = cursor.lastrowid

    # Insertar en reservas y actualizar estado de butacas
    for idButaca in idButacas:
        cursor.execute("INSERT INTO reserva (idButaca, idEntrada, idSesion, Coste, Fecha_Reserva) VALUES (%s, %s, %s, %s, CURDATE())", (idButaca, idEntrada, idSesion, precio_por_boleto))
        cursor.execute("UPDATE butaca SET Estado = 'Ocupada' WHERE idButaca = %s", (idButaca,))

    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Compra realizada con éxito.", "precio_total": precio_total})

# codigo hoy 22/1/25
# CRUD DE PELICULAS
@app.route('/api/peliculas', methods=['GET'])
def get_peliculas():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pelicula")
    peliculas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(peliculas)

@app.route('/api/peliculas/<int:id>', methods=['GET'])
def get_pelicula(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pelicula WHERE idPelicula = %s", (id,))
    pelicula = cursor.fetchone()
    cursor.close()
    conexion.close()
    return jsonify(pelicula)

@app.route('/api/peliculas', methods=['POST'])
def add_pelicula():
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO pelicula (Titulo, Genero, Clasificacion, Duracion) 
        VALUES (%s, %s, %s, %s)
    """, (data['Titulo'], data['Genero'], data['Clasificacion'], data['Duracion']))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Película agregada"})

@app.route('/api/peliculas/<int:id>', methods=['PUT'])
def update_pelicula(id):
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE pelicula 
        SET Titulo = %s, Genero = %s, Clasificacion = %s, Duracion = %s 
        WHERE idPelicula = %s
    """, (data['Titulo'], data['Genero'], data['Clasificacion'], data['Duracion'], id))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Película actualizada"})

@app.route('/api/peliculas/<int:id>', methods=['DELETE'])
def delete_pelicula(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM pelicula WHERE idPelicula = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Película eliminada"})

# CRUD para la tablas sesiones
@app.route('/api/sesiones', methods=['GET'])
def get_sesiones():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sesion")
    sesiones = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Serializar campos específicos como Hora (TIME) a string
    for sesion in sesiones:
        if isinstance(sesion['Hora'], timedelta):
            total_seconds = int(sesion['Hora'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            sesion['Hora'] = f"{hours:02}:{minutes:02}"

    return jsonify(sesiones)

@app.route('/api/sesiones/<int:id>', methods=['GET'])
def get_sesion(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sesion WHERE idSesion = %s", (id,))
    sesion = cursor.fetchone()
    cursor.close()
    conexion.close()

    # Serializar el campo Hora si existe
    if sesion and isinstance(sesion['Hora'], timedelta):
        total_seconds = int(sesion['Hora'].total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        sesion['Hora'] = f"{hours:02}:{minutes:02}"

    return jsonify(sesion)


@app.route('/api/sesiones', methods=['POST'])
def add_sesion():
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()

    # Verificar si idPelicula y idSala existen
    cursor.execute("SELECT COUNT(*) FROM pelicula WHERE idPelicula = %s", (data['idPelicula'],))
    pelicula_existe = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sala WHERE idSala = %s", (data['idSala'],))
    sala_existe = cursor.fetchone()[0]

    if not pelicula_existe or not sala_existe:
        cursor.close()
        conexion.close()
        return jsonify({"error": "idPelicula o idSala no válido"}), 400

    # Insertar la nueva sesión
    cursor.execute("""
        INSERT INTO sesion (Fecha, Hora, Idioma, idPelicula, idSala)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['Fecha'], data['Hora'], data['Idioma'], data['idPelicula'], data['idSala']))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Sesión agregada"})

@app.route('/api/sesiones/<int:id>', methods=['PUT'])
def update_sesion(id):
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE sesion 
        SET Fecha = %s, Hora = %s, Idioma = %s, idPelicula = %s, idSala = %s 
        WHERE idSesion = %s
    """, (data['Fecha'], data['Hora'], data['Idioma'], data['idPelicula'], data['idSala'], id))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Sesión actualizada"})

@app.route('/api/sesiones/<int:id>', methods=['DELETE'])
def delete_sesion(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM sesion WHERE idSesion = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Sesión eliminada"})

# CRUD para la tabla usuarios
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Serializar las fechas en formato legible
    for usuario in usuarios:
        if 'Fecha_Nac' in usuario:
            usuario['Fecha_Nac'] = usuario['Fecha_Nac'].strftime('%Y-%m-%d')
        if 'Fecha_Registro' in usuario:
            usuario['Fecha_Registro'] = usuario['Fecha_Registro'].strftime('%Y-%m-%d')

    return jsonify(usuarios)


@app.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE idCliente = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    # Serializar las fechas en formato legible
    if usuario and 'Fecha_Nac' in usuario:
        usuario['Fecha_Nac'] = usuario['Fecha_Nac'].strftime('%Y-%m-%d')
    if usuario and 'Fecha_Registro' in usuario:
        usuario['Fecha_Registro'] = usuario['Fecha_Registro'].strftime('%Y-%m-%d')

    return jsonify(usuario)


@app.route('/api/usuarios', methods=['POST'])
def add_usuario():
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO usuarios (DNI, Nombre, Apellidos, Fecha_Nac, Correo, Telefono, Usuario, Contrasena, Puntos, Tarjeta, Fecha_Registro) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (data['DNI'], data['Nombre'], data['Apellidos'], data['Fecha_Nac'], data['Correo'], 
          data['Telefono'], data['Usuario'], data['Contrasena'], data['Puntos'], data['Tarjeta']))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Usuario agregado"})


@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE usuarios 
        SET DNI = %s, Nombre = %s, Apellidos = %s, Correo = %s, Telefono = %s, Usuario = %s, 
            Contrasena = %s, Puntos = %s, Tarjeta = %s
        WHERE idCliente = %s
    """, (data['DNI'], data['Nombre'], data['Apellidos'], data['Correo'], data['Telefono'], 
          data['Usuario'], data['Contrasena'], data['Puntos'], data['Tarjeta'], id))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Usuario actualizado"})


@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE idCliente = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"message": "Usuario eliminado"})

# Ruta para la página de dashboard
@app.route('/admin/dashboard')
def dashboard():
    return render_template('dashboard.html')

# FUNCION PARA EL DASHBOARD
@app.route('/api/dashboard-data')
def dashboard_data():
    connection = conectar()
    try:
        cursor = connection.cursor(dictionary=True)  # Configurar el cursor como diccionario

        # Gráfico 1: Ventas Totales por Mes (de la tabla `reserva`)
        cursor.execute("""
            SELECT MONTH(Fecha_Reserva) AS mes, SUM(Coste) AS total
            FROM reserva
            GROUP BY mes
            ORDER BY mes ASC
        """)
        ventas_totales = cursor.fetchall()
        meses = [f"Mes {v['mes']}" for v in ventas_totales]
        valores_ventas = [v['total'] for v in ventas_totales]

        # Gráfico 2: Entradas Vendidas por Género (de la tabla `pelicula` y `sesion`)
        cursor.execute("""
            SELECT p.Genero, COUNT(*) AS total
            FROM pelicula p
            JOIN sesion s ON p.idPelicula = s.idPelicula
            JOIN reserva r ON r.idSesion = s.idSesion
            GROUP BY p.Genero
        """)
        generos = cursor.fetchall()
        generos_labels = [g['Genero'] for g in generos]
        generos_valores = [g['total'] for g in generos]

        # Gráfico 3: Entradas por Clasificación (de la tabla `pelicula`)
        cursor.execute("""
            SELECT Clasificacion, COUNT(*) AS total
            FROM pelicula
            JOIN sesion ON pelicula.idPelicula = sesion.idPelicula
            JOIN reserva ON sesion.idSesion = reserva.idSesion
            GROUP BY Clasificacion
        """)
        clasificacion = cursor.fetchall()
        clasificacion_labels = [c['Clasificacion'] for c in clasificacion]
        clasificacion_valores = [c['total'] for c in clasificacion]

        # Gráfico 4: Ocupación Promedio de Salas (de la tabla `sala`)
        cursor.execute("""
            SELECT idSala, ROUND((Ocupacion / Capacidad) * 100, 2) AS ocupacion
            FROM sala
        """)
        salas = cursor.fetchall()
        salas_labels = [f"Sala {s['idSala']}" for s in salas]
        salas_valores = [s['ocupacion'] for s in salas]

        return jsonify({
            "ventas_totales": {"meses": meses, "valores": valores_ventas},
            "generos": {"labels": generos_labels, "valores": generos_valores},
            "clasificacion": {"labels": clasificacion_labels, "valores": clasificacion_valores},
            "ocupacion_salas": {"labels": salas_labels, "valores": salas_valores}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)