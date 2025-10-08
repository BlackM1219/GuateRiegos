from flask import Flask, render_template, request, redirect, url_for, send_file
from parsers.xml_parser import XMLParser
from generators.salida_writer import SalidaWriter
from generators.graphviz_gen import GraphvizGenerator
import os


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    app.config["OUTPUT_FOLDER"] = os.path.join(os.getcwd(), "outputs")

    # Crear carpetas necesarias
    for folder in [app.config["UPLOAD_FOLDER"], app.config["OUTPUT_FOLDER"], "static"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Estructura global para almacenar datos y resultados
    datos = {"invernaderos": None, "ultimo_resultado": None}

    @app.route("/")
    def index():
        """Página principal"""
        return render_template("index.html", invernaderos=datos["invernaderos"])

    @app.route("/upload", methods=["POST"])
    def upload():
        """Carga y parsea el archivo XML"""
        if "file" not in request.files:
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error="No se seleccionó ningún archivo",
            )

        file = request.files["file"]

        if file.filename == "":
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error="No se seleccionó ningún archivo",
            )

        if file and file.filename.endswith(".xml"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            try:
                # Parsear XML
                parser = XMLParser(filepath)
                parser.parse()

                # Verificar que se cargaron invernaderos
                if parser.invernaderos and parser.invernaderos.tamano > 0:
                    datos["invernaderos"] = parser.invernaderos
                    print(f"✓ Se cargaron {parser.invernaderos.tamano} invernaderos")

                    # Preparar datos para JavaScript
                    inv_dict = {}
                    for inv in parser.invernaderos.iter():
                        planes_list = []
                        for plan_nombre, secuencia in inv.planes.iter():
                            planes_list.append(plan_nombre)
                        inv_dict[inv.nombre] = planes_list

                    import json

                    inv_json = json.dumps(inv_dict)

                    return render_template(
                        "index.html",
                        invernaderos=parser.invernaderos,
                        invernaderos_json=inv_json,
                        mensaje=f"Archivo cargado exitosamente - {parser.invernaderos.tamano} invernadero(s)",
                    )
                else:
                    return render_template(
                        "index.html",
                        invernaderos=None,
                        error="El archivo XML no contiene invernaderos válidos",
                    )
            except Exception as e:
                print(f"✗ Error al parsear: {str(e)}")
                import traceback

                traceback.print_exc()
                return render_template(
                    "index.html",
                    invernaderos=None,
                    error=f"Error al parsear XML: {str(e)}",
                )
        else:
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error="Por favor selecciona un archivo XML válido",
            )

    @app.route("/simulate", methods=["POST"])
    def simulate():
        """Ejecuta la simulación de un plan de riego"""
        invernadero_nombre = request.form.get("invernadero")
        plan_nombre = request.form.get("plan")

        print(f"Simulando: {invernadero_nombre} - {plan_nombre}")

        if not datos["invernaderos"]:
            return redirect(url_for("index"))

        # Buscar invernadero
        invernadero = None
        for inv in datos["invernaderos"].iter():
            if inv.nombre == invernadero_nombre:
                invernadero = inv
                break

        if not invernadero:
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error="Invernadero no encontrado",
            )

        # Verificar que el plan existe
        plan = invernadero.buscar_plan(plan_nombre)
        if not plan:
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error=f"Plan '{plan_nombre}' no encontrado",
            )

        # Ejecutar simulación
        try:
            resultados = invernadero.simular_plan(plan_nombre)
            if resultados:
                datos["ultimo_resultado"] = resultados
                print(
                    f"✓ Simulación completada: {resultados['tiempo_optimo']} segundos"
                )
                return render_template("report_invernadero.html", results=resultados)
            else:
                return render_template(
                    "index.html",
                    invernaderos=datos["invernaderos"],
                    error="Error: La simulación no produjo resultados",
                )
        except Exception as e:
            print(f"✗ Error en simulación: {str(e)}")
            import traceback

            traceback.print_exc()
            return render_template(
                "index.html",
                invernaderos=datos["invernaderos"],
                error=f"Error en simulación: {str(e)}",
            )

    @app.route("/generar_salida", methods=["POST"])
    def generar_salida():
        """Genera archivo XML de salida con los resultados"""
        if not datos["ultimo_resultado"]:
            return redirect(url_for("index"))

        try:
            writer = SalidaWriter()
            outpath = os.path.join(app.config["OUTPUT_FOLDER"], "salida.xml")
            writer.write(datos["ultimo_resultado"], outpath)
            print(f"✓ XML generado: {outpath}")
            return send_file(outpath, as_attachment=True, download_name="salida.xml")
        except Exception as e:
            print(f"✗ Error al generar XML: {str(e)}")
            import traceback

            traceback.print_exc()
            return f"<h3>Error al generar XML</h3><p>{str(e)}</p><a href='/'>Volver</a>"

    @app.route("/generar_grafo", methods=["POST"])
    def generar_grafo():
        """Genera gráfico Graphviz del estado de TDAs"""
        if not datos["ultimo_resultado"]:
            return redirect(url_for("index"))

        try:
            tiempo_t = request.form.get("tiempo_t")
            tiempo_t = int(tiempo_t) if tiempo_t else None

            gen = GraphvizGenerator()
            img_path = gen.generate_tda_graph(
                datos["ultimo_resultado"],
                time_t=tiempo_t,
                outpath=os.path.join("static", "tda_graph"),
            )

            if img_path:
                print(f"✓ Grafo generado: {img_path}")
                return render_template(
                    "graph_view.html",
                    image_path="tda_graph.png",
                    tiempo=tiempo_t,
                    results=datos["ultimo_resultado"],
                )
            else:
                return "<h3>Error: Graphviz no está instalado</h3><p>Instala Graphviz: <a href='https://graphviz.org/download/'>https://graphviz.org/download/</a></p><a href='/'>Volver</a>"
        except Exception as e:
            print(f"✗ Error al generar grafo: {str(e)}")
            import traceback

            traceback.print_exc()
            return f"<h3>Error al generar grafo</h3><p>{str(e)}</p><p>Asegúrate de tener Graphviz instalado</p><a href='/'>Volver</a>"

    @app.route("/ayuda")
    def ayuda():
        """Página de ayuda y acerca de"""
        return render_template("ayuda.html")

    return app
