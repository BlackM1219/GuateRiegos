from graphviz import Digraph


class GraphvizGenerator:
    """Generador de gráficos Graphviz para visualizar TDAs"""

    def generate_tda_graph(self, result, time_t=None, outpath="static/tda_graph"):
        """
        Genera un grafo mostrando el estado de los TDAs en un tiempo t
        - Plan de riego (secuencia)
        - Acciones ejecutadas hasta el tiempo t
        """
        dot = Digraph(comment="Estado de TDAs", format="png")
        dot.attr(rankdir="TB", size="10,8")
        dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue")

        # Nodo principal del plan
        dot.node(
            "plan",
            f'Plan: {result["plan_nombre"]}',
            fillcolor="gold",
            fontsize="14",
            fontname="Arial Bold",
        )

        # Obtener secuencia del plan
        secuencia_plan = result["invernadero"].buscar_plan(result["plan_nombre"])

        if secuencia_plan:
            # Crear nodos para cada elemento de la secuencia
            prev_node = "plan"
            idx = 0
            for item in secuencia_plan.iter():
                node_id = f"seq_{idx}"
                dot.node(node_id, item, fillcolor="lightyellow")
                dot.edge(prev_node, node_id)
                prev_node = node_id
                idx += 1
                # Limitar a 15 nodos para no saturar
                if idx >= 15:
                    dot.node("seq_more", "...más elementos", fillcolor="lightgray")
                    dot.edge(prev_node, "seq_more")
                    break

        # Filtrar acciones hasta tiempo t (si se especifica)
        acciones_mostrar = result["acciones_lista"]
        if time_t is not None:
            acciones_mostrar = [
                (s, acc) for s, acc in result["acciones_lista"] if s <= time_t
            ]

        # Crear subgrafo para acciones por tiempo
        if acciones_mostrar:
            dot.node(
                "acciones_title",
                "Acciones por Tiempo",
                fillcolor="lightgreen",
                fontsize="12",
                fontname="Arial Bold",
            )

            # Limitar a los primeros 10 segundos para no saturar el grafo
            for segundo, acciones in acciones_mostrar[:10]:
                tiempo_id = f"tiempo_{segundo}"
                dot.node(
                    tiempo_id, f"Segundo {segundo}", fillcolor="orange", shape="ellipse"
                )
                dot.edge("acciones_title", tiempo_id)

                # Agregar acciones de cada dron en ese segundo
                for idx, (dron_nombre, accion) in enumerate(acciones):
                    accion_id = f"t{segundo}_a{idx}"
                    label = f"{dron_nombre}\\n{accion}"
                    dot.node(
                        accion_id, label, fillcolor="white", shape="note", fontsize="10"
                    )
                    dot.edge(tiempo_id, accion_id)

            # Si hay más acciones, indicarlo
            if len(acciones_mostrar) > 10:
                dot.node(
                    "more_actions",
                    f"... {len(acciones_mostrar) - 10} segundos más",
                    fillcolor="lightgray",
                    shape="plaintext",
                )
                dot.edge("acciones_title", "more_actions")

        # Información del tiempo
        if time_t:
            dot.node(
                "time_info",
                f"Visualizando hasta t={time_t}s",
                fillcolor="pink",
                shape="note",
            )

        # Guardar archivo
        try:
            dot.render(outpath, cleanup=True)
            return f"{outpath}.png"
        except Exception as e:
            print(f"Error al generar grafo: {e}")
            # Intentar guardar solo el DOT sin renderizar
            dot.save(f"{outpath}.dot")
            return None
