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
import copy

class DFS:
    """
    Classical Depth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior.
    """

    def __init__(self, level):
        self.level = level

    def search_floor_boombox(self, source):
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
                if self.level.is_wall((x+mx, y+my)) or self.level.has_box((x+mx, y+my)):
                    continue

                rec_explore((x+mx, y+my))

        rec_explore(source)
        verbose("DFS.search_floor : " + str(mark))
        return mark

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
        verbose("DFS.search_floor : " + str(mark))
        return mark
    
    
class GMC :
    """
    grapheMC des mouvements a priori possible quand une caisse est sur une case
    cette classe ne tient jamais compte de la position du personnage
    elle utilise seulement les postions des boites (après un éventuel update)
    et la position des cibles
    """
    def __init__(self, level, pos):
        self.targets = [(y,x) for (x,y) in level.targets] # Où sont les cibles
        self.boxes = [(y,x) for (x,y) in level.boxes]
        # verbose("Targets : " + str(self.targets))
        # verbose("Boxes :" + str(self.boxes))
        self.level = level
        # On implémente le grapheMC sous la forme d'un dictionnaire de successeurs
        self.boxes = []
        self.grapheMC = {} # grapheMC est le grapheMC des mouvements possibles des caisses
        self.grapheMCinverse = {} # grapheMC est le grapheMC des provenances possibles des caisses
        # self.puits = [] # Liste pour accuillir les puits (les noeuds qui n'ont pas de successeurs dans le grapheMC
        # self.interdits = [] # Liste des noeuds qui ne comportent aucun chemin vers une cible
        dfs = DFS(self.level) # Appel pour trouver l'intérieur du jeu (case accessibles par le personnage)
        self.ground = dfs.search_floor(pos) # case accessibles par le personnage . True / False
        self.height = len(self.ground) # hauteur du plateau de jeu mur compris
        self.width = len(self.ground[0]) # largeur du plateau de jeu mur compris
        self.buildgrapheMC() # construction du grapheMC des mouvement possibles
        self.update(level)
        self.possibles = set() # Contient les cases qui peuvent éventuellement être à l'origine d'un chemin vers une cible
        # La partie nocaisse pourrait être éventuellement supprimé
        self.nocaisse=[]
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
        """
        Mets à jour les position des boites après un mouvement de caisse
        A appeler dans le mouvement du perso level.move_player() dans les boites quand il pousse un boite -> player_status == 2
        """
        self.level = level
        self.boxes = []
        for x in range(self.height):
            for y in range(self.width):
                pos = x,y
                if self.level.has_box((y,x)):
                    self.boxes.append(pos)
        self.nocaisse = []
        # verbose(self.boxes)
        for position in self.boxes :
            self.nocaisse += self.autourCaisse(position)
            self.boolCaisse(position)
    
    def autourCaisse(self,position):
        """
        Construis autour d'une caisse les positions interdites sous la forme
        d'un tableau de positions [(x,y),...]
        Principe une caisse peut être bloquée  par une autre dans une composante (horizontale / verticale)
        si elles passent toutes deux d'un degré deux hypotétiquement à un degré 0 
        """
        t = []
        if position in self.grapheMC.keys() :
            if len(self.grapheMC[position]) == 2 :
                for s in self.grapheMC[position] :
                    if len(self.grapheMC[s]) == 2 and position in self.grapheMC[s] :
                        t.append(s)
        return t
    
    def boolCaisse(self,position):
        """
        Quelles sont les position qui interdise le voisinage de deux caisses ?
        retourne un tableau t de quatre booléens pour Droite Gauche Bas Haut
        True = "ok", False = "interdit de mettre une autre caisse"
        Appelé dans le level.aide() pour le renseignement des Highlight
        """
        # verbose("Autour de caisse : " + str(position))
        t = []
        tt = [True,True,True,True]
        t = self.autourCaisse(position)
        x,y = position
        for p in t :
            xx,yy = p
            if xx == x :
                if yy > y :
                    tt[0] = False
                else :
                    tt[1] = False
            if yy == y :
                if xx > x :
                    tt[2] = False
                else :
                    tt[3] = False
        # verbose("Interdit Droite Gauche Bas Haut : " + str(tt))
        return tt
      
        
        
    def __repr__(self) :
        """
        # Mur
        X Case depuis laquelle une caisse ne peut pas atteindre une cible
        * Ne pas mettre d'autre caisse (à noter : marquage ambigu dans le terminal)
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
        for y in range(self.height):
            for x in range(self.width):
                if (y,x) in self.nocaisse :
                    str[y] = str[y][:x] + '*' + str[y][x+1:]
                if (y,x) in self.boxes :
                    str[y] = str[y][:x] + '$' + str[y][x+1:]
        s= ''
        for k in str :
            s += k + '\n'
        s += '\n'  
        return s
    
        
            
        
        
        
        
        
        
        
    


