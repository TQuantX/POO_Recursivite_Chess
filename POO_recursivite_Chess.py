#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 19:12:20 2021

@author: Thomaths QuantX

Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)  https://creativecommons.org/licenses/by-nc-sa/4.0/
Under the following terms: 
Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. 
            You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
NonCommercial — You may not use the material for commercial purposes.
ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

"""

'''
ne sont pas (encore?) impl\'ement\'es la prise en passant

'''

    
import time

class Piece():
    '''
    Une pi\`ece a une couleur, un nom et une position
    Une case vide n'a pas de couleur, ni de nom (sp\'ecifique) mais une position
    
    La classe piece ne definit que les pieces et les mouvements possibles [avec prise en passant]
    
    '''   
    
    def __init__(self, couleur : str, name : str, position : tuple):
        
        dossier = 'images_pieces/'
        
        self.couleur = couleur
        self.nom = name
        self.position = position  #position (tuple) (x,y)
        self.image = dossier+couleur+'_'+name+'.png' if couleur is not None else None
        self.est_obstacle_a = None  #pieces de la meme couleur bloquant le passage
        self.targets = None  #cases atteignables a un instant t
        self.select = False
        self.mouvements_contraints = None #si echecs
        
        
    def mise_a_nu(self):
        #on garde juste la position
        self.couleur = None
        self.nom = None
        self.est_obstacle_a = None
        self.targets = None
        self.select = False
        self.image = None
        self.mouvements_contraints = None

        
    
    def deplacement_horvert(self, coord_objectif):
        return self.position[0] == coord_objectif[0] or self.position[1] == coord_objectif[1]
        
    
    def deplacement_diag(self, coord_objectif):
        
        if self.position[0] == coord_objectif[0]: #si meme abscisse, direction verticale 
            return False
        else:
            pente = (self.position[1]-coord_objectif[1])/(self.position[0]-coord_objectif[0])
            #print(pente)
            return pente == 1 or pente == -1
        
        
    def deplacement(self, coord_objectif):  #on liste juste les types de deplacements autoris\'es.
        
        if self.nom == 'rook': #pour la tour
           return self.deplacement_horvert(coord_objectif)
            
        elif self.nom == 'knight': 
            
            if abs(self.position[0]-coord_objectif[0]) == 1:  #si ecart des abscisses de 1
                if abs(self.position[1] - coord_objectif[1]) == 2: #forcement un ecart ordonnees de 2
                    return True
                
            elif abs(self.position[1]-coord_objectif[1]) == 1:  #si ecart des ordonnees de 1
                if abs(self.position[0] - coord_objectif[0]) == 2: #forcement un ecart abscisses de 2
                    return True
                    
        elif self.nom == 'bishop':
            return self.deplacement_diag(coord_objectif)
        
        elif self.nom == 'king':
            if abs(self.position[0]-coord_objectif[0]) <= 1 and abs(self.position[1]-coord_objectif[1]) <= 1:
                return True
            
        elif self.nom == 'queen':
            if self.deplacement_horvert(coord_objectif):
                return True
            elif self.deplacement_diag(coord_objectif):
                return True
            
        elif self.nom == 'pawn':            
            
            if self.position[1] == coord_objectif[1]: #si m\^eme ordonn\'ee
                pass
            
            else:                
                if self.couleur == 'white' and self.position[1]>coord_objectif[1] :  #on va en decroissant valeurs
                    sens = 1
                elif self.couleur == 'black' and self.position[1]<coord_objectif[1] :  #on va en decroissant valeurs
                    sens = -1
                else:
                    #print("probleme avec les pions dans le sens ! ")
                    return False
            
                if self.position[0] == coord_objectif[0]: #si meme abscisse
                    
                    if (self.position[1] == 6 and sens>0) or (self.position[1] == 1 and sens<0): #si au debut du mouvement
                        if 0 < sens*(self.position[1]-coord_objectif[1])<3: #deplacement verticale de 1 ou 2
                            return True                     
                                                
                    elif sens*(self.position[1]-coord_objectif[1]) == 1: #deplacement vertical de de 1
                        return True
                                            
                elif abs(self.position[0]-coord_objectif[0])==1: #si ecart abscisse de 1:  #prise possible
                    if sens*(self.position[1]-coord_objectif[1]) == 1: #deplacement vertical de de 1
                        return True                  
                                       
        return False

class Board():
    
    '''
    variables : 
        - contenu : un dictionnaire avec la pi\`ece sur chaque case. Cl\'e : coordonn\'ees de la case
        - overboard : idem mais avec les pi\`eces pouvant acc\'eder a cette case ! 
            [utile si graphiquement on veut surligner les pi\`eces qui ont acc\`es a une case]
    
    '''
    
    def __init__(self, longueur : int = 8, largeur : int = 8 ): 

        self.longueur = longueur
        self.largeur = largeur       

        self.position_rois = [(0,0),(0,0)]  #blanc[0], noir[1]
        self.mouvements_des_rois = [[None,None,None],[None,None,None]]
        self.roque_en_cours = False
        
        if self.largeur == 8:
            self.contenu = self.initialisation_usuelle()
            self.alphabet = "ABCDEFGH"
        else:
            self.contenu = {}
            self.alphabet = ""
            
        self.overboard ={}

        self.analyse_initiale_access() #on met a jours l'overboard        
        
        self.fait_echec = None
        self.echec_et_maths = None        
        self.joueur_en_cours = 'white'        
        self.history = None
        

        
    def initialisation_usuelle(self):  ## --------- OK ----------  
         
        assert self.largeur == 8, ""
        
        dict_pieces = { } 
        
        for i in range(self.largeur):
            dict_pieces[(i,1)] = Piece("black", "pawn", (i,1))
            dict_pieces[(i,self.longueur-2)] = Piece("white", "pawn", (i,self.longueur-2))
            
            for j in range(2,self.longueur-2):
                dict_pieces[(i,j)] = Piece(None,None, (i,j))      
        
        dict_pieces[(0,0)] = Piece("black", "rook", (0,0))
        dict_pieces[(1,0)] = Piece("black", "knight", (1,0))
        dict_pieces[(2,0)] = Piece("black", "bishop", (2,0))
        dict_pieces[(3,0)] = Piece("black", "queen", (3,0))
        dict_pieces[(4,0)] = Piece("black", "king", (4,0))
        
        self.position_rois[1] = (4,0)
        
        dict_pieces[(5,0)] = Piece("black", "bishop", (5,0))
        dict_pieces[(6,0)] = Piece("black", "knight", (6,0))
        dict_pieces[(7,0)] = Piece("black", "rook", (7,0)) 
                     
        
        dict_pieces[(0,self.longueur-1)] = Piece("white", "rook", (0,self.longueur-1))
        dict_pieces[(1,self.longueur-1)] = Piece("white", "knight", (1,self.longueur-1))
        dict_pieces[(2,self.longueur-1)] = Piece("white", "bishop", (2,self.longueur-1))
        dict_pieces[(3,self.longueur-1)] = Piece("white", "queen", (3,self.longueur-1))
        dict_pieces[(4,self.longueur-1)] = Piece("white", "king", (4,self.longueur-1))
        
        self.position_rois[0] = (4,self.longueur-1)       
        
        dict_pieces[(5,self.longueur-1)] = Piece("white", "bishop", (5,self.longueur-1))
        dict_pieces[(6,self.longueur-1)] = Piece("white", "knight", (6,self.longueur-1))
        dict_pieces[(7,self.longueur-1)] = Piece("white", "rook", (7,self.longueur-1))
        
        
        
        ## ---- pour faire des tests ---------------------------
        
        
        # dict_pieces[(5,2)] = Piece("white", "pawn", (5,2)) 
        # dict_pieces[(1,3)] = Piece("white", "bishop", (1,3))    
        # # dict_pieces[(4,4)] = Piece("black", "pawn", (4,4))    
        # dict_pieces[(4,5)] = Piece("white", "rook", (4,5))
        
        # dict_pieces[(4,1)] = Piece("black", "pawn", (4,1))
        
        # # dict_pieces[(3,4)] = Piece("white", "king", (3,4))     
        
        
        ## ---- fin des tests ---------------------------
          
                
        return dict_pieces                 
            
  
    
    
    def piece_en_cours(self,position):  ## --------- OK ----------  
        if self.contenu[position].couleur is not None:
            return self.contenu[position].couleur+' '+self.contenu[position].nom
        else:
            return "case vide"
    
    
    
    
    def __str__(self):  ## --------- OK ----------    
        
        print(end="   ")
        for i in range(self.largeur):
            #print(f"| {self.alphabet[i]} ", end=" ")
            print(i, end="    ")
        print("\n")
        
        for j in range(self.longueur):
            #print(f"{self.longueur-i} |", end="")
            print(j, end=" ")
            for i in range(self.largeur):
                piece = self.contenu[(i,j)]
                if piece.couleur is not None:
                    print(piece.couleur[0]+"_"+piece.nom[0:2], end="|")
                else:
                    print(end='    /')
            print("\n")
                        
        for _ in range(self.largeur+2):
            print("  _ ", end=" ")
        print("\n")
        
        return ""
    
    
    def normalisation(self,x,y): ## --------- OK ----------  
        u,v = 0,0
        nbre_cases = 0
        if x == 0:
            v = y//abs(y)  #normalisation a 1   
            nbre_cases = abs(y)                         
        elif y == 0:
            u= x//abs(x)  #normalisation a 1
            nbre_cases = abs(x)
        elif x!=0 and y!=0:
            u= x//abs(x)
            v = y//abs(y)
            nbre_cases = abs(x)
            
        return u,v, nbre_cases
    
        
   
    def rajout_si_pas_roque(self):        #on initialise pour le cas du roque : tours en targets     
        
        if self.joueur_en_cours == "white":
            place_r = 0
        elif self.joueur_en_cours == "black":
            place_r =1
        else:
            print("erreur dans les positions et codes couleurs !! ")
            return None
        
        if self.mouvements_des_rois[place_r][0] is None: 

            roi = self.position_rois[place_r]  
            
            for tour in [(0,roi[1]),(self.largeur-1,roi[1])]:  
                
                if tour[0]==0:
                    place_t = 1
                elif tour[0] == self.largeur-1:
                    place_t = 2
                else:
                    print("probleme")
                
                if self.contenu[tour].couleur == self.joueur_en_cours and self.contenu[tour].nom == 'rook':  
                    if self.mouvements_des_rois[place_r][place_t] is None: #si la tour n'a pas ete bougee
                        if self.contenu[roi].targets is None:
                            self.contenu[roi].targets = [tour]
                        elif tour not in self.contenu[roi].targets :                    
                            self.contenu[roi].targets.append(tour)
                            
                        self.enregistrement_dans_overboard(tour, roi, True)

  
    
    def implementation_du_roque(self,position_initiale_tour):
        '''
        C'est un mouvement particulier : 
            - deja on sait que initialement et finalement ni le roi ni la tour n'etaient des targets ennemies
            - mais initialement pouvaient etre des obstacles
            - et finalement peuvent prendre des places avec des targets amies
        '''
        
        if self.joueur_en_cours == "white":
            place_r = 0
        elif self.joueur_en_cours == "black":
            place_r =1
        else:
            print("erreur dans les positions et codes couleurs !! ")
            return None

             
        # -- concernant les positions -------
        position_initiale_roi = self.position_rois[place_r]
        position_finale_roi = self.mouvements_des_rois[place_r][1]
        position_finale_tour = self.mouvements_des_rois[place_r][0]        
        
        # -- quelles sont les pieces impactees ----- 
        # on refait un parcours des cases, que l'on avait deja fait auparavant, donc non optimisation, on aurait pu sauvegarder
        # par contre, il y a peu de cases, donc on perd en temps mais moins en memoire (vrai ?)
        # et c'est plus lisible il me semble
        
        pieces_impactees = [position_finale_roi,position_finale_tour]
        
        x, y, nombre_de_cases = self.normalisation(-position_initiale_roi[0]+position_initiale_tour[0],0)
        
        n = 0
        while n<nombre_de_cases+1:  #du roi inclu a la tour inclue aussi        
            
            case_en_cours = (position_initiale_roi[0]+n*x, position_finale_roi[1])
            n += 1
            
            if (self.contenu[case_en_cours].couleur is None) or (self.contenu[case_en_cours].couleur == self.joueur_en_cours): #utile ?                
                if self.contenu[case_en_cours].couleur is not None: #si roi ou tour, obstacles a qui ? 
                    if self.contenu[case_en_cours].est_obstacle_a is not None:
                        for allie in self.contenu[case_en_cours].est_obstacle_a:
                            pieces_impactees.append(allie)                            
                            
                    for target in self.contenu[case_en_cours].targets: #comme case vide entre roi et tour, forcement des target ! 
                        self.overboard[target].remove(case_en_cours)
                else:
                    if self.overboard[case_en_cours] is not None: #normalement, pas de targets ennemies ! condition pour roque
                        for allie in self.overboard[case_en_cours]:
                            pieces_impactees.append(allie) 
            else:
                print("bizarre, probleme de couleur de case")              
            
                    
        # -- on met a jours les informations des nouvelles positions
        
        # self.contenu[position_finale_roi].mise_a_nu() #pas utile mais si jamais 
        # self.contenu[position_finale_tour].mise_a_nu() #idem 
        self.position_rois[place_r] = position_finale_roi
        self.contenu[position_finale_roi].nom = 'king'
        self.contenu[position_finale_roi].image = self.contenu[position_initiale_roi].image 
        self.contenu[position_finale_roi].couleur = self.joueur_en_cours
        
        self.contenu[position_finale_tour].nom = 'rook'
        self.contenu[position_finale_tour].image = self.contenu[position_initiale_tour].image
        self.contenu[position_finale_tour].couleur = self.joueur_en_cours
        
        # -- le roque est fait, on ne met plus a None les elements concernant le roi
        self.roque_en_cours = False
        self.mouvements_des_rois[place_r][0] = 1
        self.mouvements_des_rois[place_r][1] = 1
        self.mouvements_des_rois[place_r][2] = 1        
    
        
        # -- on met des cases vides aux anciennes positions        
        self.contenu[position_initiale_roi].mise_a_nu()
        self.contenu[position_initiale_tour].mise_a_nu()
        
        # # -- et enfin on etudie la nouvelle configuration
        for allie in pieces_impactees:
            self.etude_des_parcours_possibles(self.contenu[allie])         

    
    def liberation_des_contraintes_silyavaitechec(self, roi_en_echec):
        #si echec et mat(hs), alors None, mais normalement le jeu s'arrete avant 
        if self.contenu[roi_en_echec].mouvements_contraints is not None:
            for element in self.contenu[roi_en_echec].mouvements_contraints:
                self.contenu[element].mouvements_contraints = None
            self.contenu[roi_en_echec].mouvements_contraints = None
        
    
    def etude_du_check(self,roi_en_echec):
            
        #si la piece qui fait echec, de coord self.fait_echec, est atteignable par une piece ennemie 
        #et si cette piece ennemi n'amene pas un autre echec -> dans ce cas la, c'est mat        
               
        #si on peut s'interposer sans non plus cr\'eer d'\'echec par une autre piece
        #on stock les pieces qui peuvent s'interposer chez le roi !         
        
        x,y,nombre_de_cases = self.normalisation(self.fait_echec[0][0]-roi_en_echec[0], self.fait_echec[0][1]-roi_en_echec[1])        

        n = 0
        while n<nombre_de_cases:
            cible = (self.fait_echec[0][0]-n*x, self.fait_echec[0][1]-n*y)
            n += 1
            for target in self.overboard[cible]:
                if self.contenu[target].couleur != self.contenu[self.fait_echec[0]].couleur: #c'est forcement une piece
                    if self.not_selfcheck(target,cible, modifications_ = False, analyse_ = True) is None :
                        
                        enregistrement = True
                        if self.contenu[target].nom == 'pawn':
                            if cible[0] == target[0] and self.contenu[cible].couleur is None :
                                pass
                            elif cible[0] != target[0] and self.contenu[cible].couleur == self.contenu[self.fait_echec[0]].couleur:
                                pass
                            else:
                                enregistrement = False
                                
                        if enregistrement : 
                            #on sauvegarde chez qui peut aller proteger le roi o\`u on il peut aller
                            self.enregistrement_dans_contraintes(cible, target, modifications_ = True)         
                            #on sauvegarde chez le roi qui sont les protecteurs
                            self.enregistrement_dans_contraintes(target, roi_en_echec, modifications_ = True)
                
        
        #le roi peut aussi bouger !! 
        if self.contenu[roi_en_echec].targets is not None:
            for target in self.contenu[roi_en_echec].targets:
                if self.not_selfcheck(roi_en_echec,target,  modifications_ = False, analyse_ = True) is None:
                    self.enregistrement_dans_contraintes(target, roi_en_echec, modifications_ = True)

        if self.contenu[roi_en_echec].mouvements_contraints is None:
            print("al cheikh mat ")
            self.echec_et_maths = True
    
    
    def mais_ou_est_le_roi_de_couleur(self, couleur): ## --------- OK ----------  
        position_du_roi = None  
        if couleur == "white":
            position_du_roi = self.position_rois[0]
        elif couleur == "black":
            position_du_roi = self.position_rois[1]
        else:
            print("err mais_ou_est_le_roi : un probleme dans le choix des rois, ")
        return position_du_roi
    
    
    
    def check_if_check(self,piece,cible):  ## --------- OK ---------- 
        
        if piece.couleur == "white":
            roi_oppose = self.mais_ou_est_le_roi_de_couleur("black")
        elif piece.couleur == "black":
            roi_oppose = self.mais_ou_est_le_roi_de_couleur("white")
        else:
            print("erreur dans la positon du roi ErrXV221")
            
        if cible == roi_oppose:            
            if piece.nom == 'pawn':  #cas du pion, si la piece est en face! 
                if piece.position[0] == cible[0]:
                    return None               
                        
            self.fait_echec = [piece.position,roi_oppose]
            #je marque le roi qui est en echec 
            print("echecs !!!! ")
            #self.etude_du_check(cible)
            
    
    def enregistrement_dans_overboard(self,cible,position_piece, modifications_ = False):   ## --------- OK ----------  
        if modifications_:
            if self.overboard[cible] is None :
                self.overboard[cible] = [position_piece]
            elif position_piece not in self.overboard[cible]:
                self.overboard[cible].append(position_piece)  
                
                      
    def enregistrement_dans_targets(self, cible,piece,modifications_ = False):
        if modifications_:
            if piece.targets is None:
                piece.targets = [cible]
            elif not cible in piece.targets:
                piece.targets.append(cible)
                
            #on verifie alors si on ne provoque pas de situation d'\'echec avec l'ennemy 
            self.check_if_check(piece, cible)
                
                                
    def enregistrement_dans_obstacles(self, cible,position_piece, modifications_ = False):  ## --------- OK ----------  
        #objet principal est la cible pour laquelle on enregistre ses obstacles
        if modifications_:
            if self.contenu[cible].est_obstacle_a is None:
                self.contenu[cible].est_obstacle_a = [position_piece]                        
            elif position_piece not in self.contenu[cible].est_obstacle_a:
                self.contenu[cible].est_obstacle_a.append(position_piece) 
                
                
    def enregistrement_dans_contraintes(self, sa_cible, piece_initiale, modifications_ = False):  ## --------- OK ----------  
        #objet principal est la cible pour laquelle on enregistre ses obstacles
        if modifications_:
            if self.contenu[piece_initiale].mouvements_contraints is None:
                self.contenu[piece_initiale].mouvements_contraints = [sa_cible]                        
            elif sa_cible not in self.contenu[piece_initiale].mouvements_contraints :
                self.contenu[piece_initiale].mouvements_contraints.append(sa_cible) 
            
    
    def parcours(self, piece, position, x, y, modifications_ = False):      ## --------- OK ----------  
        '''
        recursive ! 
        '''
        
        if (position[0]+x,position[1]+y) in self.contenu.keys():   #si on ne sort pas du plateau    
            
            cible = (position[0]+x,position[1]+y)
            
            if piece.deplacement(cible): #si le deplacement initial a final est possible, on coupe sinon
                
                if self.contenu[cible].couleur != piece.couleur:                    

                    self.enregistrement_dans_overboard(cible,piece.position, modifications_)                    
                    self.enregistrement_dans_targets(cible,piece,modifications_)
                            
                    if self.contenu[cible].couleur is None:                                    
                        self.parcours(piece,cible, x, y, modifications_)               
                                                                                    
                else: #on peut atteindre la case mais il y a une piece de m\^eme couleur qui bloque     

                    self.enregistrement_dans_obstacles(cible, piece.position , modifications_)

                        
                                            
    def etude_des_parcours_possibles(self, piece, modifications_ = True): ## --------- OK ----------  
        
        '''        
        Si pas bloquer, on avance, sinon on passe a la piece suivante : voir m\'ethode parcours        
        quand une piece bloque une autre, on stocke sa position. Comme cela, quand on va bouger cette piece, on saura 
        quelles autres pieces elle bloquait et pouvoir relancer une analyse des d\'eplacements possibles des pieces maintenant non bloqu\'ees par elle 
        '''       
        
        if piece.couleur is None:
            pass                
        
        elif piece.nom =='knight': #cas particulier o\`u on ne se d\'eplace pas en +1 ou -1
            
            for i in [-1,1]:
                for j in [-2,2]:                    
                    #1ere configuration 
                    cible_1 = (piece.position[0]+i, piece.position[1]+j)
                    cible_2 = (piece.position[0]+j, piece.position[1]+i)
                    
                    for cible in [cible_1,cible_2]:
                        if cible in self.contenu.keys(): #autrement dit, si on ne sort pas du plateau
                            if self.contenu[cible].couleur != piece.couleur:
                                
                                #la piece peut aller sur la case, on actualise l'overboard             
                                self.enregistrement_dans_overboard(cible, piece.position, modifications_)
                                
                                #et ses targets
                                self.enregistrement_dans_targets(cible, piece, modifications_)   
                                
                                    
                            else: #sinon, si meme couleur, alors l'autre piece est un obstacle pour elle
                                self.enregistrement_dans_obstacles(cible, piece.position , modifications_)               

        else:
            #pour toutes les pieces se depla\c cant de 1 en 1               
            '''
            si x = 0, on n'\'evolue que de 1 en 1 verticalement (y=1 ou y=-1) : a -> a+y -> (a+y)+y ...
            si x = 1 [x=-1] et y = 0 : on garde meme ordonn\'ee mais on va vers x [d\'e]croissants donc droite[gauche]
            si x = 1 and y = 1 : on va en diagonale vers bas a droite                     
            '''
            
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:                            
                    if not (x == y and x == 0): #on bouge
                        self.parcours(piece, piece.position, x, y, modifications_) #recursive !! 
                        
                        
    
    def analyse_initiale_access(self) :        ## --------- OK ----------  
        '''
        On prend chaque piece une par une et on regarde o\`u elle peut aller initialement        
        '''
        #on initialise l'overboard,
        for row in range(self.longueur):
            for column in range(self.largeur):
                self.overboard[(column,row)] = None
            
        #for row in [0,1,self.longueur-1,self.longueur-2,2]:
        for row in range(self.longueur):
            for column in range(self.largeur):    
                self.etude_des_parcours_possibles(self.contenu[(column,row)],True)         
                    
                
        #on initialise pour le cas du roque : tours en targets
        for roi in self.position_rois :
            if self.contenu[roi].targets is None:
                self.contenu[roi].targets = [(0,roi[1]),(self.largeur-1,roi[1])]
            else:                    
                
                self.contenu[roi].targets.append((0,roi[1]))
                self.contenu[roi].targets.append((self.largeur-1,roi[1]))
                
                self.enregistrement_dans_overboard((0,roi[1]), roi, True)
                self.enregistrement_dans_overboard((self.largeur-1,roi[1]), roi, True)
                            
    
    def deplacement(self,position_initiale, position_finale, promotion = None):  ## --------- OK (a priori)  ----------  
        
        '''
        - on met le nom a case vide et on change le nom de la piece 
        - si elle bloquait des pieces, ce n'est plus le cas, il faut mettre a jours le deplacement de ces pieces de m\^eme couleur
        - idem pour la position d'arriv\'ee o\`u maintenant elle ne bloque plus mais devient targets
        - si la position finale etait target, elle devient obstacle (targets a refaire)           

        Normalement, ici, on a d\'eja v\'erifi\'e les situations d'\'echecs, de mat, ...  donc que le d\'eplacement !! 
        
        '''        
        
        #normalement, pas de probleme, on peut y aller
        #print(f"\n on se deplace de {position_initiale} a {position_finale} \n")
        
        #--- historique maj --------  
        initialement = self.contenu[position_initiale].couleur+'_'+self.contenu[position_initiale].nom
        case_perdue = ''
        if self.contenu[position_finale].couleur is not None:
            case_perdue = self.contenu[position_finale].couleur+'_'+self.contenu[position_finale].nom
        if self.history is None:
            self.history =[[position_initiale,position_finale, initialement,case_perdue]]   
        else:
            self.history.append([position_initiale,position_finale, initialement,case_perdue])         
        
        
        
        # ----------- a) on enleve de l'overboard  (resum\'e des d\'eplacements) la position d'arrivee et finale     
        ## ---- la piece jouee ne va plus "a priori" aux cases de ses targets initiales
        # (on pourrait optimiser mais pas maintenant : notamment si pas pion, peut revenir en arriere   

        for element in self.contenu[position_initiale].targets: #il y a forcement une target     
            self.overboard[element].remove(position_initiale)
        self.contenu[position_initiale].targets = None
        
                
        ## ---- la case d'arrivee ne peut plus se deplacer du coup si piece il y avait
        if self.contenu[position_finale].targets is not None : #si pas case vide
            for element in self.contenu[position_finale].targets:
                self.overboard[element].remove(position_finale) 
            self.contenu[position_finale].targets = None 
            
                               
        pieces_impactees_initial = [position_finale]  #au moins la piece que l'on bouge ... 
        
        ## ----- on regarde les pieces impactees au depart : 
        
        # la piece initialement bloquait des pieces de meme couleurs, donc laisse un vide et possiblement du passage                      
        if self.contenu[position_initiale].est_obstacle_a is not None:

            for element in self.contenu[position_initiale].est_obstacle_a:
                if element not in pieces_impactees_initial:

                    pieces_impactees_initial.append(element)
                    #self.contenu[element].targets = None       

        #self.contenu[position_initiale].est_obstacle_a = None  #sera mise a nu, donc inutile ici        

        #ou \'etait la cible de piece de la couleur oppos\'ee    
        if self.overboard[position_initiale] is not None:

            temp_overboard = self.overboard[position_initiale].copy()
            for element in temp_overboard :
                if element not in pieces_impactees_initial:

                    pieces_impactees_initial.append(element)  

                    #on enleve la o\`u elle pouvait aller car on va la reetudier ensuite
                    if self.contenu[element].targets is not None:   #si elles avaient des targets (normalement oui)

                        for sous_target in self.contenu[element].targets:  #on enleve les sous_targets de la piece impactee de l'overboard
                           if self.overboard[sous_target] is not None:
                               self.overboard[sous_target].remove(element)
                        self.contenu[element].targets = None                         
                     
                    if self.overboard[position_initiale] is not None:
                        if element in self.overboard[position_initiale]:
                            self.overboard[position_initiale].remove(element)    #idem 
            temp_overboard = None
        
        
        # --------- On regarde la position d'arrivee : elle bloquait qui et etait la target de qui ? 
        
        # --- si elle etait un obstacle, elle devient une target    
        if self.contenu[position_finale].est_obstacle_a is not None:
            for element in self.contenu[position_finale].est_obstacle_a:
                if self.contenu[element].targets is None :
                    self.contenu[element].targets = [position_finale]
                else:
                    self.contenu[element].targets.append(position_finale)
                    
                self.overboard[position_finale].append(element)                   
        
        
        # -- si elle etait une target, elle devient un obstacle si meme couleur, sinon reste target        
                       
        pieces_impactees_final = [ ]
        if self.overboard[position_finale] is not None:
            temp_overboard = self.overboard[position_finale].copy()

            for element in temp_overboard : #pour les pieces qui allaient a la position finale

                pieces_impactees_final.append(element)       
                if self.contenu[element].targets is not None:   #si elles avaient des targets (normalement oui)

                    for sous_target in self.contenu[element].targets:  #on enleve les sous_targets de la piece impactee de l'overboard
                       if self.overboard[sous_target] is not None:
                           self.overboard[sous_target].remove(element)
                    self.contenu[element].targets = None                

            temp_overboard = None    

            
        #--------------- On met les informations de  la piece dans la nouvelle position     
        
        if promotion is None:
            self.contenu[position_finale].nom = self.contenu[position_initiale].nom
            self.contenu[position_finale].image = self.contenu[position_initiale].image
            self.contenu[position_finale].targets = None
            self.contenu[position_finale].est_obstacle_a = None
            self.contenu[position_finale].couleur = self.contenu[position_initiale].couleur 
            
            # ------- on met a jours la position des rois
            if self.contenu[position_finale].nom == 'king':
                if self.contenu[position_finale].couleur == 'white':
                    place =0                    
                elif self.contenu[position_finale].couleur == 'black':
                    place = 1
                else:
                    print("erreur avec le changement de position du roi")
                self.position_rois[place] = position_finale
                if self.mouvements_des_rois[place] is None:
                    self.mouvements_des_rois[place] = position_finale
                    
            
        else:
            self.contenu[position_finale] = Piece(self.contenu[position_initiale].couleur,promotion, position_finale)
          
        # ----------  on met une case vide a la position initiale
        self.contenu[position_initiale].mise_a_nu()     

        
        # --------- enfin, on etudie les pieces impactees initialement
    
        for element in pieces_impactees_initial+pieces_impactees_final:             
            self.etude_des_parcours_possibles(self.contenu[element])   
                
        self.contenu[position_finale].mouvements_contraints = None
        self.rajout_si_pas_roque()  #si un roi a 'et'e impact'e
                

    def trois_pieces_alignees(self,position_du_roi,ennemy, position_piece):
        
        '''
        si 3 pieces (un roi et son allie, et l'autre ennemy) sont alignees
        renvoie la position de l'ennemy si alignees
        renvoie None sinon 
        '''
        if position_piece is None:
            return None
        
        
        situation_problematique_possible = None 
        
        #il faut que la piece soit entre le roi et l'ennemy
        if position_du_roi[0] == ennemy[0]: 
            if position_du_roi[0] == position_piece[0]:
                #s'ils sont tous sur meme abscisse
                if (position_piece[1]-position_du_roi[1])*(position_piece[1]-ennemy[1])<=0:
                    #la piece est entre les deux
                    situation_problematique_possible = ennemy
            
        elif position_du_roi[1] == ennemy[1]: 
            if position_du_roi[1] == position_piece[1] :
                #s'ils sont sur meme ordonnee
                if (position_piece[0]-position_du_roi[0])*(position_piece[0]-ennemy[0])<=0:
                    #la piece est entre les deux
                     situation_problematique_possible = ennemy
            
        else :  #sur meme droite ? 
            
            pente_a = (position_du_roi[1] - ennemy[1])/(position_du_roi[0] - ennemy[0])
            ordonnee_origine = position_du_roi[1] - pente_a*position_du_roi[0]
            
            if (position_piece[1]-pente_a*position_piece[0]) == (position_du_roi[1] - pente_a*position_du_roi[0]):
                #sont sur meme droite 
                if (position_piece[1]-position_du_roi[1])*(position_piece[1]-ennemy[1])<=0:
                    #la piece est entre les deux
                     situation_problematique_possible = ennemy
                     
        return situation_problematique_possible
     

    
    
    def not_selfcheck(self, position_initiale, position_finale = None,  modifications_ = False, analyse_  = False):
        
        '''
        Fonction qui regarde si le deplacement d'une piece ne provoque pas une situation d'\'echec
        On scanne toutes les pieces de couleurs oppos\'ees qui peuvent passer par la case a la position_initiale
        
         si position finale est None, on verifie juste si des deplacements sont autorisees (en opposition)
        
        
        renvoie None si tout va bien :  True , la position de l'ennemy sinon !  False
        position _finale est forecment dans les targets !! 
        
        '''
        
        #print(f"\n on regarde {self.piece_en_cours(position_initiale)} en {position_initiale}")

        #si c'est le roi qui demande a bouger
        
        if self.contenu[position_initiale].nom == "king":
            #est-il libre de bouger ? 
            if position_finale is None: 
                if self.contenu[position_initiale].targets is None:                   
                    return False #ne peut pas bouger (renvoyer un truc different de None)                
                else:
                    
                    case_libre = 0                                
                    for case in self.contenu[position_initiale].targets:  #normalement, les meme couleurs sont dans obstacles                      
                        if self.overboard[case] is not None:
                            for ennemy in self.overboard[case]:  
                                if (self.contenu[ennemy].couleur is None) or (self.contenu[ennemy].couleur == self.contenu[position_initiale].couleur) :
                                    case_libre += 1
                    if case_libre  == 0 :
                        return False
                     
                
            else:

                #si une case ennemy peut aller dessus
                if self.overboard[position_finale] is not None:
                    #print(self.overboard[position_finale])
                    for ennemy in self.overboard[position_finale]:  
                        if self.contenu[ennemy].couleur != self.contenu[position_initiale].couleur:
                            if self.contenu[ennemy].couleur is not None :
                                return False
                            
                #sinon case peut etre ennemy et donc etre mang\'ee, donc regarder obstacles ! 
                if self.contenu[position_finale].est_obstacle_a is not None:
                    return False

        
        elif self.overboard[position_initiale] is None: #si aucun ennemi ne va sur la case
            pass
        else:

            couleur_en_cours = self.contenu[position_initiale].couleur            
            
            position_du_roi = self.mais_ou_est_le_roi_de_couleur(couleur_en_cours)
            
            situation_problematique_possible = None
            
            for ennemy in self.overboard[position_initiale]:  #ennemy pouvant aller a position initiale
                
                #if self.contenu[ennemy].couleur != couleur_en_cours: #si vraiment ennemy [condition pas n\'ecessaire normalement]
                    
                #si l'ennemy peut atteindre le roi
                if self.contenu[ennemy].deplacement(position_du_roi):
                    
                    #on regarde si les trois pieces sont alignes
                    situation_problematique_possible = self.trois_pieces_alignees(position_du_roi, ennemy, position_initiale)
                            
                    if situation_problematique_possible is not None: #si on bien est sur uen meme droite
            
                        #comme entre l'ennemy et le roi, il y a des cases a etudier (knight n'est pas concern\'e)
                        
                        #si on reste au final entre le roi et l'ennemy, voire jsuqu'a l'ennemy
                        if position_finale is not None:
                            if self.trois_pieces_alignees(position_du_roi, ennemy, position_finale) is not None: #is none si pos_final is                             
                                self.contenu[position_initiale].mouvements_contraints = None
                            elif self.contenu[position_initiale].mouvements_contraints is not None :
                                if not position_finale in self.contenu[position_initiale].mouvements_contraints : 
                                    return ennemy
                            else:
                                return ennemy  #on ne doit pas bouger
                                
                        #sinon
                        else:
                            #s'il y a des pieces en interposition, on peut bouger
                            x, y, nbre_case = self.normalisation(-position_initiale[0]+position_du_roi[0],-position_initiale[1]+position_du_roi[1])

                            n = 0
                            piece_en_interposition = False
                            while n<nbre_case-1 and not piece_en_interposition:  #moins celle du roi et de la piece, non ? 
                                n += 1
                                if self.contenu[(position_initiale[0]+n*x,position_initiale[1]+n*y)].couleur == couleur_en_cours:
                                    piece_en_interposition = True
                                    
                                    
                            if not piece_en_interposition:                               

                                #s'il n'y a pas d'autres pieces en interpositions, on va voir si on peut toujours bouger entre le roi et la piece
                                #au moins d'une case                                 
                                
                                x, y, nbre_case = self.normalisation(-position_initiale[0]+ennemy[0],-position_initiale[1]+ennemy[1])
                                
                                n= 0
                                while n<nbre_case:                   
                                    n += 1
                                    cible = (position_initiale[0]+n*x, position_initiale[1]+n*y)
                                   
                                    position_forcee = True
                                    if cible in self.contenu[position_initiale].targets:
                                        if self.contenu[position_initiale].nom == 'pawn': #cas particulier du pion
                                            if x!=0:
                                                if self.contenu[(position_initiale[0]+x, position_initiale[1]+y)].couleur is None:
                                                    position_forcee = False
                                        
                                        if position_forcee and not analyse_ :
                                            self.enregistrement_dans_contraintes(cible, position_initiale, modifications_ = True)

                                if self.contenu[position_initiale].mouvements_contraints is None:

                                    return ennemy
        return None
                
            
    def etude_du_deplacement(self,position_initiale, position_finale):
        
        if self.echec_et_maths is not None:  #le jeu est fini
            return False  
                    
        elif self.fait_echec is not None : #si echec
            roi = self.fait_echec[1]
            #on regarde le roi qui est en echec (ses contraintes sont ses protecteurs)
            #if position_initiale != roi:  #si on ne regarde pas le roi
            if (position_initiale == roi) or (position_initiale in self.contenu[roi].mouvements_contraints):
                
                if position_initiale == roi and abs(roi[0]-position_finale[0])>1:
                    #le roque en temps d'échec est interdit
                    pass
                
                #si la piece est un protecteur                
                elif position_finale in self.contenu[position_initiale].mouvements_contraints: 
                    
                    #s'il peut donc se deplacer a une position qui protege le roi
                    self.liberation_des_contraintes_silyavaitechec(roi) #on remet tout a zero/None
                    self.fait_echec = None
                    return True  #on le deplace
                else:
                    print("ce deplacement laissera votre roi en \'echec")   
            else:
                print("ce deplacement laissera votre roi en \'echec")   
                    
        elif self.contenu[position_initiale].targets is not None: #si la piece a des opportunit\'es
            
            if position_finale in self.contenu[position_initiale].targets: #si une de ces opportunit\'es est la o\`u elle veut aller
                
                if self.contenu[position_initiale].nom == 'king' and abs(position_finale[0]-position_initiale[0])>1:   #cas du roque !  
                    
                    if self.joueur_en_cours == self.contenu[position_initiale].couleur : 
                        roque_possible = True
                        #si le roi n'a jamais boug'e 
                        if self.joueur_en_cours == 'white':
                            place_r = 0 
                        elif self.joueur_en_cours == 'black':
                            place_r = 1
                        else:
                            print('probleme')
                            return False
                       
                        if self.mouvements_des_rois[place_r][0] is None: #mouvements_des_rois 
                            #si le roi n'est pas en echec 
                            if self.fait_echec is None:
                                #si on a bien une tour de meme couleur aux extremites
                                if (position_finale[0] == 0) or (position_finale[0] == (self.largeur-1)):
                                    if (position_finale[1] == 0) or (position_finale[1] == (self.longueur-1)):
                                        if self.contenu[position_finale].nom == 'rook' and self.contenu[position_finale].couleur == self.joueur_en_cours :
                                            
                                            if (position_finale[0] == 0):
                                                place_t = 1
                                            elif (position_finale[0] == self.largeur-1):
                                                place_t = 2
                                            else:
                                                print('probleme')
                                                return False
                                            
                                            x, y, nbre_case = self.normalisation(position_finale[0]-position_initiale[0],position_finale[1]-position_initiale[1])
                                            if y != 0:
                                                return False
                                            #si pas de pieces entre les deux                                            
                                            #si entre les deux, pas de targets ennemie (ne se met pas en echec)                                           
                                            n = 0
                                            possible_position_roi = None #arrivee du roi, non quantique
                                            possible_position_tour = None #arrivee du roi, non quantique
                                            while n < nbre_case: #sauf la tour                                                
                                                n += 1
                                                cible = (position_initiale[0]+n*x,position_initiale[1])
                                                if n==1:
                                                    possible_position_tour = cible
                                                elif n==2:
                                                    possible_position_roi = cible
                                                if n!= nbre_case and self.contenu[cible].couleur is not None: #entre les deux sauf la tour en n=nbre_case                            
                                                    return False                                                
                                                if self.overboard[cible] is not None:
                                                    for target in self.overboard[cible]:                                                        
                                                        if self.contenu[target].couleur != self.joueur_en_cours:       
                                                            print("roque impossible, une case est target d'une ennmie")
                                                            return False
                                                        
                                                                                
                                            self.mouvements_des_rois[place_r][0] = possible_position_tour
                                            self.mouvements_des_rois[place_r][1] = possible_position_roi
                                            self.mouvements_des_rois[place_r][2] = 1  
                                            self.roque_en_cours = True
                                            return True

               
                elif self.not_selfcheck(position_initiale, position_finale) is None : #si en partant, elle ne provoque pas forc\'ement de situation d'\'echec ! 
                    if self.contenu[position_initiale].mouvements_contraints is None:
                        deplacement_autorisee = True  #pour etudier les cas particulier (pion, ....)
                        
                        if self.contenu[position_initiale].nom == 'pawn':
                            
                            if position_initiale[0] == position_finale[0] : #si meme abscisse
                                if self.contenu[position_finale].couleur is not None: #si pas case vide
                                    deplacement_autorisee = False  #on ne bouge pas
                                    
                            elif self.contenu[position_finale].couleur != self.contenu[position_initiale].couleur: #si vide ou couleur ennemie
                                if self.contenu[position_finale].couleur is None:  #si pas vide
                                    deplacement_autorisee = False  #on ne bouge pas
                                    
                        ## Si on d\'eplace la pi\`ece, est-on en \'echec ?? 
                        
                        if deplacement_autorisee:                                             
                            #self.deplacement(position_initiale, position_finale)
                            return True
                    elif position_finale in self.contenu[position_initiale].mouvements_contraints:
                        return True

                else:
                    print("ce deplacement laissera votre roi en \'echec")          
                    

            else:
                print("deplacement impossible, retentez")
        else:
            print("deplacement impossible, retentez")
        
        return False   
    
  


    def etude_du_cas_pat(self):
        #print("a reflechir")        
        return None
    
    
    def all_content(self):
        return self.contenu.keys()
    
    def get_case_image(self,position):        
        return self.contenu[position].image
    
    def get_position_roi(self):
        return self.mais_ou_est_le_roi_de_couleur(self.joueur_en_cours)
    
    def is_piece(self,position):
        if self.contenu[position].couleur is not None:
            return True
        else:
            return False
    
    def get_overboard(self,position):
        return self.overboard[position]

    def get_targets(self, position):
        if self.contenu[position].targets is not None:
            return self.contenu[position].targets
        else:
            return None
    
    def get_select(self,position):
        return self.contenu[position].select
    
    def get_couleur(self,position):
        return self.contenu[position].couleur
    
    def get_name(self,position):
        return self.contenu[position].nom
    
    def set_select(self,position, valeur : bool):
        if valeur in [True,False]:
            self.contenu[position].select = valeur
            
    def remove_constraints(self,position):
        self.contenu[position].mouvements_contraints = None
            
    def available_motion(self,position_initiale, position_finale):
        return self.etude_du_deplacement(position_initiale, position_finale)
            
    def set_motion(self,position_initiale, position_finale,promotion = None):
        #on est autoris\'e a bouger
        
        if self.roque_en_cours:
            self.implementation_du_roque(position_finale)
        else:        
            self.deplacement(position_initiale, position_finale,promotion)
        
        # -- on a boug'e donc on peut passer au joueur suivant
        self.change_joueur()  
        return self.joueur_en_cours        
        
    def is_pat(self):
        #print("il faudrait afficher les pieces qui peuvent encore bouger")
        return self.etude_du_cas_pat()
    
    def is_echec(self):
        if self.fait_echec is not None:
            #si on sait que l'on a echec mais que l'on n'a pas encore etudie si protecteurs 
            if self.contenu[self.fait_echec[1]].mouvements_contraints is None:
                self.etude_du_check(self.fait_echec[1])
            return self.fait_echec[0]   
        return None
    
    def is_mat(self):
        return self.echec_et_maths
    
    def get_player_having_to_play(self):
        return self.joueur_en_cours
    
    def set_player_having_to_play(self, couleur):
        self.joueur_en_cours = couleur
        return couleur
    
    
    def study_of_targets(self, position):  #cas du pion o\`u m\^eme si les targets possibles sont nombreuses, on ne peut pas aller partout
        
        if self.contenu[position].mouvements_contraints is not None:            
            return self.contenu[position].mouvements_contraints
        
        elif self.contenu[position].nom != 'pawn':
            return self.contenu[position].targets
        else:
            targets_possibles = None
            for each_target in self.contenu[position].targets :
                available_target = False                
                if position[0]==each_target[0]:
                    if self.contenu[each_target].couleur is None:
                        available_target = True
                elif self.contenu[each_target].couleur is not None:
                    if self.contenu[each_target].couleur != self.contenu[position].couleur:
                        available_target = True       
                
                if available_target:                    
                        if targets_possibles is None:
                            targets_possibles = [each_target]
                        else:
                            targets_possibles.append(each_target)                            
            return targets_possibles
        
    def is_pawn_promotion(self,selection,y):
        if self.contenu[selection].nom == 'pawn' and (y== 0 or y == self.longueur-1): #pas de soucis, les pions ne vont que dans un sens
            return True
        else:
            return False
        
    def induce_selfcheck(self,position_init, position_finit = None):
        return self.not_selfcheck(position_init, position_finit)
    
    def couleur_gagnante(self):
        return self.contenu[self.fait_echec[0]].couleur
        
    def change_joueur(self):
        if self.joueur_en_cours == 'white':
            self.joueur_en_cours = 'black'
            return self.joueur_en_cours
        elif self.joueur_en_cours == 'black':
            self.joueur_en_cours = 'white'
            return self.joueur_en_cours
           
    
    
        
    
## --------------------------- Part 2 : the display ---------------------------

    
import pygame as pg
#import time  #deja fait 
import sys



class Button:
    #https://pythonprogramming.altervista.org/buttons-in-pygame/
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, text,  pos, font, taille, text_color=(0,0,0), bg=(255,255,255), feedback=""):
        
        self.x, self.y = pos
        self.font = pg.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
            self.change_text(text, text_color,bg)
 
    def change_text(self, text, text_color=(0,0,0), bg=(255,255,255)):
        """Change the text whe you click"""
        self.enonce = text
        self.color_text = text_color
        self.bg = bg
        self.text = self.font.render(text, 1, pg.Color(text_color[0],text_color[1],text_color[2]))
        self.size =  self.text.get_size()
        self.surface = pg.Surface(self.size)
        self.surface.fill(pg.Color(bg[0],bg[1],bg[2]))
        self.surface.blit(self.text, (0, 0))
        self.rect = pg.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        
    def set_enonce(self,joueur_en_cours):
        text_bis = f"it's the turn of the {joueur_en_cours} king to play ! "
        self.change_text( text_bis,self.color_text, self.bg)
            
    def click(self, event):
        x, y = pg.mouse.get_pos()
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:         
                if self.rect.collidepoint(x, y):
                    
                    if self.enonce == 'Click to Quit':
                        print(" ************** \n *   Bye Bye  *\n ************** \n")
                        pg.quit()
                        return True                    
                    elif self.enonce == 'Restart':
                        print(" ********************* \n *   Restarting ...  *\n ********************* \n\n")
                        return True
                    elif self.enonce in ['rook', 'queen', 'bishop', 'knight']:
                        return True
                   
                return False
            
            
class Animation():
    
    def __init__(self, param = None):
        self.parameters = param
        
        
    def would_give_check(self, position_of_piece_who_would_induce_selfcheck,position_mouse,B):
        piece_who_would_be_played = B.get_couleur(position_mouse)+' '+B.get_name(position_mouse)
        piece_who_would_induce_selfcheck = B.get_couleur(position_of_piece_who_would_induce_selfcheck)+' '+B.get_name(position_of_piece_who_would_induce_selfcheck)
        print(f"\n\n if {piece_who_would_be_played} in {position_mouse} is played, at least {piece_who_would_induce_selfcheck} in {position_of_piece_who_would_induce_selfcheck} will reach the king ! ")
                        
    def The_End(self,winning_color):
        print(f"{winning_color} has won the game")
        
    def ItsPat(self):
        print("Pat ! ")
        
    def check_situation(self, joueur_en_cours):
        pass
        #print(f"{joueur_en_cours} is checked, I've checked ! ")
      
    
    def animation_motion(self,position_piece,position_finale, B):
        
        return None
    
        # --- parameters of the moving piece ---

        couleur_piece = B.get_couleur(position_piece)
        nom_piece = B.get_nom(position_piece)
        
        # --- parameters of the removed piece ---
        couleur_removed_piece = B.get_couleur(position_removed_piece)
        if couleur_removed_piece is not None: #if not empty space
            nom_removed_piece = B.get_nom(position_removed_piece)
        else:
            nom_removed_piece = None
            
                   
            
            
#set color with rgb
white,black,grey, red = (255,255,255),(0,0,0),(120,120,120),(204,0,34)            
mediumseagreen, seagreen = (60,179,113), (46,139,87)
            
def chessboard_drawing(gameDisplay, B,board_longueur,board_largeur,size):
    
    #drawing the initial board -----------------------------------
    #https://stackoverflow.com/questions/45945254/make-a-88-chessboard-in-pygame-with-python/45948976
    
    gameDisplay.fill(white)    
    cnt = 0
    for i in range(0,board_longueur):
        for z in range(0,board_largeur):
            #check if current loop value is even
            if cnt % 2 == 0:
                pg.draw.rect(gameDisplay, white,[size//2+size*z,size//2+size*i,size,size])
            else:
                pg.draw.rect(gameDisplay, grey, [size//2+size*z,size//2+size*i,size,size])
            pg.draw.rect(gameDisplay,black,[size//2+size*z,size//2+size*i,size,size],1)
            cnt +=1
        #since theres an even number of squares go back one value
        cnt-=1
    #Add a nice boarder
    pg.draw.rect(gameDisplay,black,[size//2,size//2,board_largeur*size,board_longueur*size],1)

    #getting the pieces and putting them on the board        
    for case in B.all_content():
        if B.get_case_image(case) is not None:
            position_image = (size//2+15 + case[0]*size, size//2+15 + case[1]*size) #le 15 pour ajuster
            gameDisplay.blit(pg.image.load(B.get_case_image(case)),position_image)   
    ## *-------------------------------------
    pg.display.update()


def draw_rectangle(gameDisplay, case, size):
    if (case[0]+case[1])%2 == 0:
        couleur_case = white
    else:
        couleur_case = grey         

    pg.draw.rect(gameDisplay, couleur_case,[size//2+size*case[0],size//2+size*case[1],size,size])
    pg.draw.rect(gameDisplay,black,[size//2+size*case[0],size//2+size*case[1],size,size],1)

# def afficher_a_qui_le_tour(joueur_en_cours,font,position,gameDisplay):    
#     textsurface = font.render(f"it's the turn of the {joueur_en_cours} king to play ! ",True, (0, 0, 20))
#     gameDisplay.blit(textsurface,position)


def main():  
        
    board_largeur = 8
    board_longueur = 8
    
    B = Board(board_longueur,board_largeur)
    animation = Animation("A")
    
    pg.init()       
    clock = pg.time.Clock()  #pour les rafraichissement des frames
    font = pg.font.SysFont("Arial",30)
                  
    #Size of squares
    size = 76 #a moduler en fonction de la taille de l'ecran et des dimensions du plateau 
    
    #set display
    gameDisplay = pg.display.set_mode((board_largeur*size+400,board_longueur*size+100))
    
    #caption
    pg.display.set_caption("Chess")    
    
    aujoueur_button = Button("A qui le tour ? ",(board_largeur*size+size, 50),font=20,taille = 0, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
    restart_button = Button("Restart",(board_largeur*size+175, 150),font=30,taille = 0, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")    
    quit_button = Button("Click to Quit",(board_largeur*size+145, 235),font=30, taille =50, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
   
    rook_promotion_button = Button("rook",(board_largeur*size+150, 365),font=30, taille =50, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
    queen_promotion_button = Button("queen",(board_largeur*size+150, 415),font=30, taille =50, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
    bishop_promotion_button = Button("bishop",(board_largeur*size+150, 465),font=30, taille =50, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
    knight_promotion_button = Button("knight",(board_largeur*size+150, 515),font=30, taille =50, text_color=(0,0,0), bg=(255,255,255),feedback="You clicked me")
        
    chessboard_drawing(gameDisplay, B, board_longueur,board_largeur,size)
    
    #beginning of logic
    gameExit = False

    demi_size = size//2    
    
    # --- pour afficher les cases sur lesquelles une piece peut aller
    selection = None  
    cases_selectionnees = None
    
    # --- pour afficher les pieces qui peuvent aller sur la case, juste en passant la souris dessus
    ancien_x, ancien_y = 0, 0
    
    cases_highlighted = None

    
    choix_promotion = False    
    joueur_en_cours = B.get_player_having_to_play()
    
    while not gameExit:      
        
        if B.is_pat() is not None :
            animation.ItsPat()
            gameExit = True          
            
        elif B.is_mat() is not None :
            animation.The_End(B.couleur_gagnante())
            gameExit = True            
            
        else:            
            
            if B.is_echec() is not None :
                animation.check_situation(joueur_en_cours)        
                gameDisplay.blit(pg.image.load(B.get_case_image(B.is_echec())),(board_largeur*size+150, 350))
                textsurface = font.render('Echec par ', True, (0, 0, 20))
                gameDisplay.blit(textsurface,(board_largeur*size+120,315))
            #else:                                                                            
                #pg.draw.rect(gameDisplay,white,[board_largeur*size+120,315,2*size,2*size])
                
            
            for event in pg.event.get():
                
                aujoueur_button.set_enonce(joueur_en_cours)              

                
                ## ---- si on doit quitter le jeu
                if event.type == pg.QUIT or quit_button.click(event)  : 
                    pg.quit()
                    gameExit = True

                    
                elif restart_button.click(event):
                    B = Board(board_longueur,board_largeur)
                    selection = None
                    ancien_x, ancien_y = 0, 0
                    cases_selectionnees = None
                    cases_highlighted = None
                    choix_promotion = False         
                    joueur_en_cours = B.set_player_having_to_play("white") 
                    chessboard_drawing(gameDisplay, B, board_longueur,board_largeur,size)
                    
                elif choix_promotion:   
                    
                    pg.draw.rect(gameDisplay, white, [board_largeur*size+100,300,250,300])
                    pg.draw.rect(gameDisplay, black, [board_largeur*size+100,300,250,300],3)
                    rook_promotion_button.show(gameDisplay)
                    queen_promotion_button.show(gameDisplay)
                    knight_promotion_button.show(gameDisplay)
                    bishop_promotion_button.show(gameDisplay)
                    
                    textsurface = font.render('Promotion', True, (0, 0, 20))
                    gameDisplay.blit(textsurface,(board_largeur*size+120,315))
                    
                    promotion = None
                    if rook_promotion_button.click(event):
                        promotion = 'rook'
                    elif queen_promotion_button.click(event):
                        promotion = 'queen'
                    elif knight_promotion_button.click(event):
                        promotion = 'knight'
                    elif bishop_promotion_button.click(event):
                        promotion = 'bishop'
                        
                    if promotion is not None:
                        choix_promotion = False
                        joueur_en_cours = B.set_motion(selection,(x,y),promotion)                   
                        print(B)
                        draw_rectangle(gameDisplay, selection, size) #on remet la case de d\'epart en \'etat          
                        draw_rectangle(gameDisplay, (x,y), size) #idem pour arrivee
                        position_image = (size//2+15 +x*size, size//2+15 + y*size) #le 15 pour ajuster
                        gameDisplay.blit(pg.image.load(B.get_case_image((x,y))),position_image)  #on met la piece a l'arrivee
                        pg.display.update()
                        selection = None
                        
                        #on remet un blanc la o\`u \'etait mis les promotions
                        pg.draw.rect(gameDisplay, white, [board_largeur*size+90,290,270,320]) 
                                            
                #sinon, on joue
                else:
                    position_souris = pg.mouse.get_pos()                

                    #si la souris est sur le plateau de jeu et si une case a une piece, on illumine o\`u elle peut aller       
                    if (position_souris[0]-demi_size)>=0 and ((position_souris[0]-demi_size)//size)<board_largeur:
                        if (position_souris[1]-demi_size)>=0 and ((position_souris[1]-demi_size)//size)<board_longueur:
                                                        
                            x = (position_souris[0]-demi_size)//size
                            y = (position_souris[1]-demi_size)//size
                            
                            if x != ancien_x or y != ancien_y : 
                                
                                #on remet les cases a l'ancienne couleur
                                cases_a_decolorer = [ ]
                                if cases_highlighted is not None:
                                    cases_a_decolorer = cases_a_decolorer + cases_highlighted
                                    cases_highlighted = None 
                               
                                if cases_a_decolorer != []:
                                    for each_case in cases_a_decolorer : 
                                        #on remet la case en noir ou blanc
                                        draw_rectangle(gameDisplay,each_case, size)                                        
                                        if B.is_piece(each_case):
                                            position_image = (size//2+15 +each_case[0]*size, size//2+15 + each_case[1]*size) #le 15 pour ajuster
                                            gameDisplay.blit(pg.image.load(B.get_case_image(each_case)),position_image)   
                                    
                                    
                                #si une piece peut avoir acces a la case, alors on l'illumine                                        
                                if B.get_overboard((x,y)) is not None :
                                    cases_highlighted = B.get_overboard((x,y)).copy()
                                    couleur_case = red
                                    for each_case in cases_highlighted:                                    
                                        #on la met en rouge
                                        pg.draw.rect(gameDisplay, couleur_case,[size//2+size*each_case[0],size//2+size*each_case[1],size,size])
                                        #on met un contour noir
                                        pg.draw.rect(gameDisplay,black,[size//2+size*each_case[0],size//2+size*each_case[1],size,size],1)
                                        #on remet les pieces par dessus
                                        if B.is_piece(each_case):
                                            position_image = (size//2+15 +each_case[0]*size, size//2+15 + each_case[1]*size) #le 15 pour ajuster
                                            gameDisplay.blit(pg.image.load(B.get_case_image(each_case)),position_image)   

                                                                
                            ## --------- si on clique sur une case (vide ou non)
                            if event.type == pg.MOUSEBUTTONDOWN:  
                                
                                if pg.mouse.get_pressed()[2] : #clic-droit    
                                    
                                    if selection is not None and B.get_select((x,y)) : 
                                     
                                        B.set_select(selection,False)  
                                        selection = None                                        
                                        cases_selectionnees = None        
                                        joueur_en_cours = B.change_joueur()
                                            
                                                                         
                                                     
                                elif pg.mouse.get_pressed()[0] :  
                                        
                                        if selection is None and not B.get_select((x,y)) : 
                                            
                                            if B.is_piece((x,y)):           #si on ne selectionne pas une case vide
                                                if B.get_targets((x,y)) is not None and B.get_couleur((x,y)) == joueur_en_cours : #si on peut la bouger !!
                                                    
                                                    is_a_piece_who_would_induce_selfcheck = B.induce_selfcheck((x,y))                         
                                                        
                                                    if (is_a_piece_who_would_induce_selfcheck is None) or (is_a_piece_who_would_induce_selfcheck == False):
                                                        
                                                        #if B.get_targets(selection) is not None: #redondant avvec if B.get_targets((x,y)) is not None                                                                                                                  
                                                        #cas particulier du pion, dans ma configuration, on ne doit pas illuminer si diag vides : a faire ?
                                                        cases_possibles = B.study_of_targets((x,y)) 
                                                        if cases_possibles is not None:
                                                            selection = (x,y)
                                                            B.set_select(selection, True) 
                                                            cases_selectionnees = [selection] + cases_possibles      
                                                    else:
                                                        animation.would_give_check(is_a_piece_who_would_induce_selfcheck,(x,y),B)   

                                                                            
                                        elif selection is not None : #si on a une piece de selectionnee
                                            
                                            if B.get_select((x,y)): #on deselectionne la piece   (normalement, seule piece selectionnee)                             
                                                B.set_select(selection,False)       
                                                # if B.is_echec() is None: 
                                                #     B.remove_constraints(selection)
                                                selection = None                                                        
                                                
                                            else:                   #sinon on bouge
                                                #if B.get_targets(selection) is not None: #si selectionnee, a des targets nons nulles !! 
                                                if (x,y) in B.get_targets(selection):  #si on peut se dirigier vers la case 
                                                    if B.available_motion(selection,(x,y)): #si on ne provoque pas d'echec ou autre
                                                    #if B.induce_selfcheck(selection, (x,y)) is None: 
                                                        if B.is_pawn_promotion(selection,y):
                                                            
                                                            choix_promotion = True
                                                            
                                                            # pg.draw.rect(gameDisplay, black, [board_largeur*size+100,300,250,300],3)
                                                            # rook_promotion_button.show(gameDisplay)
                                                            # queen_promotion_button.show(gameDisplay)
                                                            # knight_promotion_button.show(gameDisplay)
                                                            # bishop_promotion_button.show(gameDisplay)
                                                            
                                                            # textsurface = font.render('Promotion', True, (0, 0, 20))
                                                            # gameDisplay.blit(textsurface,(board_largeur*size+120,315))
    
    
                                                        else:                                                        
                                                            joueur_en_cours = B.set_motion(selection,(x,y))
                                                            #print(B)
                                                            selection = None
                                                            pg.draw.rect(gameDisplay, white, [board_largeur*size+100,300,250,300])
                                                    
                                                                                   
                            if cases_selectionnees is not None:                                         
                                for each_case in cases_selectionnees:                                             
                                    
                                    if (each_case[0]+each_case[1])%2 == 0:
                                        if selection is not None :
                                            couleur_case = (128,170,255)
                                        else:
                                            couleur_case = white
                                    else:
                                        if selection is not None :
                                            couleur_case = (51,119,255)
                                        else:
                                            couleur_case = grey         
                            
                                    pg.draw.rect(gameDisplay, couleur_case,[size//2+size*each_case[0],size//2+size*each_case[1],size,size])
                                    pg.draw.rect(gameDisplay,black,[size//2+size*each_case[0],size//2+size*each_case[1],size,size],1)
                                    
                                    if B.is_piece(each_case):
                                        position_image = (size//2+15 +each_case[0]*size, size//2+15 + each_case[1]*size) #le 15 pour ajuster
                                        gameDisplay.blit(pg.image.load(B.get_case_image(each_case)),position_image)   
                                        
                                if selection is None:
                                    cases_selectionnees = None 
                                 
        if not gameExit:
            
            gameDisplay.blit(pg.image.load(B.get_case_image(B.get_position_roi())),(board_largeur*size+200, 75))
            textsurface = font.render('--------------------------------', True, (0, 0, 20))
            gameDisplay.blit(textsurface,(board_largeur*size+60,125))
            
            textsurface = font.render('--------------------------------', True, (0, 0, 20))
            gameDisplay.blit(textsurface,(board_largeur*size+60,260))
                        
            aujoueur_button.show(gameDisplay)
            quit_button.show(gameDisplay)

            restart_button.show(gameDisplay)
            clock.tick(30) #fps rafraichissement
            pg.display.update()        
        
    pg.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()    

