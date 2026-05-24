from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import json, os, uuid

app = Flask(__name__)
DB_FILE = 'switches.json'


# Загрузка и автоматическое исправление ID
def load_switches():
    switches = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                switches = json.load(f)
        except:
            switches = []

    # Исправляем записи без ID, чтобы не было ошибки KeyError
    updated = False
    for s in switches:
        if 'id' not in s:
            s['id'] = str(uuid.uuid4())
            updated = True

    if updated:
        save_switches(switches)
    return switches


def save_switches(switches):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(switches, f, ensure_ascii=False, indent=4)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('login') == "admin" and data.get('password') == "prodazi2026":
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', switches=load_switches())


@app.route('/add_switch', methods=['POST'])
def add_switch():
    sws = load_switches()
    sws.append({
        "id": str(uuid.uuid4()),
        "street": request.form.get('street'),
        "ip": request.form.get('ip')
    })
    save_switches(sws)
    return redirect(url_for('dashboard'))


@app.route('/edit_switch', methods=['POST'])
def edit_switch():
    sw_id = request.form.get('id')
    sws = load_switches()
    for s in sws:
        if s.get('id') == sw_id:
            s['street'] = request.form.get('street')
            s['ip'] = request.form.get('ip')
            break
    save_switches(sws)
    return redirect(url_for('dashboard'))


@app.route('/delete_switch/<sw_id>')
def delete_switch(sw_id):
    sws = load_switches()
    save_switches([s for s in sws if s.get('id') != sw_id])
    return redirect(url_for('dashboard'))


@app.route('/export')
def export_data():
    return send_file(DB_FILE, as_attachment=True)


if __name__ == '__main__':
    # host='0.0.0.0' открывает доступ для всех устройств в сети
    app.run(debug=True, host='0.0.0.0', port=5000)
