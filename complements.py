# Ce fichier accueille des éléments pui ne dépendent pas du jeu
# Classe file, pile
# Affichage de matrice de booléen
# ...

def containsTrue(m):
    """
    Renvoie le premier (x,y) True d'une matrice de bool
    sinon False
    """
    for x in range(len(m)) :
            for y in range(len(m[0])) :
                if m[x][y] :
                    return y,x
    return False

def MboolTodec(m):
    """
    Transforme une matrice de 0, et 1 ou de True et False en un nombre décimal
    """
    s = '0b'
    for i in range(len(m)) :
            for j in range(len(m[0])) :
                if m[j][i] :
                    s += '1'
                else :
                    s += '0'  
    return int(s,2) # Transforme un booléen en base 2 en décimal

def MboolTobinTab(m1) :
    """
    Transforme une matrice de booléen en une matrice de 0 et 1
    0 pour False et 1 pour True
    """
    m = [[0 for x in range(len(m1[0]))]
                for y in range(len(m1))]
    for i in range(len(m1)) :
        for j in range(len(m1[0])) :
            if m1[i][j] :
                m[i][j] = 1
    return m

def matToString(matrice) :
    """
    Une matrice de Booléen sous forme de X pour False
    Ne sert que pour l'affichage dans le terminal
    """
    s = '\n'
    for i in range(len(matrice)) :
        for j in range(len(matrice[0])) :
            if matrice[i][j] :
                s = s + ' '
            else :
                s = s + '#'
        s += '\n'
    return s

'''
JETER
def verboseMbool(matrice) :
    """
    Une matrice de Booléen sous forme de X pour False
    Ne sert que pour l'affichage dans le terminal
    """
    verbose(matToString(matrice))
    

def verboseMbool(matrice) :
    """
    Une matrice de Booléen sous forme de X pour False
    Ne sert que pour l'affichage dans le terminal
    """
    s = ''
    for i in range(len(matrice)) :
        for j in range(len(matrice[0])) :
            if matrice[i][j] :
                s = s + ' '
            else :
                s = s + 'X'
        s += '\n'
    verbose(s)
'''

def andMbool(m1,m2) :
    """
    Opération m1 And m2
    Renvoit une matrice de booléen de deux autres matrices m1 et m2
    On suppose que m2 a les mêmes dimensiones que m1
    """
    m = [[False for x in range(len(m1[0]))]
                for y in range(len(m1))]
    for i in range(len(m1)) :
        for j in range(len(m1[0])) :
            if m1[i][j] and m2[i][j] :
                m[i][j] = True
    return m

'''
JETER
def andMbool(m1,m2) :
    """
    Renvoit une matrice de booléen de deux autres matrices m1 et m2
    """
    m = [[False for x in range(len(m1[0]))]
                for y in range(len(m1))]
    for i in range(len(m1)) :
        for j in range(len(m1[0])) :
            if m1[i][j] and m2[i][j] :
                m[i][j] = True
    return m
'''

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
            return False
    
    def __contains__(self,x) :
        return x in self.t
    
    def isempty(self):
        if len(self.t)>0 :
            return False
        return True

'''
JETER
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
            return False
    
    def __contains__(self,x) :
        return x in self.t
    
    def isempty(self):
        if len(self.t)>0 :
            return False
        return True
'''