"""
Handles the reading of levels from pack files,
as well as the state of the level when playing the game
- map of whole level: floor, walls, targets
- player position
- position of boxes
"""

import os
import pygame
import common as C
from copy import deepcopy
from explore import *
from utils import *
from exploreextend import *


class Level:
    """
    Store the internal state of a level
    """

    def __init__(self, game, filename):
        self.game = game
        verbose("Nouveau Jeu : " + str(game))
        self.num_moves = 0
        self.filename = filename # String Nom du fichier : .txt
        self.level_lines = []
        self.level_number = 0
        self.load_file()    # read whole file
        self.loaded = False  # True when a level is loaded
        self.pushed_box = None
        # verbose("Graphe Mouvement Caisse :" + str(gmc.grapheMC))

    def place_box(self, box):
        x, y = box
        self.mboxes[y][x] = True

    def clear_box(self, box):
        x, y = box
        self.mboxes[y][x] = False

    def set_player(self, p):
        verbose('player set at', p)
        self.player_position = p

    def parse_rows(self, rows, symbols):
        self.map = []
        max_width = 0
        self.boxes = []
        self.targets = []
        height = len(rows)

        for y in range(len(rows)):
            level_row = []
            if rows[y] == '':
                height -= 1
                continue
            if len(rows[y]) > max_width:
                max_width = len(rows[y])

            for x in range(len(rows[y])):
                block = symbols.index(rows[y][x])
                level_row.append(block)

                if block == C.BOX:
                    level_row[-1] = C.GROUND
                    self.boxes.append((x, y))

                elif block == C.TARGET:
                    self.targets.append((x, y))

                elif block == C.TARGET_FILLED:
                    level_row[-1] = C.TARGET
                    self.boxes.append((x, y))
                    self.targets.append((x, y))

                elif block == C.PLAYER:
                    level_row[-1] = C.GROUND
                    self.player_position = (x, y)

                elif block == C.PLAYER_ON_TARGET:
                    level_row[-1] = C.TARGET
                    self.targets.append((x, y))
                    self.player_position = (x, y)

            self.map.append(level_row)

        self.width = max_width
        self.height = height

        for y in range(height):
            while len(self.map[y]) < max_width:
                self.map[y].append(C.AIR)

        # map of boxes
        self.mboxes = [[False for x in range(self.width)]
                       for y in range(self.height)]
        for bx, by in self.boxes:
            self.mboxes[by][bx] = True

        verbose("Level size: ", self.width, "x", self.height)
        # verbose(self.map)
        # verbose(self.mboxes)
        verbose("boxes :" + str(self.boxes))

    def load_file(self):
        """
        Load a pack of sokoban levels.
        Does not create all levels but stores the corresponding lines so
        as to be able to load a particular level later.
        """

        verbose('Reading file', self.filename)
        with open(os.path.join('assets', 'levels', self.filename)) as level_file:
            # prefers that to readlines() as there is not trailing "\n"
            rows = level_file.read().splitlines()

        num = 0
        lev = []
        current = []
        title = None

        for r in rows:
            if r == '':
                # end of level
                if current != []:
                    lev.append((title, current))
                    current = []
                    title = None
                continue

            if r[0] == ';':
                continue

            if r.startswith('Title: '):
                title = r[7:]

            # check if this is a valid line:
            if not valid_soko_line(r):
                continue

            current.append(r)  # row belongs to level

        self.level_lines = lev

    def load(self, levelnum):
        self.loaded = False

        if levelnum > len(self.level_lines):
            return False

        self.title, rows = self.level_lines[levelnum-1]
        self.parse_rows(rows, C.SYMBOLS_ORIGINALS)

        # Use DFS to mark the interior floor as ground
        dfs = DFS(self)
        mark = dfs.search_floor(self.player_position)
        
        #
        self.gms = GMC(self,self.player_position)
        
        #
        self.gj = GrapheJeu(self)
        verbose("Fin :\n" + str(self.gj.success))
        print(self.gj.solution)
        
        for y in range(self.height):
            for x in range(self.width):
                if mark[y][x]:
                    if self.map[y][x] == C.AIR:
                        self.map[y][x] = C.GROUND

        # highlight on some tiles
        self.mhighlight = [[C.HOFF for x in range(
            self.width)] for y in range(self.height)]

        # no previous move to cancel
        self.state_stack = []
        self.num_moves = 0
        self.loaded = True
        
        
        
        return True
    
    def solve(self) :
        pass
    
    def moveplayerto(self,pos) :
        dest = pos
        orig = self.player_position
        verbose(orig)
        f = File()
        f.enqueue(dest)
        marked = {}
        marked[dest] = (None,None)
        # while (n = f.dequeue()) : Est-ce qu' il y a une syntaxe pour ça en python ?
        # verbose(f.isempty())
        while not f.isempty() :
            pc = f.dequeue()
            x,y = pc
            for d, (mx, my) in enumerate(C.DIRS):
                if not self.is_wall((y+my,x+mx)) and not self.has_box((y+my,x+mx))  :
                    np = pc
                    verbose(pc)
                    nc = (y+my,x+mx)
                    if nc not in marked.keys() :
                        marked[nc] = (d,np)
                        f.enqueue(nc)
                    
        chemin = []
        verbose(marked)
        
        nc = orig 
        while marked[nc] is not (None,None) :
            chemin.append(marked[nc][0])
            nc = marked[nc][1]
        for m in chemin :
            key = DIRKEY[m]
            self.game.move_character(m)
        
        
    def move(self,t):
        """
        "automated" movement: pretend the user has pressed a direction key
        on the keyboard.
        Here we move up, right, down, then left
        """
        for m in t :
            key = DIRKEY[m]
            self.game.move_character(key)
                    
        return marked
        for m in [C.UP, C.RIGHT, C.DOWN, C.LEFT]:
            key = DIRKEY[m]
            self.move_character(key)

    def reset_highlight(self):
        for y in range(self.height):
            for x in range(self.width):
                self.mhighlight[y][x] = C.HOFF

    def highlight(self, positions, htype=C.HATT):
        for x, y in positions:
            self.mhighlight[y][x] = htype

    # Some helper functions to check the state of a tile

    def has_box(self, pos):
        x, y = pos
        return self.mboxes[y][x]

    def is_target(self, pos):
        x, y = pos
        return self.map[y][x] in [C.TARGET, C.TARGET_FILLED]

    def is_wall(self, pos):
        x, y = pos
        return self.map[y][x] == C.WALL

    def is_floor(self, pos):
        x, y = pos
        return self.map[y][x] in [C.GROUND, C.TARGET, C.PLAYER]

    def is_empty(self, pos):
        return self.is_floor(pos) and not self.has_box(pos)

    def get_current_state(self):
        return {'mboxes': deepcopy(self.mboxes),
                'player': self.player_position,
                'moves': self.num_moves,
                }

    def restore_state(self, state):
        self.mboxes = state['mboxes']
        self.update_box_positions()
        self.player_position = state['player']
        self.num_moves = state['moves']

    def push_state(self):
        self.state_stack.append(self.get_current_state())
        # verbose("dernier etat (Level.state_stack[-1]) : " + str(self.state_stack[-1]))
               
    def aide(self):
        """
        positionne le highlight C.HELP sur les case interdites pour une caisse
        positionne le highlight dans un intervalle 10..26 sur chaque caisse :
                             DGBH . Interdits de mettre une caisse à Droite / Gauche / en Bas / Haut
        10 = 10 + 0 = 10 + 0b0000
        11 = 10 + 1 = 10 + 0b0001
        12 = 10 + 2 = 10 + 0b0010
        ...
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x,y) in self.gms.grapheMC.keys() and (x,y) not in self.gms.possibles :
                    self.mhighlight[x][y] = C.HELP           
        for position in self.gms.boxes :
            t = self.gms.boolCaisse(position)
            x , y = position
            self.mhighlight[y][x] = 10
            for i in range(4) :
                self.mhighlight[y][x] += (1-t[i])*(2**i)   # 10 = 10 + (0b0000) // 11 = 10 + (0b0001) ...    

        self.bfs = BFS(self)
        boxes = []
        targets = []
        for y in range(self.height):
            for x in range(self.width):
                if self.has_box((x, y)):
                    boxes.append((x, y))
                if self.is_target((x, y)):
                    targets.append((x, y))

        #ch = bfs.chemin(self.gj.solution[0][0], self.player_position)
        mony, monx = self.gj.solution[0][0]
        #print("Premier objectif : ", (monx, mony))
        px, py = self.player_position
        #print("Position du personnage : ", (px, py))
        #print("Dictionnaire Parents : ", self.bfs.search_floor((px, py)))
        ch = self.bfs.chemin((monx, mony), self.bfs.search_floor((px, py)))
        #print("Chemin à suivre : ", ch)
        for prochain in ch:
            x, y = prochain
            self.mhighlight[y][x] = C.HSELECT

        for box in boxes:
            #print("Positions des caisses : ", self.bfs.search_floor(box))
            #print(targets[0])
            ch = self.bfs.chemin(targets[0], self.bfs.search_floor(box))
            #print("Déplacement de la caisse : ", ch)
            if len(ch) > 1:
                prochain = self.bfs.chemin(targets[0], self.bfs.search_floor(box))[1]
                x, y = prochain
                self.mhighlight[y][x] = C.HSUCC
    
    def move_player(self, direction):
        """
        Update the internal state of the level after a player movement:
        position of the player and maybe a box has been moved.
        Return value:
        - ST_MOVING if the player is moving without pushing a box
        - ST_PUSHING if the payer is moving and pushing a box
        - ST_IDLE if the player is not moving (the move was illegal)
        """
        x, y = self.player_position
        move_x, move_y = direction

        # print ("trying to move", x,"x",y," in direction",direction)

        player_status = C.ST_IDLE

        xx = x+move_x
        yy = y+move_y
        xx2 = x+2*move_x
        yy2 = y+2*move_y

        if xx < 0 or xx >= self.width or\
           yy < 0 or yy >= self.height:
            return

        if self.is_empty((xx, yy)):
            # Player just moved on an empty cell
            self.player_position = (xx, yy)
            player_status = C.ST_MOVING

        elif self.has_box((xx, yy)) and self.is_empty((xx2, yy2)):
            # Player is trying to push a box
            self.pushed_box = (xx2, yy2)

            player_status = C.ST_PUSHING

            # Save current state
            self.push_state()

            boxi = self.boxes.index((xx, yy))
            self.boxes[boxi] = (xx2, yy2)

            self.mboxes[yy][xx] = False
            self.mboxes[yy2][xx2] = True

            self.player_position = (xx, yy)

        if player_status != C.ST_IDLE:
            self.num_moves += 1
        
        self.gms.update(self)
        # verbose("Renvoyé par Level.move_player() (0-bloque / 1-libre / 2-pousse)" + str(player_status))
        if player_status == 2 :
            self.gms.update(self)
            # verbose("GMC :\n" + str(self.gms))
        
        self.aide()
        
        return player_status

    def hide_pushed_box(self):
        x, y = self.pushed_box
        self.mboxes[y][x] = False

    def show_pushed_box(self):
        x, y = self.pushed_box
        self.mboxes[y][x] = True



    def update_box_positions(self):
        self.boxes = []
        for y in range(self.height):
            for x in range(self.width):
                if self.mboxes[y][x]:
                    self.boxes.append((x, y))
        self.gms.update(self)
                    

    def cancel_last_change(self):
        """
        Return True if there is still cancelable moves
        """

        if not self.state_stack:
            verbose("No previous state")
            return False

        state = self.state_stack.pop()
        self.restore_state(state)
        return self.state_stack != []

    def has_cancelable(self):
        return self.state_stack != []

    def has_win(self):
        for b in self.boxes:
            if not self.is_target(b):
                return False
        return True


    
    def render(self, window, textures, highlights):
        """
        Render the whole level.
        Some tiles might be highlighted.
        """
        
        for y in range(self.height):
            for x in range(self.width):
                pos = (x * C.SPRITESIZE, y * C.SPRITESIZE)

                if self.mboxes[y][x]:
                    if self.is_target((x, y)):
                        window.blit(textures[C.TARGET_FILLED], pos)
                    else:
                        window.blit(textures[C.BOX], pos)

                elif self.map[y][x] in textures:
                    window.blit(textures[self.map[y][x]], pos)
                    if self.is_target((x, y)):
                        window.blit(textures[C.TARGETOVER], pos)

                h = self.mhighlight[y][x]
                if h:
                    window.blit(highlights[C.SPRITESIZE][h], pos)
        
        
        
        
        
                    
