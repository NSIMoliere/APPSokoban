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

class casesAtteignables:
    """
    Parcours le niveau à partir de la position du joueur et retourne la matrice
    booléenne des positions atteignables
    l'idée est d'appeler la fonction
    trouve_matrice_cases_atteignables(à la position courante du joueur)
    et de l'appeler à nouveau à chaque fois qu'il pousse une caisse (changement de config)
    """

    def __init__(self, level):
        self.level = level

    def trouve_matrice_cases_atteignables(self, source):
        init_x, init_y = source

        # on initialise toutes les cases comme non atteignables
        cases_atteignables = [[False for x in range(self.level.width)]
                for y in range(self.level.height)]
        
        # pour se rappeler de quelles cases ont été visitées
        seen = [[False for x in range(self.level.width)]
                for y in range(self.level.height)]
        
        # file des cases à traiter, initialisé avec la position de départ du joueur
        cases_a_traiter = [source]
        cases_atteignables[init_y][init_x]=True
        

        def rec_trouve_cases_atteignables():
            """
            rec_trouve_cases_atteignables()
            passe si la liste extérieure cases_a_traiter est vide
            sinon, pour (x,y) en tête de la liste cases_a_traiter
            elle retire (x,y) de la liste puis
            si (x,y) a été visité elle passe
            sinon, elle teste si la case au dessus est vide
            si oui elle l'ajoute dans la liste des cases atteignables
            et ajoute cette cellule dans la liste cases_a_traiter
            même chose pour la case du dessous, de droite, de gauche
            elle retire ensuite 
            """
            # si la liste de cases à traiter est vide
            if cases_a_traiter = []
                return
            # traitement de la cases en tête de liste
            # on supprime la case de la liste
            x, y = liste_de_cases_a_traiter.pop(0)
            # si la case a déjà été vue, on passe
            if seen[y][x]:
                return

            # marque la position actuelle comme visitée / vue
            seen[y][x] = True

            for d, (mx, my) in enumerate(C.DIRS):
                if not self.level.is_empty((x+mx, y+my)):
                    continue
                # si la cellule (x+mx, y+my) est vide on la marque comme atteignable
                # et on l'ajoute à la liste des cases à traiter
                cases_atteignables[y+my][x+mx]=True
                cases_a_traiter.append((x+mx, y+my))
                

                rec_trouve_cases_atteignables()

        rec_trouve_cases_atteignables()
        return cases_atteignables 


