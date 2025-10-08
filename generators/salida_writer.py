import xml.etree.ElementTree as ET
from xml.dom import minidom


class SalidaWriter:
    """Escritor de archivos XML de salida"""

    def write(self, result, outpath="salida.xml"):
        """
        Genera el archivo XML de salida con los resultados de la simulación
        según el formato especificado en el documento
        """
        # Crear estructura XML
        root = ET.Element("datosSalida")
        lista_inv = ET.SubElement(root, "listaInvernaderos")

        # Datos del invernadero
        inv_elem = ET.SubElement(
            lista_inv, "invernadero", {"nombre": result["invernadero"].nombre}
        )
        lista_planes = ET.SubElement(inv_elem, "listaPlanes")

        # Datos del plan
        plan_elem = ET.SubElement(
            lista_planes, "plan", {"nombre": result["plan_nombre"]}
        )

        # Tiempo óptimo
        tiempo_elem = ET.SubElement(plan_elem, "tiempoOptimoSegundos")
        tiempo_elem.text = str(result["tiempo_optimo"])

        # Calcular totales de agua y fertilizante
        total_agua = 0
        total_fertilizante = 0

        # Eficiencia de drones
        eficiencia_elem = ET.SubElement(plan_elem, "eficienciaDronesRegadores")
        for dron in result["invernadero"].drones.iter():
            ET.SubElement(
                eficiencia_elem,
                "dron",
                {
                    "nombre": dron.nombre,
                    "litrosAgua": str(dron.litros_total),
                    "gramosFertilizante": str(dron.gramos_total),
                },
            )
            total_agua += dron.litros_total
            total_fertilizante += dron.gramos_total

        # Totales
        agua_elem = ET.SubElement(plan_elem, "aguaRequeridaLitros")
        agua_elem.text = str(total_agua)

        fertilizante_elem = ET.SubElement(plan_elem, "fertilizanteRequeridoGramos")
        fertilizante_elem.text = str(total_fertilizante)

        # Instrucciones detalladas
        instrucciones_elem = ET.SubElement(plan_elem, "instrucciones")
        for segundo, acciones in result["acciones_lista"]:
            tiempo_elem = ET.SubElement(
                instrucciones_elem, "tiempo", {"segundos": str(segundo)}
            )
            for dron_nombre, accion in acciones:
                ET.SubElement(
                    tiempo_elem, "dron", {"nombre": dron_nombre, "accion": accion}
                )

        # Formatear y guardar XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(xml_str)

        return outpath
