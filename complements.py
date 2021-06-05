# Ce fichier accueille des éléments pui ne déoende pas du jeu
# Classe file, pile
# Affichage de matrice de booléen
# ...

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