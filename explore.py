"""
Explorations for Sokoban.
Fill free to add new exploration code here.
"""

import pygame
from pygame.locals import *
import common as C
from utils import *
import queue
import heapq
from time import time
from math import sqrt


class DFS:
    """
    Classical Depth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior.
    """

    def __init__(self, level):
        self.level = level

    def search_floor(self, source):
        init_x, init_y = source

        # to remember which tiles have been visited or not
        mark = [[False for x in range(self.level.width)]
                for y in range(self.level.height)]

        def rec_explore(position):
            x, y = position
            if mark[y][x]:
                return

            # mark current position as visited
            mark[y][x] = True

            for d, (mx, my) in enumerate(C.DIRS):
                if self.level.is_wall((x+mx, y+my)):
                    continue

                rec_explore((x+mx, y+my))

        rec_explore(source)
        return mark
    
    
class File:
    ''' classe File
    création d'une instance File avec une liste
    '''
    def __init__(self):
        self.L = []
    
    def vide(self):
        return self.L == []
    
    def defiler(self):
        assert not self.vide(), "file vide"
        return self.L.pop(0)
    
    def enfiler(self, x):
        self.L.append(x)
    
    def taille(self):
        return len(self.L)

    def sommet(self):
        return self.L[0]

    def present(self, x):
        return x in self.L

    
class BFS:
    """
    Classical Breadth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior.
    """

    def __init__(self, level):
        self.level = level
        
        #f.enfiler(depart)
        #parent[depart] = None

    def voisins(self, pos):
        v = []
        x, y = pos
        #g = GMC(self.level, (y, x))
        for d, (mx, my) in enumerate(C.DIRS):
            (ox, oy) = (-mx, -my)
            #if x+mx >= 0 and x+mx < self.level.width and y+my >= 0 and y+my < self.level.height\
               #and x+ox >= 0 and x+ox < self.level.width and y+oy >= 0 and y+oy < self.level.height:
            
            if not (self.level.is_wall((x+mx, y+my)) or self.level.has_box((x+mx, y+my))):\
                   #and not (self.level.is_wall((x+ox, y+oy)) or self.level.has_box((x+ox, y+oy))):
            #if (x+mx, y+my) in g.possibles:
                v.append((x+mx, y+my))
        return v

    def search_floor(self, source):
        parent = {}
        sommet_visite = []
        f = File()
        f.enfiler(source)
        parent[source] = None
        
        while not f.vide():
            tmp = f.defiler()
            
            if tmp not in sommet_visite:
                sommet_visite.append(tmp)
                
            for voisin in self.voisins(tmp):
                
                if voisin not in sommet_visite and not f.present(voisin):
                    f.enfiler(voisin)
                    parent[voisin] = tmp
        
        return parent

    def chemin(self, end, parent):
        chemin = []
        courant = end
        while courant != None and courant in parent.keys():
            chemin = [courant] + chemin
            courant = parent[courant]
        return chemin

class Aide:
    """
    Cases accessibles
    """

    def __init__(self, level):
        self.level = level

    def search_mv(self, source):
        init_x, init_y = source

    
        # mark current position as visited
        mark[y][x] = True

        for d, (mx, my) in enumerate(C.DIRS):
            if self.level.is_wall((x+mx, y+my)):
                continue

            rec_explore((x+mx, y+my))

        rec_explore(source)
        return mark

