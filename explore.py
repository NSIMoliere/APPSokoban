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
from complements import *

class DFS:
    """
    Classical Depth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior".
    ET plus :
    Recherche une zone atteignable depuis une position sans bouger une caisse
    """

    def __init__(self, level):
        self.level = level
    
    '''
    JETER
    """
    DFS à partir d'une position, les caisses sont considérés comme des murs
    qui renvoit un tableau de booléens
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
    '''

    
    def search_floor_boombox(self, source, boxes):
        """
        DFS qui renvoit un tableau de booléens
        en tenant compte de la position du personnage et des boites
        source (x,y) position du personnage éventuelle
        boites = [(x,y),...]
        """
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
        """
        DFS qui renvoit un tableau de booléens
        depuis la source position du personnage éventuelle
        source (x,y)
        """
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
    
'''
JETER
class File:
    """ classe File
    création d'une instance File avec une liste
    """
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
'''

class BFS:
    """
    Classical Breadth-First Search
    """
    def __init__(self, level):
        self.level = level

    def voisins(self, pos):
        """
        Renvoit les voisins d'une position
        Sous forme d'un tableau de coordonnées :
        [(x,y),(x,y),...]
        """
        v = []
        x, y = pos
        for d, (mx, my) in enumerate(C.DIRS):
            (ox, oy) = (-mx, -my)
            if self.level.is_empty((x+mx, y+my)):
                v.append((x+mx, y+my))
        return v

    def search_floor(self, source):
        parent = {}
        sommet_visite = []
        f = File()
        f.enqueue(source)
        parent[source] = None
        while not f.isempty():
            tmp = f.dequeue()
            if tmp not in sommet_visite:
                sommet_visite.append(tmp)
            for voisin in self.voisins(tmp):
                if voisin not in sommet_visite and not voisin in f :
                    f.enqueue(voisin)
                    parent[voisin] = tmp
        return parent

    def chemin(self, end, parent):
        """
        Retourne le chemin sans pousser de caisse
        jusqu'à / depuis : end une position (x,y)
        """
        chemin = []
        courant = end
        while courant != None and courant in parent.keys():
            chemin = [courant] + chemin
            courant = parent[courant]
        return chemin
 