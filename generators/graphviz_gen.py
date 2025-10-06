# Genera un archivo DOT que representa el estado de los TDAs (plan y cola de acciones) en un tiempo t

from graphviz import Digraph

class GraphvizGenerator:
    def generate_tda_graph(self, result, time_t=None, outpath='tda.dot'):
        dot = Digraph(comment='TDA State')
        # Nodo plan secuencial
        dot.node('plan', f'Plan: {result.plan_nombre}')

        # agregar secuencia completa
        seq_nodes = []
        # result.invernadero.planes: ListaSimple de (nombre, seq)
        for p in result.invernadero.planes.iter():
            if p[0] == result.plan_nombre:
                seq = p[1]
                break
        else:
            seq = []

        for i, item in enumerate(seq):
            nid = f's{i}'
            dot.node(nid, item)
            seq_nodes.append(nid)
        for i in range(len(seq_nodes)-1):
            dot.edge(seq_nodes[i], seq_nodes[i+1])
        if seq_nodes:
            dot.edge('plan', seq_nodes[0])

        # acciones en tiempos: mostrar hasta time_t if provided
        if time_t is not None:
            acciones = [a for a in result.acciones_lista if a[0] <= time_t]
        else:
            acciones = result.acciones_lista

        for segundo, acciones_seg in acciones:
            node_id = f't{segundo}'
            dot.node(node_id, f'T={segundo}s')
            for dr_name, accion in acciones_seg:
                act_id = f'{node_id}_{dr_name}_{accion}'
                dot.node(act_id, f'{dr_name}: {accion}')
                dot.edge(node_id, act_id)

        dot.save(outpath)
        return outpath