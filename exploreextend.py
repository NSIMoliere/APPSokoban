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


class File() :
    def __init__(self) :
        self.t = []
        
    def enqueue(self,x) :
        self.t.append(x)
        
    def dequeue(self) :
        if len(self.t) > 0 :
            r = self.t[0]
            self.t = self.t[1:]
            return r
        else :
            return false
    
    def __contains__(self,x) :
        return x in self.t
    
    def isempty(self):
        if len(self.t)>0 :
            return False
        return True

class Noeud() :
    def __init__(self , plateau, pos, positions = []  ) :
        """
        positions : tableau de couples (x,y) des positions des caisses
        pos : position du perso
        """
        self.caisses = positions
        self.niveau = 0
        self.index = -1
        self.plateau = plateau
        self.zone = pos
        self.zone = self.determineZone()
        self.footprint = int(self.__hash__())
        
    def determineZone(self) :
        dfs = DFS(self.plateau.level)
        mark = dfs.search_floor_boombox(self.zone)
        for x in range(self.plateau.width) :
            for y in range(self.plateau.height) :
                if mark[y][x] == True :
                    return x,y
    
    def __repr__(self) :
        s = "[[. " + str(self.caisses) + " / >> " + str(self.zone) + " <<  .]]"
        return s
        
    def __eq__(self, other):
        if self.footprint() == other.footprint() :
            return True
    
    def __ne__(self, other):
        if self.footprint() != other.footprint() :
            return True
    
    def __hash__(self):
        # classer les positions des caisses dans l'ordre croissant, dans un tuple de bonne longueur
        self.caisses.sort()
        a = 0
        for p in self :
            a = (a,p)
        a = (a , self.zone)
        return hash(a)
  
    def ajoutecaisse(self,position) :
        """
        ajoute une position (couple (x,y))de caisse à la fois
        """
        self.caisses.append(position)
        
    def nbcaisses(self) :
        return len(self.caisses)
    
    # Les deux méthodes suivantes pour permettre de lopper sur les caisses du Noeud :
    def __next__(self) :
        self.index += 1
        if self.index >= len(self.caisses) :
            raise StopIteration
        else :
            return self.caisses[self.index]
            
    def __iter__(self) :
        return self
    
    def __contains__(self,position) :
        return position in self.caisses
    
    def voisins(self,plateau) :
        mvts = [(-1,0),(+1,0),(0,-1),(0,+1)]
        voisins = []
        for dpos in mvts :
            for i in range(self.nbcaisses()) :
                pos = self.caisses[i]
                prevposcaisse = tuple(map(sum, zip(pos,dpos))) 
                prevposchar = tuple(map(sum, zip(pos,dpos,dpos)))
                if prevposcaisse in plateau.cases and prevposchar in plateau.cases :
                    if prevposcaisse not in self and prevposchar not in self :
                        prevcaisses = self.caisses[:]
                        prevcaisses[i] = prevposcaisse
                        voisin = Noeud(self.plateau,prevposchar,prevcaisses)
                        voisins.append(voisin)
        return voisins
                                     

class Arc() :
    def __init__(self,posToPush) :
        self.posToPush = posToPush
        self.posFrom = posToPush
        
    def __repr__(self) :
        s = '|--' + str(self.posFrom) + '---' + str(self.posToPush) + '-->'
        return s
        
    def setFrom(self,position) :
        self.posFrom = position
        
    def copy(self) :
        A = Arc(self.posToPush)
        A.posFrom = self.posFrom
        return A
    
    
class GrapheJeu() :
    def __init__(self,level) :
        self.Pred = {}
        self.plateau = Plateau(level)
        y,x = level.player_position
        self.player_position = x,y
        self.boxes = [(y,x) for (x,y) in level.boxes]
        self.set_noeudGagne( Noeud( self.plateau , (x,y) , [(y,x) for (x,y) in level.targets] ) )
        verbose(self.success)
        self.solve()
    
    def solve(self) :
        marked = self.BFS() 
        verbose(marked)
        c = 0
        noeud_courant = Noeud(self.plateau , self.player_position, self.boxes)
        verbose(noeud_courant.caisses)
        # verbose(marked[noeud_courant.footprint])
        if noeud_courant.footprint in marked.keys() :
            verbose("Il y a une solution")
            # verbose(marked[noeud_courant.footprint])
            while noeud_courant.footprint in marked.keys() and c < 100:
                noeud_courant = marked[noeud_courant.footprint][2]
                if noeud_courant is not None :
                    verbose(noeud_courant.caisses)
                    # verbose(marked[noeud_courant.footprint])
                else :
                    break
                c= c+1
                
                
    
    def set_noeudGagne(self,S) :
        """
        S est le Noeud où le niveau est gagné
        """
        self.success = S
    
    
    def BFS(self) :
        """
        Exploration BFS du graphe (en même temps que sa construction !)
        """
        n = self.success
        d = 0
        f = File()
        f.enqueue(n)
        marked = {}
        marked[n.footprint] = (d,n,None)
        # while (n = f.dequeue()) : Est-ce qu' il y a une syntaxe pour ça en python ?
        verbose(f.isempty())
        while not f.isempty() :
            nc = f.dequeue()
            d = d + 1
            for v in nc.voisins(self.plateau) :
                verbose(v)
                if v.footprint not in marked.keys() : # Ici il faudrait voir à normaliser la clé
                    f.enqueue(v)
                    marked[v.footprint] = (d,v,nc)
        return marked


    
class Plateau() :
    """
    Classe pour accueillir les éléments statiques du plateau
    """
    def __init__(self,level) :
        self.level = level
        self.cases = []
        dfs = DFS(self.level) # Appel pour trouver l'intérieur du jeu (case accessibles par le personnage)
        self.ground = dfs.search_floor(level.player_position) # case accessibles par le personnage . True / False
        self.height = len(self.ground) # hauteur du plateau de jeu mur compris
        self.width = len(self.ground[0]) # largeur du plateau de jeu mur compris
        for y in range(self.height):
            for x in range(self.width):
                if self.ground[y][x]:
                    self.cases.append((y,x))

    
def main() :
    mvts = [(-1,0),(+1,0),(0,-1),(0,+1)]
    for dpos in mvts :
        pos = (3,4)
        print(tuple(map(sum, zip(pos,dpos))))
        print(tuple(map(sum, zip(pos,dpos,dpos))))
    print((2,3) in [(3,4),(3,3)])

if __name__ == "__main__":
    main()
        
    


