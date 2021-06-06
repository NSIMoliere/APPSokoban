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
from explore import *

   
class GMC :
    """
    grapheMC des mouvements a priori possible quand une caisse est sur une case
    cette classe ne tient jamais compte de la position du personnage
    elle utilise seulement les postions des boites (après un éventuel update)
    et la position des cibles
    """
    def __init__(self, level, pos):
        self.targets = level.targets # Où sont les cibles
        self.boxes = level.boxes
        #print("Targets : " + str(self.targets))
        #print("Boxes :" + str(self.boxes))
        self.level = level
        # On implémente le grapheMC sous la forme d'un dictionnaire de successeurs
        self.grapheMC = {} # grapheMC est le grapheMC des mouvements possibles des caisses
        self.grapheMCinverse = {} # grapheMC est le grapheMC des provenances possibles des caisses
        dfs = DFS(self.level) # Appel pour trouver l'intérieur du jeu (case accessibles par le personnage)
        self.ground = dfs.search_floor(pos) # case accessibles par le personnage . True / False
        self.height = len(self.ground) # hauteur du plateau de jeu mur compris
        self.width = len(self.ground[0]) # largeur du plateau de jeu mur compris
        self.buildgrapheMC() # construction du grapheMC des mouvement possibles
        self.update(level)
        self.possibles = set() # Contient les cases qui peuvent éventuellement être à l'origine d'un chemin vers une cible        
        for k in self.targets :
            self.possibles = self.possibles.union(self.dfsInv(k)) # Appel d'un dfs sur le grapheMC inverse depuis la cible.
        print(self)
        
        
    def buildgrapheMC(self):
        """
        La fonction construit le grapheMC des mouvement de caisse  possible.
        Pour bouger pouvoir bouger horizontalement, la caisse doit avoir des cases accessibles à gauche ou à droite.
        Pour bouger pouvoir bouger verticalement, la caisse doit avoir des cases accessibles en haut et en bas.
        """
        # Dictionnaire des successeurs
        # Ajout des noeuds du graphe comme clés au dictionnaire
        for y in range(self.height):
            for x in range(self.width):
                if self.ground[y][x]:
                    self.grapheMC[(x,y)]= set()
        # Ajout des arcs au graphe 
        for y in range(self.height):
            for x in range(self.width):
                if (x,y) in self.grapheMC.keys() and (x,y-1) in self.grapheMC.keys() and (x,y+1) in self.grapheMC.keys() :
                    self.grapheMC[(x,y)].add((x,y-1))
                    self.grapheMC[(x,y)].add((x,y+1))
                if (x,y) in self.grapheMC.keys() and (x-1,y)in self.grapheMC.keys() and (x+1,y) in self.grapheMC.keys() :
                    self.grapheMC[(x,y)].add((x-1,y))
                    self.grapheMC[(x,y)].add((x+1,y))
        # Transformation du graphe (le sens de chaque arc est inversé)
        # Dictionnaire des prédécesseurs
        for o,dd in self.grapheMC.items() : # o origine # dd : ensemble des destinations
            if not o in self.grapheMCinverse :
                    self.grapheMCinverse[o] = set()
            for d in dd : # destination
                if not d in self.grapheMCinverse : # inversement du dictionnaire
                    self.grapheMCinverse[d] = {o}
                else :
                    self.grapheMCinverse[d].add(o)
                    
    
    def dfsInv(self, destination):
        """
        Exploration DFS du graphe inversé en partant du point de destination
        Renvoit Les cases éventuelles qui peuvent faire que la caisse se retrouve sur la destination
        """
        # verbose("dfs inverse depuis cible : " + str(destination))
        vus = set()
        def rec(pos):
            if pos not in vus :
                vus.add(pos)
                verbose(pos)
            for p in self.grapheMCinverse[(pos)] :
                if p not in vus :
                    rec(p)                  
        rec(destination)
        print(str(vus))
        return vus
    
    def update(self,level) :
        """
        Mets à jour les position des boites après un mouvement de caisse
        A appeler dans le mouvement du perso level.move_player() dans les boites quand il pousse un boite -> player_status == 2
        """
        self.level = level
        self.boxes = []
        # verbose('test' + str(self.boxes))
        # verbose('test' + str(self.width))
        # verbose('test' + str(self.height))
        for y in range(self.height):
            for x in range(self.width):
                pos = x,y
                if self.level.has_box((x,y)):
                    self.boxes.append(pos)
 
        for position in self.boxes :
            # self.nocaisse += self.autourCaisse(position)
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
        Quelles sont les positions qui interdisent le voisinage de deux caisses ?
        retourne un tableau t de quatre booléens pour Bas Haut Droite Gauche 
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
                if (x,y) in self.grapheMC.keys() :
                    str[y] = str[y][:x] + 'X' + str[y][x+1:]
        for y in range(self.height):
            for x in range(self.width):
                if (x,y) in self.possibles :
                    str[y] = str[y][:x] + ' ' + str[y][x+1:]
                if (x,y) in self.targets :
                    str[y] = str[y][:x] + '.' + str[y][x+1:]
        # Marquage Caisse
        for y in range(self.height):
            for x in range(self.width):
                if (x,y) in self.boxes :
                    str[y] = str[y][:x] + '$' + str[y][x+1:]
        s= ''
        for k in str :
            s += k + '\n'
        s += '\n'  
        return s
    
        
            