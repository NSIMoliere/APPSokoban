from complements import *

class LevelGraphe():
    
    def __init__(self,level) :
        
        # Préparation :
        self.level = level
        
        self.VTo = MCreate(self.level.width,self.level.height,0) #(Matrice de 0)
        self.VFrom = MCreate(self.level.width,self.level.height,0) #(Matrice de 0)
        self.valeursTo = [i for i in range(1,20)] # Marqueurs To non utilisés
        self.valeursTo.reverse()
        self.valeursFrom = [i for i in range(1,20)]
        self.valeursFrom.reverse() # Marqueurs From non utilisés

        self.targets = self.level.targets[:]
        self.targetsVues = []
        self.boxes = self.level.boxes[:]
        self.boxesVues = []
        
        # C'est parti
        self.bfsTo()
        

        while len(self.targets) > 0 :
            print("Attention : Il y plusieurs sous-problèmes !")
            self.bfsTo()        
        while len(self.boxes) > 0 :
            print("Attention : Il y plusieurs sous-problèmes !")
            self.bfsFrom()
     
        
        # Résultat
        print(matString(self.VTo))
        print(matString(self.VFrom))
        self.valeurs = MparM(self.VTo,self.VFrom)
        print(matString(self.valeurs))
        
        self.impossibles = []
        # Case zéro : Impossible d'y passer une caisse :
        for y in range(self.level.height):
            for x in range(self.level.width):
                if self.valeurs[y][x] == 0 and self.level.is_floor((x,y)):
                    self.impossibles.append((x,y))
        
        
    def bfsFrom(self, depart=None) :
        """
        renseigne la matrice VFrom en y ajoutant la valeur
        2**i à self.VFrom[y][x]
        si la case est atteinte depuis la case depart (x,y)
        sont tenues en compte :
        - les positions des murs
        - l'existence des trois cases possibles pour permettre de POUSSER une caisse
        """
                #######
                ### ###
                ###.###
                # .$. # 
                ###.###
                ### ###
                #######
                
        # Test
        if depart is None :
            depart , i = self.boxes.pop() , self.valeursFrom.pop()
        else :
            self.boxes.remove(depart)
            i = self.valeursFrom.pop()
        # Fin test
        
        self.boxesVues.append(depart)
        value = i
        f = File()
        x,y = depart
            
        if self.level.is_floor(depart) :
            valfound = self.VFrom[y][x]        
            if valfound == 0 :
                self.VFrom[y][x] = value
                f.enqueue(depart)

        while not f.isempty() :
            pos = f.dequeue()
            x,y = pos
            if self.level.has_box((x,y)) :
                if (x,y) not in self.boxesVues :
                    self.boxesVues.append((x,y))
                    self.boxes.remove((x,y))
                    
            # Test
            if self.level.is_target((x,y)) :
                if (x,y) not in self.targetsVues : self.bfsTo((x,y))
            # Fin Test
            
            # On vérifie si les cases adjacentes opposées sont libres simultanément :
            # Verticalement
            
            if self.level.mightMoveUpDown(pos) :
            #if self.level.is_floor((x,y-1)) and self.level.is_floor((x,y+1)) :
                # Vers le haut
                valfound = self.VFrom[y-1][x]
                if valfound == 0 : # valfound == 0 :
                    self.VFrom[y-1][x] = value
                    f.enqueue((x,y-1))
                # Vers le bas
                valfound = self.VFrom[y+1][x]
                if valfound == 0 : # valfound == 0 :
                    self.VFrom[y+1][x] = value
                    f.enqueue((x,y+1))
                    
            if self.level.mightMoveRightLeft(pos) :
            #if self.level.is_floor((x-1,y)) and self.level.is_floor((x+1,y)) :
                valfound = self.VFrom[y][x-1]
                # Vers la gauche
                if valfound == 0 : # valfound == 0 :
                    self.VFrom[y][x-1] = value
                    f.enqueue((x-1,y))
                # Vers la droite
                valfound = self.VFrom[y][x+1]
                if valfound == 0  : # valfound == 0 :
                    self.VFrom[y][x+1] = value
                    f.enqueue((x+1,y))  
        return 
        
        
    def bfsTo(self, destination=None) :
        """
        renseigne la matrice VTo en y ajoutant la valeur
        2**i à self.VTo[y][x]
        jusaqu'à la case destination (x,y)
        - les positions des murs
        - l'existence des trois cases possibles pour permettre de TIRER une caisse
        les arcs entre les cases sont créés dynamiquement
        """
                #######
                ### ###
                ###S###
                # $.S # 
                ###S###
                ### ###
                #######
        
        # Test
        if destination is None :
            destination , i = self.targets.pop() , self.valeursTo.pop()
        else :
            self.targets.remove(destination)
            i = self.valeursTo.pop()
        # Fin test
        
        self.targetsVues.append(destination)
        value = i
        f = File()
        x,y = destination
        if self.level.is_floor(destination) :
            valfound = self.VTo[y][x]        
            if valfound == 0 :
                self.VTo[y][x] = value
                f.enqueue(destination)
            
            
        while not f.isempty() :
            pos = f.dequeue()
            x,y = pos
            if self.level.is_target((x,y)) :
                if (x,y) not in self.targetsVues :
                    self.targetsVues.append((x,y))
                    self.targets.remove((x,y))
            # Test
            if self.level.has_box((x,y)) :
                if (x,y) not in self.boxesVues : self.bfsFrom((x,y))
            # Fin Test
            
            # On vérifie si il existe deux cases qui sont libres du même côté, sur la mème composante :
            # Verticalement
            if self.level.mightComeFromLeft(pos) :
            # if self.level.is_floor((x-1,y)) and self.level.is_floor((x-2,y)) :
                valfound = self.VTo[y][x-1]
                if valfound < value : # valfound < value :
                    self.VTo[y][x-1] = value
                    f.enqueue((x-1,y))
                    
                    
            if self.level.mightComeFromRight(pos) :
            # if self.level.is_floor((x+1,y)) and self.level.is_floor((x+2,y)) :
                valfound = self.VTo[y][x+1]
                if valfound < value : # valfound < value :
                    self.VTo[y][x+1] = value
                    f.enqueue((x+1,y))
                    
            if self.level.mightComeFromAbove(pos) :
            # if self.level.is_floor((x,y-1)) and self.level.is_floor((x,y-2)) :
                valfound = self.VTo[y-1][x]
                if valfound < value : # valfound < value :
                    self.VTo[y-1][x] = value
                    f.enqueue((x,y-1))
            
            if self.level.mightComeFromBelow(pos) :
            # if self.level.is_floor((x,y+1)) and self.level.is_floor((x,y+2)) :
                valfound = self.VTo[y+1][x]
                if valfound < value : # valfound < value :
                    self.VTo[y+1][x] = value
                    f.enqueue((x,y+1))
        return 
    
    
    
def main() :
    pass

if __name__ == "__main__":
    main()