import xml.etree.ElementTree as ET
from models.dominio import Invernadero, Planta, Dron
from models.tda import ListaEnlazada

class XMLParser:
    """Parser para archivos XML de configuración de invernaderos"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.drones_globales = ListaEnlazada()  # Drones disponibles globalmente
        self.invernaderos = ListaEnlazada()  # Lista de invernaderos cargados

    def parse(self):
        """Parsea el archivo XML y construye las estructuras de datos"""
        tree = ET.parse(self.filepath)
        root = tree.getroot()

        # 1. Parsear lista global de drones
        lista_drones = root.find("listaDrones")
        if lista_drones is not None:
            for nodo_dron in lista_drones.findall("dron"):
                dron = Dron(
                    id=nodo_dron.get("id"),
                    nombre=nodo_dron.get("nombre")
                )
                self.drones_globales.append(dron)

        # 2. Parsear invernaderos
        lista_invernaderos = root.find("listaInvernaderos")
        if lista_invernaderos is not None:
            for nodo_inv in lista_invernaderos.findall("invernadero"):
                inv = self._parsear_invernadero(nodo_inv)
                self.invernaderos.append(inv)

    def _parsear_invernadero(self, nodo_inv):
        """Parsea un nodo de invernadero completo"""
        inv = Invernadero(nodo_inv.get("nombre"))
        
        # Número de hileras y plantas por hilera
        num_hileras = nodo_inv.find("numeroHileras")
        if num_hileras is not None:
            inv.numero_hileras = int(num_hileras.text.strip())
        
        plantas_x_hilera = nodo_inv.find("plantasXhilera")
        if plantas_x_hilera is not None:
            inv.plantas_por_hilera = int(plantas_x_hilera.text.strip())

        # Parsear plantas (etiqueta correcta: listaPlantas)
        lista_plantas = nodo_inv.find("listaPlantas")
        if lista_plantas is not None:
            for nodo_planta in lista_plantas.findall("planta"):
                planta = Planta(
                    nombre=nodo_planta.text.strip(),
                    hilera=int(nodo_planta.get("hilera")),
                    posicion=int(nodo_planta.get("posicion")),
                    litros=int(nodo_planta.get("litrosAgua")),
                    gramos=int(nodo_planta.get("gramosFertilizante"))
                )
                inv.plantas.append(planta)

        # Parsear asignación de drones
        asignacion_drones = nodo_inv.find("asignacionDrones")
        if asignacion_drones is not None:
            for nodo_asig in asignacion_drones.findall("dron"):
                dron_id = nodo_asig.get("id")
                hilera_asignada = int(nodo_asig.get("hilera"))
                
                # Buscar el dron en la lista global y crear una copia
                dron_original = self._buscar_dron_global(dron_id)
                if dron_original:
                    # Crear nueva instancia para este invernadero
                    dron_copia = Dron(dron_original.id, dron_original.nombre)
                    dron_copia.hilera = hilera_asignada
                    inv.drones.append(dron_copia)

        # Parsear planes de riego (etiqueta correcta: planesRiego)
        planes_riego = nodo_inv.find("planesRiego")
        if planes_riego is not None:
            for nodo_plan in planes_riego.findall("plan"):
                nombre_plan = nodo_plan.get("nombre")
                texto_plan = nodo_plan.text.strip()
                
                # Parsear secuencia del plan (ej: "H1-P2, H2-P1, H2-P2")
                secuencia = self._parsear_secuencia_plan(texto_plan)
                inv.planes.append((nombre_plan, secuencia))

        return inv

    def _parsear_secuencia_plan(self, texto):
        """
        Convierte texto del plan en una lista de instrucciones
        Entrada: "H1-P2, H2-P1, H2-P2"
        Salida: ListaEnlazada con ["H1-P2", "H2-P1", "H2-P2"]
        """
        secuencia = ListaEnlazada()
        # Dividir por comas y limpiar espacios
        items = [item.strip() for item in texto.split(',')]
        for item in items:
            if item:  # Ignorar cadenas vacías
                secuencia.append(item)
        return secuencia

    def _buscar_dron_global(self, dron_id):
        """Busca un dron en la lista global por ID"""
        for dron in self.drones_globales.iter():
            if dron.id == dron_id:
                return dron
        return None