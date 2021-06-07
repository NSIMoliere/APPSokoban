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

###########################################################################################
# La classe noeud est un état passager du plateau
# Elle contient l'emplacement des caisses
# Elle contient l'emplacement du personnage de manière normalisée :
#    sous forme d'une zone atteignable (matrice de booléen True, False)
# Pour pouvoir la retrouver sous forme de clé du dictionnaire, on produit aussi une emprunte unique
# Le décimal correspondant au nombres binaire de cette matrice + les caisses
#
# L'unique chose très importante ici est la recherche des prédécesseurs (plus bas) ou successeurs (pas faite, ça vous tente ?)
###########################################################################################

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
        self.index = -1 #?
        self.plateau = plateau
        self.determineZone(pos) 
        self.footprint = int(self.__hash__())
    
    def determineZone(self,pos) :
        """
        Dans un plateau comportant des caisses
        Renvoit le décimal correspondant au nombre binaire :
        00000000 00111100 01111110 ... ou chaque ligne correspond aux cases accessibles depuis
        depuis la position pos
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
        s = "\n[[Noeud id(" + str(self.footprint) +").]]\n" + "boxes pos :" + str(self.caisses) + "\nzone :" + matToString(self.zone)
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
    
    # Les deux fonctions suivantes font la même chose
    '''
    #JETER
    def nbcaisses(self) :
        # Je crois qu'on s'en serrt pas, à tester.
        return len(self.caisses)
    '''
    # Nous appelons la longueur du noeud, le nombre de caisses qu'il contient
    def __len__(self) :
        """
        Renvoit le nombre de caisse du noeud
        """
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
    
    # La méthode suivante permet de déterminer si une caisse à la position (x,y)
    # est présente dans ce noeud ou non (True ou False)
    # On peut l'appeler avec le mot "in"    
    def __contains__(self,position) :
        return position in self.caisses
    
    # La méthode suivante permet de renvoyer les predecesseurs d'un noeud
    # Une seule caisse a bougé d'une place
    ###################################################### C'est ici que ça se joue !
    ###################################################### Super important
    # Imaginons ce noeud, le perso est dans cette zone avec les tirets -----
    ########  
    ###---##  
    #---#-##   
    #-#--$ # 
    #---$# # 
    ##$#   #  
    ##   ###  
    ########
    # Précédemment il a pu être là :  pas là :  pas là :
        ########  ########  ########  ########  ########
        ###--@##  ###---##  ###---##  ###---##  ###   ##   
        #---#$##  #---#-##  #---#-##  #---#-##  #   # ##   
        #-#----#  #-#@$--#  #-#--$-#  #-#-$@-#  # #  $ #       
        #---$#-#  #---$#-#  #-@$-#-#  #---$#-#  #    # #  
        ##$# #-#  ##$# #-#  ##$#---#  ##$# #-#  ##$#$# #   
        ##   ###  ##   ###  ##---###  ##   ###  ##--@### 
        ########  ########  ########  ########  ########
    # La méthode suivante permet de renvoyer les predecesseurs d'un noeud
    # Une seule caisse a bougé d'une case
    # Peut-on améliorer cette méthode ?
    # On pourrait pas considérer comme voisin un noeud où une seule caisse a bougé
    # Mais de plusieurs cases ?
    def predecesseurs(self,plateau) :
        """
        Renvoit un tableau contenant les noeuds predecesseurs dans le graphe
        """
        mvts = [(-1,0),(+1,0),(0,-1),(0,+1)] # Mouvements possibles
        predecesseurs = []
        # Pour chacun des mouvements
        for dpos in mvts : 
            # Pour chacune des caisses :
            for i in range(len(self)) :
            # for i in range(len(self.nbcaisses()) :
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
                xp,yp = prevposperso # position du perso pour pousser la caisse
                xc,yc = prevposcaisse # position de la caisse au coup précédent
                # print("Tous predecesseurs éventuels :",prevposperso,prevposcaisse);
                if plateau.ground[yc][xc] and plateau.ground[yp][xp] and prevposcaisse not in self :
                        print("Predecesseurs :",prevposperso,prevposcaisse);print()
                        # print("Predecesseurs possibles:",prevposperso,prevposcaisse);print()
                        # On contruit ce noeud possible :
                        prevcaisses = self.caisses[:]
                        prevcaisses[i] = prevposcaisse
                        predecesseur = Noeud(self.plateau,prevposperso,prevcaisses)
                        # On l'ajoute au tableau si seulement c'est possible
                        # Considération sur l'intersection des zones accessibles avant et maintenant
                        if andMbool(self.zone,predecesseur.zone)[yp][xp] : # Voir complements : on fait l'intersection AND des deux matrices
                            predecesseurs.append(predecesseur) # Le mouvement a pu se faire                       
        return predecesseurs
                                    
"""
NE PAS JETER POUR L'INSTANT
Ca va peut-être servir !
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
        """ Exemple : Microcosmos - 3eme niveau
        4 Noeuds gagnants possibles : C'est la position du personnage @ après le dernier coup qui change
        Les prédécesseurs ne sont pas les mêmes
        ########  ########  ########  ########
        ###   ##  ###   ##  ###   ##  ###   ##
        #   #@##  #   # ##  #   # ##  #   # ##  
        # #  $ #  # #  $ #  # #  $ #  # #  $ #  
        # $  # #  # $@ # #  # $  # #  # $  # #
        ## #$  #  ## #$  #  ## #$@ #  ##@#$  #
        ##   ###  ##   ###  ##   ###  ##   ###
        ########  ########  ########  ########
        Ces quatres noeuds ne sont pas la même situation finale pourtant chacune favorables
        """
        # self.success = Noeud( self.plateau , self.player_position , level.targets )
        self.solution = [] # Tableau où la solution sera rangée
        # Les cases possibles du plateau moins les boites bien positionnées : self.startpp
        self.startpp = self.plateau.cases
        for p in level.boxes :
            if p in self.startpp : self.startpp.remove(p)
        pos = self.startpp.pop() # Une positon possible du personnage en fin de jeu
        self.success = Noeud( self.plateau , pos , level.targets )
        self.marked = {} # Ici on accueillera le graphe des predecesseurs
        self.explored = False # Si un premier BFS a été réalisé compñétement ou non 
        while len(self.startpp)>0 and not(self.solve()) : # Tentative de solution depuis ici
            self.explored = True
            for x in range(self.plateau.width) :
                for y in range(self.plateau.height) :
                    if self.success.zone[y][x] == True :
                        p = (x,y)
                        if p in self.startpp : self.startpp.remove(p)
            self.success = Noeud( self.plateau , pos , level.targets )
            pos = self.startpp.pop()
        #   self.success = Noeud( self.plateau , (x,y) , level.targets )
        for s in self.solution : print(s)
    
    
    def solve(self) :
        """
        Reconstruis le trajet depuis calculé par le BFS du graphe des situations de jeu
        Le graphe est construit en début de programme
        Renvoit une liste de points (x,y) o le personnage doit aller
        Puis le mouvement à faire pour pousser la caisse
        ((4, 5), 0) Aller en (5,5) et pousser vers le haut
        ((3, 2), 1) Aller en (3,2) et pousser vers le bas
        ((5, 5), 2) Aller en (3,2) et pousser vers la gauche
        ((2, 4), 3) Aller en (2,4) et pousser vers la droite 
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
                    m = tuple(map(operator.sub, d, o))  # Ces lignes permettent d'opérer sur les tuples : (x,y)+(z,t)=(x+z,y+t) 
                    pd = tuple(map(operator.sub, (0,0), m))
                    pd = tuple(map(operator.sub, o, m))
                    # Renvoit les codes de mouvement selon le fichier game.py et common.py
                    if m == (0,-1) : m = C.UP #0
                    if m == (0,1) : m = C.DOWN #1
                    if m == (-1,0) : m = C.LEFT #2
                    if m == (1,0) : m = C.RIGHT #3
                    verbose(str(pd) + " " + str(m))
                    self.solution.append((pd,m))
                    # verbose(marked[noeud_courant.footprint])
                else :
                    break # Permet de ne pas renvoyer un noeud courant None dans la boucle
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
        # self.marked = {}
        self.marked[n.footprint] = (d,n,None)
        while not f.isempty() :
            nc = f.dequeue()
            d = d + 1
            culdesac = True
            for v in nc.predecesseurs(self.plateau) :
                verbose(v)
                if v.footprint not in self.marked.keys() : # Peut-on 
                    f.enqueue(v)
                    self.marked[v.footprint] = (d,v,nc)
                    culdesac = False
        return self.marked

    
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
        
    


