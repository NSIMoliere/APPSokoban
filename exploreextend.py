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
        self.index = -1 # ? Je
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
        
    def distanceto(self,other) :
        """
        Etape 1 :
        distance entre deux noeuds Manhattan + mouvement du personnage
        Etape 2 :
        Prise en compte de la topologie du plateau : création de tenseurs sur le niveau.py
        """
        dist = 0
        #print(self)
        #print(other)
        for b in self.caisses :
            #print('ok')
            d = 0
            x,y = b
            #print(b)
            for bb in other.caisses :
                xx,yy = bb
                #print(bb)
                # Moyenne d'une distance type Manhattan, en prenant compte le mouvement du personnage.
                # un mouvement selon une composante a un cout de 1,
                # un nouvement en diagonale a un cout de 1 + 2(changement de place du perso) + 1 
                ########  b est le point de départ, 
                #b12345...
                #14567...
                #258
                #.6
                #..
                btobb = abs(y-yy)*2**abs(x-xx) + abs(x-xx)*2**abs(y-yy)
                '''
                # Prise en compte de la topologie du plateau
                # Tenseurs : Les tenseurs sont créés dans niveau.py : k est à régler à la main
                # k = 2 * self.plateau.level.gj.nbcases
                # Attention si appel avec cases non praticables Division by zero
                # ratio = k / (self.plateau.level.gj.tensions[y][x] + self.plateau.level.gj.tensions[yy][xx])
                # btobb = ratio * btobb
                '''
                d = d + btobb
                
                # Moyenne des distances 
                d = d // len(other)
            dist = dist + d
        return dist // len(self)
        
    
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
        # ((((0,(xb1,yb1)),(xb2,yb2)),(xb3,yb3))..,(empruntebinairedelazone))
        # Où b1,b2,b3 sont les positions des boites
        # Et z est la zone où se trouve le joueur
        self.caisses.sort()
        a = 0
        for c in self.caisses :
            a = (a,c)
            #print(c)
        a = (a , self.zonebintodec)
        return hash(a)
  
    def ajoutecaisse(self,position) :
        """
        ajoute une position (couple (x,y))de caisse à la fois
        Inutile
        """
        self.caisses.append(position)
    
    # Nous appelons la longueur du noeud, le nombre de caisses qu'il contient
    def __len__(self) :
        """
        Renvoit le nombre de caisse du noeud
        """
        return len(self.caisses)
    
    # Les deux méthodes suivantes pour permettre de looper sur les caisses du Noeud :
    # Style for c in n où n est un noeud
    '''
    def __next__(self) :
        self.index += 1
        if self.index >= len(self.caisses) :
            raise StopIteration
        else :
            return self.caisses[self.index]
            
    def __iter__(self) :
        return self
    '''
    
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
    ########                          celui là      voisin impossible :
    # Précédemment il a pu être là :  pas voisin :  pas là :
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
                if plateau.ground[yc][xc] and plateau.ground[yp][xp] and prevposcaisse not in self and prevposperso not in self :
                        #print("Predecesseurs :",prevposperso,prevposcaisse);print()
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

    def successeurs(self,plateau) :
        """
        Renvoit un tableau contenant les noeuds successeurs dans le graphe
        """
        mvts = [(-1,0),(+1,0),(0,-1),(0,+1)] # Mouvements possibles
        successeurs = []
        # Pour chacun des mouvements
        for dpos in mvts : 
            # Pour chacune des caisses :
            for i in range(len(self)) :
                pos = self.caisses[i]
                #######
                #######
                ### ###
                ## $ ## Ici la caisse a quatre successeurs possibles
                ### ###
                #######
                #######
                nextposcaisse = tuple(map(sum, zip(pos,dpos)))
                xc,yc = nextposcaisse # position de la caisse au coup précédent
                if plateau.ground[yc][xc] :
                    nextposperso = pos
                    xp,yp = nextposperso # position du perso pour pousser la caisse
                    nextcaisses = self.caisses[:]
                    for i in range(len(nextcaisses)) :
                        if nextcaisses[i] == nextposperso :
                            nextcaisses[i] = nextposcaisse
                    successeur = Noeud(self.plateau,nextposperso,nextcaisses)
                    successeurs.append(successeur) # Le mouvement a pu se faire
                '''
                JETER FAUX !!!
                # print("Tous successeurs éventuels :",nextposperso,nextposcaisse);
                if plateau.ground[yc][xc] and plateau.ground[yp][xp]  : 
                        # On contruit ce noeud possible :
                        
                        nextcaisses[i] = nextposcaisse
                        successeur = Noeud(self.plateau,nextposperso,nextcaisses)
                        # On l'ajoute au tableau si seulement c'est possible
                        # Considération sur l'intersection des zones accessibles avant et maintenant
                        if andMbool(self.zone,successeur.zone)[yp][xp] : # Voir complements : on fait l'intersection AND des deux matrices
                            successeurs.append(successeur) # Le mouvement a pu se faire
                '''
        return successeurs


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
    """
    Le graphe des positions possibles du jeu
    """
    def __init__(self,level) :
        self.Pred = {} # Dictionnaire des prédecesseurs
        self.plateau = Plateau(level) 
        self.player_position = level.player_position
        self.boxes = level.boxes
        self.gl = level.gl
        self.solution = [] # Tableau où la solution sera rangée
        self.LstSucc = {}
        self.LstPreced = {}
        
        '''
        # Mon test du jour : Ne pas tenir compte
        '''
        # Construire les noeuds de succès possible et éliminer les doublons. Les ranger dans les noeuds possibles
        # Les identifier
        self.marked = {}
        self.isf = self.plateau.issuesfavorables[:]
        self.isf_fp = [n.footprint for n in self.isf]
        # Construire ensuite le noeud de départ
        self.start = Noeud(self.plateau , self.player_position, self.boxes)
        # Lancer un BFSdescendant, depuis le noeud de départ et  
        # alternativement des BFSremontant, depuis les noeuds de succès, en gérant les priorités.
        # self.BFSto(self.start)
        '''
        # Fin test du jour
        '''
        # Tests distances :
        print("Test distance :")
        print(self.start.distanceto(self.isf[0]))
        
        
        # Équivalent avec la solution précédente :
        self.marked = {}
        self.isf = self.plateau.issuesfavorables[:]
        if len(self.isf) > 0 : self.success = self.isf.pop();
        while not(self.solve()) and len(self.isf) > 0 :
            self.success = self.isf.pop();
        
        # Impression de la solution dans la console
        # for s in self.solution : print(s)
        
    
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
        print("recherche d'une solution pour un noeud gagnant:")
        mvt = 0
        noeud_courant = Noeud(self.plateau , self.player_position, self.boxes)
        marked = self.BFS(noeud_courant)
        # print(marked)
        # verbose(marked[noeud_courant.footprint])
        if noeud_courant.footprint in marked.keys() :
            print("Il y a une solution")
            print("Nombres de noeud construits :",str(len(marked.keys())))
            # verbose(marked[noeud_courant.footprint])
            while noeud_courant.footprint in marked.keys() :#and mvt < 100:
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
                    # verbose(str(pd) + " " + str(m))
                    self.solution.append((pd,m))
                    # verbose(marked[noeud_courant.footprint])
                else :
                    break # Permet de ne pas renvoyer un noeud courant None dans la boucle
                #mvt =  mvt + 1
            print("Une solution en "+str(mvt)+" mouvements de caisses.")
            
            return True
        else :
            print("Pas de solution pour ce noeud ...")
            return False
    
    def BFS(self,posfrom) :
        """
        Exploration BFS du graphe (en même temps que sa construction !)
        Retourne un tableau de prédecesseurs et un tableau
        """
        print("Tentative de solution")
        n = self.success
        posfromfp = posfrom.footprint
        d = 0
        f1 = File()
        f1.enqueue(n)
        f2 = File() 
        # self.marked = {}
        if posfromfp != n.footprint : # Si on n'est pas à la solution déjà !
            self.marked[n.footprint] = (d,n,None)
        while not f1.isempty() or not f2.isempty() :
            if f2.isempty() :
                nc = f1.dequeue()
            else :
                nc = f2.dequeue()
            dsuivant = 0
            if not f1.isempty() : dsuivant = self.gl.noeud_is_Possible(f1.peek()) + f1.peek().distanceto(n)  
            d = d + 1
            for v in nc.predecesseurs(self.plateau) :
                if self.gl.noeud_is_Possible(v) != 0 :
                    if v.footprint not in self.marked.keys() :
                        dd = 0
                        dv =  self.gl.noeud_is_Possible(v)
                        if not f1.isempty() :
                             dv += f1.peek().distanceto(n) 
                        if dv > dsuivant :
                            f2.enqueue(v)
                        else :
                            f1.enqueue(v)
                        self.marked[v.footprint] = (d,v,nc)
                        if posfromfp == v.footprint :
                            return self.marked
        return self.marked
         
        '''
        # Mon test du jour : Ne pas tenir compte
        '''
    def BFSfrom(self,posfrom) :
        pass
        print("Montée : ")
        n = self.success # On part ici du noeud de succes et on remonte dans le graphe : liste des prédecesseurs
        posfromfp = posfrom.footprint # On cherche la situation actuelle
        # On en profite aussi pour renseigner la liste des successeurs
        # Condition d'arrêt :
        # ?
        d = 0
        f1from = File()
        f1from.enqueue(n)
        if posfromfp not in self.isf_fp : # Si on n'est pas à la solution déjà !
            if n.footprint not in self.LstPreced :
                self.LstPreced[n.footprint] = {}
        else :
            return self.LstSucc
        # Remontée
        while not f1from.isempty() :
            nc = f1from.dequeue()
            d = d + 1
            for v in nc.predecesseurs(self.plateau) :
                if self.gl.noeud_is_Possible(v) != 0 :
                    if v.footprint not in self.LstPreced.keys() :
                        dv = self.gl.noeud_is_Possible(v)
                        if dv != 0 :
                            f1from.enqueue(v)
                        if nc.footprint not in self.LstPreced :
                            self.LstPreced[nc.footprint] = (d,dcum,v,nc)
                        else :
                            self.LstPreced[nc.footprint].add((d,dcum,v,nc))
                        if v.footprint not in LstSucc :
                            self.LstSucc[v.footprint] = (d,dcum,v,nc)
                        else :
                            self.LstSucc[v.footprint].add((d,dcum,v,nc))
                        if posfromfp == v.footprint :
                            return self.LstSucc
        return self.LstSucc
        
        
    def BFSto(self,posfrom) :
        pass
        print("Descente : ")
        # On cherche la situation de succes
        posfromfp = posfrom.footprint # On part ici de la situation actuelle, on descend : liste des successeurs
        # On en profite aussi pour renseigner liste des prédecesseurs
        # Condition d'arrêt :
        # ?
        d = 0
        f1to = File()
        if posfromfp not in self.isf_fp : # Si on n'est pas à la solution déjà !
            f1to.enqueue((posfrom,d))
        else :         
            return self.LstSucc
        # Descente
        while not f1to.isempty() :
            nc,d = f1to.popBigger()
            d = d + 1
            for v in nc.successeurs(self.plateau) :
                if v.footprint in self.isf_fp :
                    print("Solution trouvée !")
                    return self.LstSucc 
                if self.gl.noeud_is_Possible(v) != 0 :
                    if v.footprint not in self.LstSucc.keys() :
                        # dd = 0
                        dv = self.gl.noeud_is_Possible(v)
                        dcum = d + self.gl.noeud_is_Possible(v) / (1+v.distanceto(self.isf[0]))
                        if dv != 0 :
                            f1to.enqueue((v,dcum))
                        self.LstSucc[nc.footprint] = (d,dcum,nc,v) # On met l'arc entier
                        self.LstPreced[v.footprint] = (d,dcum,nc,v) # On met l'arc entier  
        return self.LstSucc
        
        
    
    
    

    
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
        self.issuesfavorables = self.successPossibles()

    def successPossibles(self):
        """
        Retourne les noeuds possibles de fin, dans un tableau :
        Il y en a plusieurs car la position des caisses finale peut déterminer plusieurs zone différentes
        Exemple : Microcosmos - 3eme niveau
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
        Ces quatres noeuds ne sont pas la même situation finale pourtant chacune favorables.
        """
        issuesfav = []
        finalpp = []
        for x in range(self.width) :
            for y in range(self.height) :
                if self.level.is_floor((x,y)) :
                    finalpp.append((x,y)) 
        for p in self.level.targets : # 
            if p in finalpp : finalpp.remove(p)
        pos = finalpp.pop() # Une positon possible du personnage en fin de jeu
        success = Noeud( self , pos , self.level.targets )
        while len(finalpp)>0 :
            issuesfav.append(success)
            for x in range(self.width) :
                for y in range(self.height) :
                    if success.zone[y][x] == True :
                        p = (x,y)
                        if p in finalpp : finalpp.remove(p)
            success = Noeud( self, pos , self.level.targets )
            if len(finalpp)>0 : pos = finalpp.pop()
        return issuesfav


    
def main() :
    mvts = [(-1,0),(+1,0),(0,-1),(0,+1)]
    for dpos in mvts :
        pos = (3,4)
        print(tuple(map(sum, zip(pos,dpos))))
        print(tuple(map(sum, zip(pos,dpos,dpos))))
    print((2,3) in [(3,4),(3,3)])

if __name__ == "__main__":
    main()
        
    


