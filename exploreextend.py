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
import operator
from complements import *

class Noeud() :
    def __init__(self , plateau , pos, positions = []  ) :
        """
        plateau : objet Plateau
        plateau.cases : tableau de couples (x,y) des positions possibles sur le plateau de jeu
        positions : tableau de couples (x,y) des positions des caisses
        pos : position du perso
        """
        self.caisses = positions 
        self.niveau = 0
        self.index = -1
        self.plateau = plateau
        self.determineZone(pos) 
        self.footprint = int(self.__hash__())
        
    def determineZone(self,pos) :
        """
        Dans un plateau comportant des caisses
        Renvoit le décimal correspondant au nombre binaire :
        00000000 00111100 01111110 ... ou chaque ligen correpond aux acses accessible depuis
        depuis la position 
        """
        dfs = DFS( self.plateau.level )
        mark2 = dfs.search_floor_boombox( pos , self.caisses )
        # verbose("search_boombox " + str(self.zone) + "\n" + "caisses : " + str(self.caisses) + "\n")
        # verboseMbool(mark2)
        s = '0b'
        for x in range(self.plateau.width) :
            for y in range(self.plateau.height) :
                if mark2[y][x] == True :
                    s += '1'
                else :
                    s += '0'  
        self.zonebintodec = int(s,2)
        self.zone = mark2
    
    def __repr__(self) :
        s = "[[. " + str(self.caisses) + " / >> " + str(self.zone) + " <<  .]]"
        return s
        
    # Les classes suivantes permettent de 
    # tester l'égalité de deux noeuds / non egalité / Savoir si deux noeuds sont les mêmes ...
    def __eq__(self, other):
        if self.footprint() == other.footprint() :
            return True
    
    def __ne__(self, other):
        if self.footprint() != other.footprint() :
            return True
    
    def __hash__(self):
        # Renvoit un entier unique qui caractèrise le noeud
        # (..(((0,(xb1,yb1)),(xb2,yb2)),(xb3,yb3))..,(xz,yz)
        # Où b1,b2,b3 sont les positions des boites
        # Et z est la zone où se trouve le joueur
        self.caisses.sort()
        a = 0
        for p in self :
            a = (a,p)
        a = (a , self.zonebintodec)
        return hash(a)
  
    def ajoutecaisse(self,position) :
        """
        ajoute une position (couple (x,y))de caisse à la fois
        Inutile
        """
        self.caisses.append(position)
        
    def nbcaisses(self) :
        # Je crois qu'on s'en serrt pas, à tester.
        return len(self.caisses)
    
    # Les deux méthodes suivantes pour permettre de looper sur les caisses du Noeud :
    # Style for c in n où n est un noeud
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
    
    # La méthode suivante permet de renvoyer les predecesseurs d'un noeud
    # Une seule caisse a bougé
    def predecesseurs(self,plateau) :
        """
        Renvoit un tableau contenant les noeuds predecesseurs dans le graphe
        """
        mvts = [(-1,0),(+1,0),(0,-1),(0,+1)] # Mouvements possibles
        predecesseurs = []
        # Pour chacun des mouvements
        for dpos in mvts : 
            # Pour chacune des caisses : 
            for i in range(self.nbcaisses()) :
                pos = self.caisses[i]
                #######
                ### ###
                ### ###
                #  $  # Ici la caisse a quatre prédécesseurs possibles
                ### ###
                ### ###
                #######
                
                prevposcaisse = tuple(map(sum, zip(pos,dpos)))
                prevposperso = tuple(map(sum, zip(pos,dpos,dpos)))
                xp,yp = prevposperso
                xc,yc = prevposcaisse
                # print("Tous predecesseurs :",prevposperso,prevposcaisse);
                
                if plateau.ground[yc][xc] and plateau.ground[yp][xp] and prevposcaisse not in self :
                        print("Predecesseurs :",prevposperso,prevposcaisse);print()
                        
                        prevcaisses = self.caisses[:]
                        prevcaisses[i] = prevposcaisse
                        predecesseur = Noeud(self.plateau,prevposperso,prevcaisses)
                        if andMbool(self.zone,predecesseur.zone)[yp][xp] :
                            predecesseurs.append(predecesseur) # Le mouvement a pu se faire
                        
        return predecesseurs
                                    
