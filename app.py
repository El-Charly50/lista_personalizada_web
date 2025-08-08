from flask import Flask, render_template, request, jsonify, send_file
from m3u_utils import descargar_m3u, parsear_m3u_completo, generar_m3u_filtrado, generar_txt
import io
import threading
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cargar_m3u', methods=['POST'])
def cargar_m3u():
    url = request.json.get('url')
    try:
        contenido = descargar_m3u(url)
        canales = parsear_m3u_completo(contenido)
        grupos = sorted(set(c['group'] for c in canales))
        return jsonify({'ok': True, 'grupos': grupos, 'canales': canales})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

@app.route('/filtrar_canales', methods=['POST'])
def filtrar_canales():
    data = request.json
    canales = data.get('canales', [])
    grupos = set(data.get('grupos', []))
    seleccionados = set(data.get('seleccionados', []))
    filtrados = [c for c in canales if c['group'] in grupos and c['name'] in seleccionados]
    return jsonify({'ok': True, 'filtrados': filtrados})

@app.route('/verificar_canales', methods=['POST'])
def verificar_canales():
    canales = request.json.get('canales', [])
    activos = []
    inactivos = []
    def check_channel(canal):
        try:
            resp = requests.head(canal['url'], timeout=5)
            if resp.status_code in [200, 206, 301, 302, 303, 307, 308]:
                return True
        except Exception:
            pass
        return False
    threads = []
    results = [None] * len(canales)
    def worker(idx, canal):
        results[idx] = check_channel(canal)
    for idx, canal in enumerate(canales):
        t = threading.Thread(target=worker, args=(idx, canal))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    for idx, canal in enumerate(canales):
        if results[idx]:
            activos.append(canal)
        else:
            inactivos.append(canal)
    return jsonify({'ok': True, 'activos': activos, 'inactivos': inactivos})

@app.route('/descargar_m3u', methods=['POST'])
def descargar_m3u_filtrado():
    canales = request.json.get('canales', [])
    m3u = generar_m3u_filtrado(canales)
    return send_file(io.BytesIO(m3u.encode('utf-8')), mimetype='audio/x-mpegurl', as_attachment=True, download_name='lista_filtrada.m3u')

@app.route('/descargar_txt', methods=['POST'])
def descargar_txt_filtrado():
    canales = request.json.get('canales', [])
    txt = generar_txt(canales)
    return send_file(io.BytesIO(txt.encode('utf-8')), mimetype='text/plain', as_attachment=True, download_name='lista_filtrada.txt')

if __name__ == '__main__':
    app.run(debug=True)