class GMC :
    """
    grapheMC des mouvements a priori possible quand une caisse est sur une case
    """
    def __init__(self, level, pos):
        self.targets = [(y,x) for (x,y) in level.targets] # Où sont les cibles
        self.boxes = [(y,x) for (x,y) in level.boxes]
        verbose("Targets : " + str(self.targets))
        verbose("Boxes :" + str(self.boxes))
        self.level = level
        # On implémente le grapheMC sous la forme d'un dictionnaire de successeurs
        self.boxes = []
        self.grapheMC = {} # grapheMC est le grapheMC des mouvements possibles des caisses
        self.grapheMCinverse = {} # grapheMC est le grapheMC des provenances possibles des caisses
        self.puits = [] # Liste pour accuillir les puits (les noeuds qui n'ont pas de successeurs dans le grapheMC
        self.interdits = [] # Liste des noeuds qui ne comportent aucun chemin vers une cible
        dfs = DFS(self.level) # Appel pour trouver l'intérieur du jeu (case accessibles par le personnage)
        self.ground = dfs.search_floor(pos) # case accessibles par le personnage . True / False
        self.height = len(self.ground) # hauteur du plateau de jeu mur compris
        self.width = len(self.ground[0]) # largeur du plateau de jeu mur compris
        self.buildgrapheMC() # construction du grapheMC des mouvement possibles
        # self.reduce() # Transforme le grapheMC complet en un grapheMC permis
        self.update(level)
        self.possibles = set() # Contient les cases qui peuvent éventuellement
        # verbose(self.grapheMCinverse)
        for k in self.targets :
            pass
            self.possibles = self.possibles.union(self.dfsInv(k)) # Appel d'un dfs sur le grapheMC inverse depuis la cible.
        verbose("GMC :\n" + str(self))
        
        
    def buildgrapheMC(self):
        """
        La fonction construit le grapheMC des mouvement de caisse  possible.
        Pour bouger pouvoir bouger horizontalement, la caisse doit avoir des cases accessibles à gauche ou à droite.
        Pour bouger pouvoir bouger verticalement, la caisse doit avoir des cases accessibles en haut et en bas.
        """
        # Ajout des noeuds du graphe comme clés au dictionnaire
        for y in range(self.height):
            for x in range(self.width):
                if self.ground[y][x]:
                    self.grapheMC[(y,x)]= set()
        # Ajout des arcs au graphe
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.grapheMC.keys() and (y-1,x) in self.grapheMC.keys() and (y+1,x) in self.grapheMC.keys() :
                    self.grapheMC[(y,x)].add((y-1,x))
                    self.grapheMC[(y,x)].add((y+1,x))
                if (y,x) in self.grapheMC.keys() and (y,x-1)in self.grapheMC.keys() and (y,x+1) in self.grapheMC.keys() :
                    self.grapheMC[(y,x)].add((y,x-1))
                    self.grapheMC[(y,x)].add((y,x+1))
        # Transformation du graphe (le sens de chaque arc est inversé)
        for o,dd in self.grapheMC.items() :
            if not o in self.grapheMCinverse :
                    self.grapheMCinverse[o] = set()
            for d in dd :
                if not d in self.grapheMCinverse :
                    self.grapheMCinverse[d] = {o}
                else :
                    self.grapheMCinverse[d].add(o)
                    
    
    def dfsInv(self, destination):
        """
        Exploration DFS du graphe inversé en partant du point de destination
        Renvoit Les cases éventuelles qui peuvent faire que la caisse se retrouve sur la destination
        """
        verbose("dfs inverse depuis cible : " + str(destination))
        vus = set()
        def rec(pos):
            if pos not in vus :
                vus.add(pos)
                verbose(pos)
            for p in self.grapheMCinverse[(pos)] :
                if p not in vus :
                    rec(p)                  
        rec(destination)
        # verbose(str(vus))
        return vus
    
    def update(self,level) :
        self.level = level
        self.boxes = []
        for x in range(self.height):
            for y in range(self.width):
                pos = x,y
                if self.level.has_box((y,x)):
                    self.boxes.append(pos)
        # verbose('test' + str(self.boxes))
    
    def autourCaisse(self,position):
        """
        Construis autour d'une caisse les positions interdites
        retourne un tableau t de quatre booléens pour Haut Bas Gauche Droite
        """
        t = []
        if position in self.grapheMC.keys() :
            if len(self.grapheMC[position]) == 2 :
                for s in self.grapheMC[position] :
                    if len(self.grapheMC[s]) == 2 and position in self.grapheMC[s] :
                        t.append(s)
        return t
        
        
        
    def __repr__(self) :
        """
        # Mur
        X Case depuis laquelle une caisse ne peut pas atteindre une cible
        * Ne pas mettre d'autre caisse
        . target
        $ box
        """
        str = []
        for y in range(self.height):
            str.append('')
            for x in range(self.width):
                str[y] += '#'
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.grapheMC.keys() :
                    str[y] = str[y][:x] + 'X' + str[y][x+1:]
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.possibles :
                    str[y] = str[y][:x] + ' ' + str[y][x+1:]
                if (y,x) in self.targets :
                    str[y] = str[y][:x] + '.' + str[y][x+1:]
        # Marquage Caisse
        t = []
        # verbose(self.boxes)
        
        for position in self.boxes :
            t += self.autourCaisse(position)
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in t :
                    str[y] = str[y][:x] + '*' + str[y][x+1:]
                if (y,x) in self.boxes :
                    str[y] = str[y][:x] + '$' + str[y][x+1:]
        
        s= ''
        for k in str :
            s += k + '\n'
        s += '\n'  
        return s
    
    
    """
    def __repr__(self) :
        str = []
        for y in range(self.height):
            str.append('')
            for x in range(self.width):
                str[y] += '#'
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.grapheMC.keys() :
                    str[y] = str[y][:x] + 'X' + str[y][x+1:]
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.puits :
                    str[y] = str[y][:x] + '+' + str[y][x+1:] 
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.permitedgrapheMC.keys() :
                    str[y] = str[y][:x] + ' ' + str[y][x+1:]
        s= ''
        for k in str :
            s += k + '\n'
        s += '\n'  
        return s
    """
    
    def search_target(self, source):
        """
        Renvoit True si une recherche DFS depuis la source rencontre une target
        False sinon
        """
        init_x, init_y = source
        # to remember which tiles have been visited or not
        vus = []
        
        def rec(pos):
            if pos not in vus :
                vus.append(pos)
            for p in self.grapheMC[(pos)] :
                if p not in vus :
                    rec(p)          
        rec(source)
        r = False
        for k in vus :
            if k in self.targets:
             r = True
        verbose("GMS.search_target : " + str(r) + " -> " + str(vus))
        return r
    
    def reduce(self) :
        def puits(g):
                t = []
                for k in g.keys() :
                    if g[k] == set() and k not in self.targets :
                        t.append(k)
                return t
        
        self.permitedgrapheMC = copy.deepcopy(self.grapheMC) # permited grapheMC est le grapheMC des cases où on peut mettre la caisse sans être bloqué
        p = puits(self.grapheMC)
        self.puits = p
        # verbose("nombre de puits (non cibles) dans le grapheMC de départ : " + str(len(p)))
        # verbose("puits :" + str(p))
        # suppression des puits :
        def rec(p) :
            while len(p) > 0 :
                verbose("grapheMC permis : " + str(self.permitedgrapheMC))
                # verbose("puits :" + str(p))
                # verbose("suppression de " + str(len(p)) + " puits")
                for k in p :
                    self.permitedgrapheMC.pop(k) # suppression du puits
                    self.interdits.append(k)
                    for kk in self.permitedgrapheMC.keys() :
                        if k in self.permitedgrapheMC[kk] :
                            self.permitedgrapheMC[kk].remove(k)
                p = puits(self.permitedgrapheMC)
                verbose("puits :" + str(p))
        rec(p)
        verbose("grapheMC permis : " + str(self.permitedgrapheMC))
        verbose("Puits :" + str(self.interdits))
        for (x,y) in self.interdits :
            for d, (my, mx) in enumerate(C.DIRS):
                k = (x+mx,y+my)
                if k in self.permitedgrapheMC :
                    verbose(str(k))
                    if not(self.search_target(k)) :
                        self.permitedgrapheMC.pop(k) # suppression du puits
                        self.interdits.append(k)
                        for kk in self.permitedgrapheMC.keys() :
                            if k in self.permitedgrapheMC[kk] :
                                self.permitedgrapheMC[kk].remove(k)
