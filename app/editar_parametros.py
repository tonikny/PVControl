#from flask import Flask, request, render_template

from flask import Flask, render_template, request, redirect, url_for

import os

app = Flask(__name__)

###############################################
# Configuración de la contraseña
PASSWORD = "1234"  # poner en Parametros_FV.py para version final
################################################

session = {}
session['logged_in'] = False


# Ruta para el formulario de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


#########################
# Parametros_FV.py
#########################
@app.route('/leer_Parametros_FV')
def leer_Parametros_FV():
    if 'logged_in' in session and session['logged_in']:        
        try:
            with open('/home/pi/PVControl+/Parametros_FV.py', 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return ''
    else:
        return redirect(url_for('login'))
        
@app.route('/guardar_Parametros_FV', methods=['POST'])
def guardar_Parametros_FV():
    if 'logged_in' in session and session['logged_in']:
        content = request.form['FV']
        with open('/home/pi/PVControl+/Parametros_FV1.py', 'w') as file:
            file.write(content)
        return render_template('index.html')
    else:
        return redirect(url_for('login'))
        
#############################
# Parametros_Web.js
# ###########################
@app.route('/leer_Parametros_Web')
def leer_Parametros_Web():
    if 'logged_in' in session and session['logged_in']:        
        try:
            with open('/home/pi/PVControl+/html/Parametros_Web.js', 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return ''
    else:
        return redirect(url_for('login'))

@app.route('/guardar_Parametros_Web', methods=['POST'])
def guardar_Parametros_Web():
    if 'logged_in' in session and session['logged_in']:    
        content = request.form['Web']
        with open('/home/pi/PVControl+/html/Parametros_Web.js', 'w') as file:
            file.write(content)
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


# Ruta para cargar la página principal
@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug=True)
    
