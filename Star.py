#
# Implementa la simulacion de un TRIS/TRAS
#
# Elaboro: Edgar Daniel Rodriguez Herrera
#

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation
import random

class AlgoritmoTrisTras(Model):
    #se ejecuta por cada proceso/modelo que se asocia con cada nodo del grafo
    #Esta clase desciende de la clase Model e implementa los metodos
    #"init()" y "receive()", que en la clase madre se definen como abstractos
    def init(self):
        #Aqui se definen e inicializan los atributos particulares del algoritmo
        print ("Inicio funciones", self.id)
        print("Mis vecinos son: ", end=" ")
        for neighbor in self.neighbors:
            if self.id != 1:
                self.sucesor = self.neighbors[0]
            print(neighbor, end=" ")
        #print("\n")

        #solo los nodos diferentes del nodo central pueden tomar la decision
        if self.id != 1:
            # 0 -> no, 1 -> si
            decision = random.randint(0, 1)
            if decision == 1:
                #se agrega el nodo a la lista de decisiones
                decisiones.append(self.id)
            print("\nDecision tris: ", decision, "\n")
        #para el nodo 1,
        else:
            print("\n")
            #se inicializa un contador de recursos disponibles
            self.recursos = random.randint(1, 5)
            #y un contador de peticiones TRIS que recibe
            self.peticiones = 0

    def receive(self, event):
        # Aqui se definen las acciones concretas que deben ejecutarse cuando se
        # recibe un evento
        print("T= ", self.clock, " Nodo [", self.id, "] Recibo :", event.getName(), "desde [", event.getSource(), "]")
        print("Mensajes transmitidos: ", event.counter)
        #si es el evento semilla
        if event.getName() == "INICIA":
            #name, time, target, source, counter
            newevent = Event("TRIS", self.clock + 1, self.sucesor, self.id, event.counter+1)
            #manda un TRIS al nodo 1
            self.transmit(newevent)
        #si el nodo 1 recibe un tris
        elif event.getName() == "TRIS":
            print("Nodo [", self.id, "] Recursos disponibles: ", self.recursos)
            #aumenta el numero de peticiones
            self.peticiones += 1
            print("Nodo [", self.id, "] Peticiones TRIS atendidas: ", self.peticiones)
            #si tiene recursos disponibles
            if self.recursos > 0:
                #decrementa un recurso
                self.recursos -= 1
                print("Nodo [", self.id, "] Recursos restantes: ", self.recursos)
                #y envia TRAS al nodo que manda la solicitud
                newevent = Event("TRAS", self.clock + 1, event.source, self.id, event.counter+1)
                self.transmit(newevent)
            #si NO tiene recursos disponibles
            else:
                print("Nodo [", self.id, "] Ya no tengo recursos!")
                #envia TRUS al nodo que manda la solicitud
                newevent = Event("TRUS", self.clock + 1, event.source, self.id, event.counter+1)
                self.transmit(newevent)
        #si los nodos de la periferia reciben un TRAS del nodo 1
        elif event.getName() == "TRAS":
            #si aun hay nodos con peticiones TRIS
            if len(decisiones)>0:
                if len(decisiones)>1:
                    #quitamos el primer nodo (ya atendido) de la lista
                    decisiones.pop(0)
                    print("Decisiones tris restantes: ", decisiones, "\n")
                    #y el proximo nodo de la lista manda TRIS al nodo 1
                    newevent = Event("TRIS", self.clock + 1, event.source, decisiones[0], event.counter + 1)
                    self.transmit(newevent)
            #si se atendio el ultimo nodo de la lista
            else:
                print("Ya no existen peticiones TRIS!")
        #si los nodos de la periferia reciben un TRUS del nodo 1
        elif event.getName() == "TRUS":
            print("[", self.id, "] Ya NO existen recursos!")
# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion
if len(sys.argv) != 2:
   print ("Por favor proporcione el nombre de la grafica de comunicaciones")
   raise SystemExit(1)

# se crea una lista en donde se van guardando las decisiones de peticion tris
decisiones= []
maxtime= 20
experiment = Simulation(sys.argv[1], maxtime)#filename, maxtime

# imprime lista de nodos que se extraen del archivo
# experiment.graph[indice+1 == nodo] == vecino
print("Lista de nodos: ", experiment.graph)

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = AlgoritmoTrisTras()
    experiment.setModel(m, i)

# imprime la lista de decisiones
print("Decisiones tris: ", decisiones, "\n")
# de esta lista se elige al primer nodo para que sea el evento semilla
# inserta un evento semilla en la agenda y arranca
#si hay almenos 1 elemento con peticion TRIS
if len(decisiones)>0:
    seed = Event("INICIA", 0.0, decisiones[0], decisiones[0], 0)
    #name, time, target, source, counter, recursos
    experiment.init(seed)
    experiment.run()
    decisiones.clear()
else:
    print("No hay peticiones TRIS!")
    exit(1)
