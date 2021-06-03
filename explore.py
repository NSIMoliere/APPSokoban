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

global cible
global boite
global mark
class DFS:
    """
    Classical Depth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior.
    """

    def __init__(self, level):
        self.level = level

    def search_floor(self, source):
        init_x, init_y = source
        global cible
        global boite
        global mark
        print("la valeur de self.level.width est : ", self.level.width )
        #long = self.level.width
        print("la valeur de self.level.width est : ", self.level.height )
        #haut = self.level.height
        # to remember which tiles have been visited or not
        mark = [[False for x in range(self.level.width)]   #création de la matrice d'adjacence
                for y in range(self.level.height)]
        mark2 = [[False for x in range(self.level.width)]   #création de la matrice d'adjacence
                for y in range(self.level.height)]
        def rec_explore(position):
            global cible
            global boite
            global mark
            
            x, y = position
            if mark[y][x]:
                return

            # mark current position as visited
            mark[y][x] = True

            for d, (mx, my) in enumerate(C.DIRS):
                if self.level.is_wall((x+mx, y+my)):
                    continue
                
                if self.level.has_box((x+mx, y+my)):
                    print("boite trouvée coordonnées :", (x+mx, y+my))
                    boite = (x+mx, y+my)
                    mark[y+my][x+mx] = "Boite"
                    print("la boite posséde les coordonnées :", boite)
                    continue
                
                if self.level.is_target((x+mx, y+my)):
                    print("cible trouvée coordonnées :", (x+mx, y+my))
                    cible = (x+mx, y+my)
                    mark[y+my][x+mx] = "Cible"
                    
                    continue
                    
                
                rec_explore((x+mx, y+my))
                
        rec_explore(source)
        
        print(mark)
        print("la cible est au ", cible)
        print("la boite est au ", boite)
        
        return mark
        
