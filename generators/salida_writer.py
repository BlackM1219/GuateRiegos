import xml.etree.ElementTree as ET

class SalidaWriter:
    def write(self, result, outpath):
        # result: objeto con invernadero, plan_nombre, tiempo_optimo, eficiencia_por_dron (ListaSimple), acciones_lista
        root = ET.Element('datosSalida')
        listaInv = ET.SubElement(root, 'listaInvernaderos')
        inv_el = ET.SubElement(listaInv, 'invernadero', {'nombre': result.invernadero.nombre})
        listaPlanes = ET.SubElement(inv_el, 'listaPlanes')
        plan_el = ET.SubElement(listaPlanes, 'plan', {'nombre': result.plan_nombre})
        ET.SubElement(plan_el, 'tiempoOptimoSegundos').text = str(result.tiempo_optimo)

        # agua y fertilizante totales
        total_agua = 0.0
        total_gramos = 0.0
        eficiencia_el = ET.SubElement(plan_el, 'eficienciaDronesRegadores')

        for d in result.invernadero.drones.iter():
            ET.SubElement(eficiencia_el, 'dron', {
                'nombre': d.nombre,
                'litrosAgua': str(d.litros_total),
                'gramosFertilizante': str(d.gramos_total)
            })
            total_agua += d.litros_total
            total_gramos += d.gramos_total

        ET.SubElement(plan_el, 'aguaRequeridaLitros').text = str(total_agua)
        ET.SubElement(plan_el, 'fertilizanteRequeridoGramos').text = str(total_gramos)

        instr_el = ET.SubElement(plan_el, 'instrucciones')
        for segundo, acciones in result.acciones_lista:
            tiempo_el = ET.SubElement(instr_el, 'tiempo', {'segundos': str(segundo)})
            for dr_name, accion in acciones:
                ET.SubElement(tiempo_el, 'dron', {'nombre': dr_name, 'accion': accion})

        tree = ET.ElementTree(root)
        tree.write(outpath, encoding='utf-8', xml_declaration=True)
        return outpath