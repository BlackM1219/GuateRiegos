from models.tda import ListaSimple
from models.dominio import Invernadero

class Simulator:
    def __init__(self, data_lista):
        # data_lista: ListaSimple de Invernadero
        self.data = data_lista

    def find_invernadero(self, nombre):
        for inv in self.data.iter():
            if inv.nombre == nombre:
                return inv
        return None

    def run_plan(self, invernadero_nombre, plan_nombre):
        inv = self.find_invernadero(invernadero_nombre)
        if not inv:
            raise ValueError('Invernadero no encontrado')
        plan_seq = inv.obtener_plan(plan_nombre)
        if not plan_seq:
            raise ValueError('Plan no encontrado')

        # resultado: estructura dict-like (no dict?) We'll construct an object using simple classes
        class Result:
            pass
        res = Result()
        res.invernadero = inv
        res.plan_nombre = plan_nombre
        res.tiempo_optimo = 0
        res.acciones_por_segundo = ListaSimple()  # cada elemento: (segundo, lista de (drone_nombre, accion))
        res.eficiencia_por_dron = ListaSimple()

        # keep global clock, and ensure only 1 dron riega a la vez across greenhouse
        segundos = 0

        # helper: get drone by hilera
        drone_map = {}
        for d in inv.drones.iter():
            drone_map[d.hilera] = d

        # We'll iterate the plan sequence in order.
        # For each plan entry e.g., 'H1-P2', parse hilera and posicion.

        # To respect movement times and the constraint "only one drone can water at a time",
        # we will schedule actions incrementally: for each target, compute movement time for its drone (may overlap with other drones' movement),
        # but watering is exclusive and must wait until drone has arrived and no other watering happening.

        # We'll maintain for each drone the available_time (when it becomes free to start next action)
        drone_available = {}
        for d in inv.drones.iter():
            drone_available[d.nombre] = 1  # time starts at 1 according to example

        watering_busy_until = 0

        # For readability create a simple append helper to acciones_por_segundo
        def add_action(segundo, drone_name, accion):
            # find if segundo exists in res.acciones_por_segundo; if not append new
            found = None
            for item in res.acciones_por_segundo.iter():
                if item[0] == segundo:
                    found = item
                    break
            if not found:
                res.acciones_por_segundo.append((segundo, ListaSimple()))
                found = None
                for item in res.acciones_por_segundo.iter():
                    if item[0] == segundo:
                        found = item
                        break
            # found[1] is ListaSimple
            found[1].append((drone_name, accion))

        # process sequence
        for entry in plan_seq:
            # parse like H1-P2
            try:
                part = entry.replace('H', '').replace('P', '').split('-')
                hilera = int(part[0])
                posicion = int(part[1])
            except Exception:
                # skip malformed
                continue

            drone = inv.drone_por_hilera(hilera)
            if not drone:
                continue
            # movement time from current drone position to target
            move_time = abs(drone.posicion_actual - posicion)
            # drone can start moving when its available
            start_move_at = drone_available[drone.nombre]
            # we schedule movement: each meter = 1 second; we record actions per second for that drone
            cur_pos = drone.posicion_actual
            time_cursor = start_move_at
            step = 1 if posicion > cur_pos else -1
            for p in range(cur_pos + step, posicion + step, step):
                # move one meter
                add_action(time_cursor, drone.nombre, f'Adelante (H{hilera}P{p})' if step==1 else f'Atras (H{hilera}P{p})')
                time_cursor += 1
            # update drone position and its available time
            drone.posicion_actual = posicion
            drone_available[drone.nombre] = time_cursor

            # watering must wait until drone has arrived and until no other watering in progress
            start_watering = max(drone_available[drone.nombre], watering_busy_until)
            # schedule watering (1 second)
            add_action(start_watering, drone.nombre, 'Regar')
            # update totals
            plant = inv.plantas_por_hilera_pos(hilera, posicion)
            if plant:
                drone.litros_total += plant.litros
                drone.gramos_total += plant.gramos
            # update times
            drone_available[drone.nombre] = start_watering + 1
            watering_busy_until = start_watering + 1
            segundos = max(segundos, watering_busy_until)

        # After plan, drones return to inicio (posicion 1)
        for d in inv.drones.iter():
            if d.posicion_actual != 1:
                start_move = drone_available[d.nombre]
                cur_pos = d.posicion_actual
                time_cursor = start_move
                step = -1 if cur_pos > 1 else 1
                for p in range(cur_pos + step, 1 + step, step):
                    add_action(time_cursor, d.nombre, f'Atras (H{d.hilera}P{p})' if step==-1 else f'Adelante (H{d.hilera}P{p})')
                    time_cursor += 1
                d.posicion_actual = 1
                drone_available[d.nombre] = time_cursor
                segundos = max(segundos, time_cursor)

        res.tiempo_optimo = segundos

        # eficiencia por dron
        for d in inv.drones.iter():
            res.eficiencia_por_dron.append((d.nombre, d.litros_total, d.gramos_total))

        # convert acciones_por_segundo ListaSimple to a list-like structure for writers/templates
        # We'll create a simple list: list of (segundo, list of (drone_name, accion)) by iterating
        acciones = []
        for item in res.acciones_por_segundo.iter():
            segundo = item[0]
            lista_acc = []
            for x in item[1].iter():
                lista_acc.append(x)
            acciones.append((segundo, lista_acc))
        res.acciones_lista = acciones

        return res