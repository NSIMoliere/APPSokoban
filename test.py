DIRS = [(0, -1),  # up
        (0, 1),   # down
        (-1, 0),  # left
        (1, 0),   # right
       ]
    
def ajouteVoisin(noeud):
    dict={}
    listenew=[]
    for i in range(len(noeud)):
        for mx,my in DIRS:
            newnoeud=[]
            if bougeable(noeud[i][0]+mx,noeud[i][1]+my):
                for j in range(len(noeud)):
                    if j!=i:
                        newnoeud.append(noeud[j])
                newnoeud.append((noeud[i][0]+mx,noeud[i][1]+my))
                listenew.append(tuple(newnoeud))
    listenew.sort()
    dict={noeud:listenew}
    print(dict)
    
def bougeable(a,b):
    return True