from models.tda import ListaEnlazada

class Planta:
    """Representa una planta en el invernadero"""
    def __init__(self, nombre, hilera, posicion, litros, gramos):
        self.nombre = nombre
        self.hilera = hilera
        self.posicion = posicion
        self.litros = litros
        self.gramos = gramos

    def __str__(self):
        return f"{self.nombre} (H{self.hilera}P{self.posicion})"


class Dron:
    """Representa un dron regador"""
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera = None  # Hilera asignada
        self.posicion_actual = 1  # Todos inician en posición 1
        self.litros_total = 0  # Agua acumulada
        self.gramos_total = 0  # Fertilizante acumulado

    def __str__(self):
        return f"{self.nombre} (Hilera {self.hilera})"


class Invernadero:
    """Representa un invernadero con sus plantas, drones y planes de riego"""
    def __init__(self, nombre):
        self.nombre = nombre
        self.numero_hileras = 0
        self.plantas_por_hilera = 0
        self.plantas = ListaEnlazada()  # Lista de todas las plantas
        self.drones = ListaEnlazada()  # Lista de drones asignados
        self.planes = ListaEnlazada()  # Lista de tuplas (nombre_plan, secuencia)

    def buscar_plan(self, nombre_plan):
        """Busca un plan de riego por nombre"""
        for plan_nombre, secuencia in self.planes.iter():
            if plan_nombre == nombre_plan:
                return secuencia
        return None

    def buscar_planta(self, hilera, posicion):
        """Busca una planta específica por hilera y posición"""
        for planta in self.plantas.iter():
            if planta.hilera == hilera and planta.posicion == posicion:
                return planta
        return None

    def buscar_dron_por_hilera(self, hilera):
        """Busca el dron asignado a una hilera específica"""
        for dron in self.drones.iter():
            if dron.hilera == hilera:
                return dron
        return None

    def reiniciar_drones(self):
        """Reinicia las posiciones y totales de todos los drones"""
        for dron in self.drones.iter():
            dron.posicion_actual = 1
            dron.litros_total = 0
            dron.gramos_total = 0

    def simular_plan(self, plan_nombre):
        """
        Simula la ejecución de un plan de riego siguiendo las reglas:
        1. Los drones demoran 1 segundo en moverse 1 metro
        2. Los drones demoran 1 segundo en regar
        3. Solo 1 dron puede regar a la vez
        4. Se debe seguir el orden del plan
        """
        # Reiniciar drones antes de la simulación
        self.reiniciar_drones()
        
        # Obtener secuencia del plan
        secuencia = self.buscar_plan(plan_nombre)
        if not secuencia:
            return None

        # Estructura para almacenar acciones por segundo
        acciones_por_tiempo = {}  # {segundo: [(nombre_dron, accion), ...]}
        
        # Control de tiempo para cada dron y para el riego global
        tiempo_disponible_dron = {}  # Cuándo estará libre cada dron
        tiempo_riego_global = 0  # Cuándo se podrá regar nuevamente (constraint de 1 riego a la vez)
        
        # Inicializar tiempos de drones
        for dron in self.drones.iter():
            tiempo_disponible_dron[dron.nombre] = 1

        def agregar_accion(segundo, nombre_dron, accion):
            """Helper para agregar una acción en un segundo específico"""
            if segundo not in acciones_por_tiempo:
                acciones_por_tiempo[segundo] = []
            acciones_por_tiempo[segundo].append((nombre_dron, accion))

        # Procesar cada instrucción del plan
        for entrada in secuencia.iter():
            # Parsear entrada tipo "H1-P2"
            try:
                partes = entrada.replace('H', '').replace('P', '').replace(' ', '').split('-')
                hilera = int(partes[0])
                posicion = int(partes[1])
            except:
                continue  # Ignorar entradas mal formadas

            # Buscar dron y planta correspondientes
            dron = self.buscar_dron_por_hilera(hilera)
            planta = self.buscar_planta(hilera, posicion)
            
            if not dron or not planta:
                continue

            # Calcular tiempo de movimiento
            distancia = abs(dron.posicion_actual - posicion)
            inicio_movimiento = tiempo_disponible_dron[dron.nombre]
            
            # Registrar movimiento (cada metro = 1 segundo)
            tiempo_actual = inicio_movimiento
            pos_actual = dron.posicion_actual
            
            if distancia > 0:
                # Determinar dirección
                if posicion > pos_actual:
                    # Moverse hacia adelante
                    for p in range(pos_actual + 1, posicion + 1):
                        agregar_accion(tiempo_actual, dron.nombre, f"Adelante (H{hilera}P{p})")
                        tiempo_actual += 1
                else:
                    # Moverse hacia atrás
                    for p in range(pos_actual - 1, posicion - 1, -1):
                        agregar_accion(tiempo_actual, dron.nombre, f"Atras (H{hilera}P{p})")
                        tiempo_actual += 1
            
            # Actualizar posición del dron
            dron.posicion_actual = posicion
            
            # El dron llega en tiempo_actual, pero debe esperar si hay otro regando
            tiempo_llegada = tiempo_actual
            tiempo_inicio_riego = max(tiempo_llegada, tiempo_riego_global)
            
            # Si hay espera, registrar "Esperar"
            if tiempo_inicio_riego > tiempo_llegada:
                for t in range(tiempo_llegada, tiempo_inicio_riego):
                    agregar_accion(t, dron.nombre, "Esperar")
            
            # Registrar riego
            agregar_accion(tiempo_inicio_riego, dron.nombre, "Regar")
            
            # Actualizar totales del dron
            dron.litros_total += planta.litros
            dron.gramos_total += planta.gramos
            
            # Actualizar tiempos (riego dura 1 segundo)
            tiempo_disponible_dron[dron.nombre] = tiempo_inicio_riego + 1
            tiempo_riego_global = tiempo_inicio_riego + 1

        # Tiempo óptimo es el máximo tiempo usado
        tiempo_optimo = max(tiempo_disponible_dron.values()) if tiempo_disponible_dron else 0

        # Convertir diccionario a lista ordenada
        acciones_lista = []
        for segundo in sorted(acciones_por_tiempo.keys()):
            acciones_lista.append((segundo, acciones_por_tiempo[segundo]))

        # Construir resultado
        resultado = {
            'invernadero': self,
            'plan_nombre': plan_nombre,
            'tiempo_optimo': tiempo_optimo,
            'acciones_lista': acciones_lista
        }

        return resultado

    def __str__(self):
        return f"Invernadero: {self.nombre} ({self.numero_hileras} hileras x {self.plantas_por_hilera} plantas)"