"""
Cette classe ne sert à rien
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
"""   
    
class GrapheJeu() :
    """
    Le graphe des positions possibles du jeu
    """
    def __init__(self,level) :
        self.Pred = {} # Dictionnaire des prédecesseurs
        self.plateau = Plateau(level) 
        self.player_position = level.player_position
        self.boxes = level.boxes
        # Le noeud où le jeu est gagnant (Attention il peut y avoir plusieurs noeuds gagnants)
        self.solution = [] # Tableau où la solution est rangée
        self.success = Noeud( self.plateau , self.player_position , level.targets )
        # self.success = Noeud( self.plateau , (6,5) , level.targets )
        self.startpp = self.plateau.cases
        for p in level.boxes :
            self.startpp.remove(p)
        pos = self.startpp.pop()

       
        while len(self.startpp)>0 and not(self.solve()) :
            for x in range(self.plateau.width) :
                for y in range(self.plateau.height) :
                    if self.success.zone[y][x] == True :
                        if p in self.startpp : self.startpp.remove(p)
            self.success = Noeud( self.plateau , pos , level.targets )
            pos = self.startpp.pop()
        
        #   self.success = Noeud( self.plateau , (x,y) , level.targets )
        
        for s in self.solution : print(s)
    
    def solve(self) :
        """
        Reconstruis le trajet depuis le BFS du graphe
        """
        marked = self.BFS()
        print(marked)
        mvt = 0
        noeud_courant = Noeud(self.plateau , self.player_position, self.boxes)
        # verbose(marked[noeud_courant.footprint])
        if noeud_courant.footprint in marked.keys() :
            verbose("Il y a une solution")
            # verbose(marked[noeud_courant.footprint])
            while noeud_courant.footprint in marked.keys() and mvt < 100:
                prevCaisses = noeud_courant.caisses
                noeud_courant = marked[noeud_courant.footprint][2]
                if noeud_courant is not None :
                    for c in prevCaisses :
                        if c not in noeud_courant.caisses :
                            o = c
                    for c in noeud_courant.caisses :
                        if c not in prevCaisses :
                            d = c
                    m = tuple(map(operator.sub, d, o))
                    pd = tuple(map(operator.sub, (0,0), m))
                    pd = tuple(map(operator.sub, o, m))
                  
                    if m == (0,-1) : m = C.UP #0
                    if m == (0,1) : m = C.DOWN #1
                    if m == (-1,0) : m = C.LEFT #2
                    if m == (1,0) : m = C.RIGHT #3
                    
                    verbose(str(pd) + " " + str(m))
                    self.solution.append((pd,m))
                    # verbose(marked[noeud_courant.footprint])
                else :
                    break
                mvt =  mvt + 1
            return True
        else :
            print("pas de solution")
            return False
   
            
    
    def BFS(self) :
        """
        Exploration BFS du graphe (en même temps que sa construction !)
        Retourne un tableau de prédecesseurs
        """
        n = self.success
        d = 0
        f = File()
        f.enqueue(n)
        marked = {}
        marked[n.footprint] = (d,n,None)
        while not f.isempty() :
            nc = f.dequeue()
            d = d + 1
            for v in nc.predecesseurs(self.plateau) :
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
        self.cases = [] # Ensembles des cases vides sous forme de liste de couples (x,y)
        dfs = DFS(self.level) # Appel pour trouver l'intérieur du jeu (case accessibles par le personnage)
        self.ground = dfs.search_floor(level.player_position) # case accessibles par le personnage . True / False
        self.height = len(self.ground) # hauteur du plateau de jeu mur compris
        self.width = len(self.ground[0]) # largeur du plateau de jeu mur compris
        for x in range(self.width):
            for y in range(self.height):
                if self.ground[y][x]:
                    self.cases.append((x,y))
        print(self.cases)

    
def main() :
    mvts = [(-1,0),(+1,0),(0,-1),(0,+1)]
    for dpos in mvts :
        pos = (3,4)
        print(tuple(map(sum, zip(pos,dpos))))
        print(tuple(map(sum, zip(pos,dpos,dpos))))
    print((2,3) in [(3,4),(3,3)])

if __name__ == "__main__":
    main()
        
    


