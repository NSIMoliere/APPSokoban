# Ce fichier accueille des éléments pui ne dépendent pas du jeu
# Classe file, pile
# Affichage de matrice de booléen
# ...


def MparM(m1,m2) :
    """
    Renvoit une matrice avec chaque élément multiplié par l'autre
    """
    m = MCreate(len(m1[0]),len(m1),0)
    for y in range(len(m1)) :
            for x in range(len(m1[0])) :
                m[y][x] = m1[y][x] * m2[y][x]
    return m

def MplusM(m1,m2,c1=1,c2=1) :
    """
    Renvoit une matrice avec chaque élément additionné par l'autre
    Eventuellement additions coefficientées par un poids
    """
    m = MCreate(len(m1[0]),len(m1),0)
    for y in range(len(m1)) :
            for x in range(len(m1[0])) :
                m[y][x] = c1 * m1[y][x] + c2 * m2[y][x]
    return m
    

def MboolCreate(width,height):
    """
    Renvoit une matrice de booléens False des dimensions voulues
    """
    m = [[False for x in range(width)]
                for y in range(height)]
    return m

def MCreate(width,height,val=0):
    """
    Renvoit une matrice de val=0 des dimensions voulues
    """
    m = [[val for x in range(width)]
                for y in range(height)]
    return m

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

def matString(m) :
    """
    Renvoit ligne par ligne la matrice
    """
    s = '\n'
    for i in range(len(m)) :
        for j in range(len(m[0])) :
            s += "{:>5}".format(str(m[i][j])) #Ici c'est juste pour un affichage correct, des tabulations ct trop long !
        s += '\n'
    return s


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

def sommeMat(m) :
    """
    Renvoit la somme des coef
    """
    somme = 0
    for x in range(len(m)) :
            for y in range(len(m[0])) :
                somme += m[x][y]
    return somme

def matNormalise(m) :
    """
    Renvoit la matrice avec le poids de chaque elements sur le poids total
    """
    somme = sommeMat(m)
    for x in range(len(m)) :
            for y in range(len(m[0])) :
                m[x][y] = round(m[x][y]/somme,3)                  
    return m

def matRound(m) :
    """
    Renvoit la matrice de valeurs arrondies
    """
    somme = sommeMat(m)
    for x in range(len(m)) :
            for y in range(len(m[0])) :
                m[x][y] = round(m[x][y],3)                  
    return m
    
def minMat(m1,m2) :
    """
    Renvoit coef par coef, la matrice des minimum
    """
    m = MCreate(len(m1[0]),len(m1),0)
    for y in range(len(m1)) :
            for x in range(len(m1[0])) :
                m[y][x] = min( m1[y][x], m2[y][x])
    return m

def tensionsMat(m):
    mhd = MCreate(len(m[0]),len(m),0)
    mhg = MCreate(len(m[0]),len(m),0)
    mvh = MCreate(len(m[0]),len(m),0)
    mvb = MCreate(len(m[0]),len(m),0)
    for i in range(len(m)) :
        acc = 0
        for j in range(len(m[0])) :
            if m[i][j] == 0 :
                acc = 0
            acc += m[i][j]
            mhd[i][j] = acc
        for j in range(len(m[0])-1,-1,-1) :
            if m[i][j] == 0 :
                acc = 0
            acc += m[i][j]
            mhg[i][j] = acc 
    for j in range(len(m[0])) :
        acc = 0
        for i in range(len(m)) :
            if m[i][j] == 0 :
                acc = 0
            acc += m[i][j]
            mvb[i][j] = acc
        for i in range(len(m)-1,-1,-1) :
            if m[i][j] == 0 :
                acc = 0
            acc += m[i][j]
            mvh[i][j] = acc
    tenseurshorizontaux = matNormalise(minMat(mvh,mvb))
    ratio = len(m)/(len(m[0]) + len(m)) # Ajustement si le plateau est rectangulaire (ratio = 1/2 pour carré)
    # print(matString(tenseurshorizontaux))
    tenseursverticaux = matNormalise(minMat(mhd,mhg))
    # print(matString(tenseursverticaux))
    mm = MplusM(matNormalise(minMat(mvh,mvb)),matNormalise(minMat(mhd,mhg)),ratio,1-ratio)
    print(matString(matRound(mm)))
    print(sommeMat(mm))
    return mm
    
    

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
    
    def peek(self) :
        if len(self.t) > 0 : return self.t[0]
        
    def popBigger(self) :
        """
        Pas le temps de faire propre l'élément est enfiler sous forme d'un tuple (element, poids)
        """
        maxP = self.t[0][1]
        maxI = 0
        for i in range(len(self.t)) :
            if self.t[i][1] > maxP :
                maxI = i
        return self.t.pop(maxI)
    
    def popSmaller(self) :
        """
        Pas le temps de faire propre l'élément est enfiler sous forme d'un tuple (element, poids)
        """
        maxP = self.t[0][1]
        maxI = 0
        for i in range(len(self.t)) :
            if self.t[i][1] < maxP :
                maxI = i
        return self.t.pop(maxI)
    
    
    def __contains__(self,x) :
        return x in self.t
    
    def isempty(self):
        if len(self.t)>0 :
            return False
        return True
