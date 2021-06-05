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
    the "interior" and "exterior".
    """

    def __init__(self, level):
        self.level = level
    
    """
    DFS qui renvoit un tableau de booléens
    en tenant compte de la position du personnage et des boites
    source (x,y)
    boites = [(x,y),...]
    """
    def search_floor_boombox(self, source, boxes):
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
                if self.level.is_wall((x+mx, y+my)) or (x+mx, y+my) in boxes :
                    continue

                rec_explore((x+mx, y+my))

        rec_explore(source)
        # verbose("DFS.search_floor : " + str(mark))
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
        # verbose("DFS.search_floor : " + str(mark))
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
            if self.level.is_empty((x+mx, y+my)):# and self.level.is_empty((x+2*mx, y+2*my)):\
                   #and not (self.level.is_wall((x+ox, y+oy)) or self.level.has_box((x+ox, y+oy))):
            #if (x+mx, y+my) in g.possibles:
                v.append((x+mx, y+my))
        #print(f"Voisins de {pos} : {v}")
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
 