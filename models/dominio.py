from models.tda import ListaEnlazada
import time

class Plant:
    def __init__(self, nombre, hilera, posicion, litros, gramos):
        self.nombre = nombre
        self.hilera = hilera
        self.posicion = posicion
        self.litros = litros
        self.gramos = gramos

    def __str__(self):
        return f"{self.nombre} (H{self.hilera},P{self.posicion})"


class Drone:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.total_litros = 0
        self.total_gramos = 0

    def regar(self, planta):
        """Simula el riego de una planta"""
        time.sleep(0.1)  # simula tiempo (ajustable)
        self.total_litros += planta.litros
        self.total_gramos += planta.gramos
        return f"Riega {planta.nombre}"


class Invernadero:
    def __init__(self, nombre):
        self.nombre = nombre
        self.plantas = ListaEnlazada()
        self.drones = ListaEnlazada()
        self.planes = ListaEnlazada()

    def buscar_plan(self, nombre_plan):
        for plan_nombre, instrucciones in self.planes.iter():
            if plan_nombre == nombre_plan:
                return instrucciones
        return None

    def buscar_planta(self, hilera, posicion):
        for planta in self.plantas.iter():
            if planta.hilera == hilera and planta.posicion == posicion:
                return planta
        return None

    def simular_plan(self, instrucciones):
        acciones_por_segundo = []
        segundo = 1

        for instruccion in instrucciones.iter():
            planta = self.buscar_planta(instruccion["hilera"], instruccion["posicion"])
            if not planta:
                continue

            if self.drones.cabeza:
                dron = self.drones.cabeza.dato
                accion = dron.regar(planta)
                acciones_por_segundo.append((segundo, [(dron.nombre, accion)]))
                segundo += 1

        eficiencia = []
        for d in self.drones.iter():
            eficiencia.append((d.nombre, d.total_litros, d.total_gramos))

        return {
            "invernadero": self,
            "plan_nombre": "Simulación",
            "tiempo_optimo": segundo,
            "eficiencia_por_dron": ListaEnlazada(),
            "acciones_lista": acciones_por_segundo
        }
