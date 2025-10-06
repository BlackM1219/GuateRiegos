# ===========================================
# TDA: Nodos básicos
# ===========================================

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


# ===========================================
# Lista Enlazada Simple
# ===========================================

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamano = 0

    def append(self, dato):
        """Agrega al final de la lista"""
        nuevo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo
            self.cola = nuevo
        else:
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self.tamano += 1

    def prepend(self, dato):
        """Agrega al inicio de la lista"""
        nuevo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo
            self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        self.tamano += 1

    def remove(self, dato):
        """Elimina el primer nodo con ese dato"""
        actual = self.cabeza
        anterior = None
        while actual:
            if actual.dato == dato:
                if anterior:
                    anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                if actual == self.cola:
                    self.cola = anterior
                self.tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def find(self, dato):
        """Busca un dato y lo devuelve si existe"""
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return actual.dato
            actual = actual.siguiente
        return None

    def iter(self):
        """Permite recorrer con for-in"""
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def __len__(self):
        return self.tamano

    def __getitem__(self, index):
        if index < 0 or index >= self.tamano:
            raise IndexError("Índice fuera de rango")
        actual = self.cabeza
        for _ in range(index):
            actual = actual.siguiente
        return actual.dato

    def __str__(self):
        return "[" + ", ".join(str(x) for x in self.iter()) + "]"


# ===========================================
# Pila (Stack) usando Lista Enlazada
# ===========================================

class Pila:
    def __init__(self):
        self.lista = ListaEnlazada()

    def push(self, dato):
        self.lista.prepend(dato)

    def pop(self):
        if not self.lista.cabeza:
            return None
        dato = self.lista.cabeza.dato
        self.lista.cabeza = self.lista.cabeza.siguiente
        self.lista.tamano -= 1
        if self.lista.tamano == 0:
            self.lista.cola = None
        return dato

    def peek(self):
        return self.lista.cabeza.dato if self.lista.cabeza else None

    def is_empty(self):
        return self.lista.tamano == 0

    def __len__(self):
        return len(self.lista)

    def __str__(self):
        return "Pila: " + str(self.lista)


# ===========================================
# Cola (Queue) usando Lista Enlazada
# ===========================================

class Cola:
    def __init__(self):
        self.lista = ListaEnlazada()

    def enqueue(self, dato):
        self.lista.append(dato)

    def dequeue(self):
        if not self.lista.cabeza:
            return None
        dato = self.lista.cabeza.dato
        self.lista.cabeza = self.lista.cabeza.siguiente
        self.lista.tamano -= 1
        if self.lista.tamano == 0:
            self.lista.cola = None
        return dato

    def is_empty(self):
        return self.lista.tamano == 0

    def __len__(self):
        return len(self.lista)

    def __str__(self):
        return "Cola: " + str(self.lista)
