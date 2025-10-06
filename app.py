from flask import Flask, render_template, request, redirect, send_file
from parsers.xml_parser import XMLParser
import os

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    estructura = {"invernaderos": None}

    @app.route('/')
    def index():
        return render_template('index.html', data=estructura["invernaderos"])

    @app.route('/upload', methods=['POST'])
    def upload():
        file = request.files['file']
        if file and file.filename.endswith('.xml'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            parser = XMLParser(filepath)
            parser.parse()
            estructura["invernaderos"] = parser.invernaderos
            return render_template('index.html', data=parser.invernaderos)
        else:
            return render_template('index.html', data=None)

    @app.route('/simulate', methods=['POST'])
    def simulate():
        invernadero_name = request.form.get("invernadero")
        plan_name = request.form.get("plan")

        if not estructura["invernaderos"]:
            return redirect('/')

        for inv in estructura["invernaderos"].iter():
            if inv.nombre == invernadero_name:
                plan = inv.buscar_plan(plan_name)
                if not plan:
                    return render_template('index.html', data=estructura["invernaderos"])
                resultados = inv.simular_plan(plan)
                return render_template('report_invernadero.html', results=resultados)
        return redirect('/')

    return app
