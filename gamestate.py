#!/usr/bin/python2.7

import const
import random


class GameState(object):
    #stores games state
    def __init__(self):
        #initialize a tetris board with 20 rows and 10 columns. 0 = not filled, 1-7 = type of block
        self.board = [[ 0 for x in range(const.board_w) ] for y in range(const.board_h)]
        self.score = 0
        self.level_score=0
        self.level = 1
        self.curr_piece = None
        self.next_piece = None
        self.game_mode = 1
        self.lines = 0
        self.lines_till_next_level=10
        self.alive = 1
    def set_game_mode(self, num):
        self.game_mode = num
    def get_next_piece(self):
        #randomly returns what the next piece will be. A piece is a list of 3 elements, it's shape, a list of the 4 blocks it covers, and its orientation
        a = random.choice(range(1,8))  
		
        piece = [a]
        if a==1:
            #I block
            piece.append([ (3,0),(4,0),(5,0),(6,0) ])
        elif a==2:
            #reverse L
            piece.append([ (3,0), (3,1), (4,1), (5,1) ])
        elif a==3:
            #L
            piece.append([ (5,0), (5,1), (4,1), (3,1) ])
        elif a==4:
            #square
            piece.append([ (4,0), (5,0), (4,1), (5,1) ])
        elif a==5:
            #right snake
            piece.append([ (3,1), (4,1), (4,0), (5,0) ])
        elif a==6:
            #T block
            piece.append([  (4,0), (3,1),(4,1), (5,1) ])
        elif a==7:
            #left snake
            piece.append([ (3,0),(4,0),(4,1), (5,1)   ])
        piece.append(0) 
        return piece
    def check_board(self,tmp_board):
        checker = 0
        for i in range(const.board_w):
            for j in range(const.board_h):
                if self.board[j][i] - tmp_board[j][i]:
                    checker +=1
        return checker
    def make_piece(self):
        if self.next_piece == None:
            self.next_piece = self.get_next_piece()
        self.curr_piece= self.next_piece
        self.next_piece = self.get_next_piece()
        
    def print_board(self):
        for i in range(20):
            print(self.board[i]),
            print
    def moveRight(self):
        for i,j in self.curr_piece[1]:
            if i>=9:
                return
            
        new_coords = []
        
        for k in range(len(self.curr_piece[1])):
           new_coords.append ((self.curr_piece[1][k][0]+1,self.curr_piece[1][k][1]))
        for i,j in new_coords:
            if self.board[j][i]:
                return
        self.curr_piece[1] = new_coords
    def moveLeft(self):
        for i,j in self.curr_piece[1]:
            if i<=0:
                return 
        new_coords = []
        
        for k in range(len(self.curr_piece[1])):
           new_coords.append((self.curr_piece[1][k][0]-1,self.curr_piece[1][k][1]))
        for i,j in new_coords:
            if self.board[j][i]:
                return
        self.curr_piece[1] = new_coords
    def moveDown(self):
        for i,j in self.curr_piece[1]:
            if j>=19:
                self.place_piece_on_board();
                self.curr_piece = None
                return
            
            if self.board[j+1][i]:
                self.place_piece_on_board()
                self.curr_piece = None
                return
            
        curr_coords = self.curr_piece[1]
        
        for k in range(len(self.curr_piece[1])):
           self.curr_piece[1][k] = (self.curr_piece[1][k][0],self.curr_piece[1][k][1]+1)
    
    def place_piece_on_board(self): 
        counter = 0
        tmp_board = [[ 0 for x in range(const.board_w) ] for y in range(const.board_h)]

        for i in range(const.board_w):
            for j in range(const.board_h):
                tmp_board[j][i] = self.board[j][i]
        for i,j in self.curr_piece[1]:
            tmp_board[j][i] = self.curr_piece[0]
        if self.check_board(tmp_board) == 4:
            self.board = tmp_board
        else:
            print("error")
            sys.exit(0)

        
    def checkRow(self):
        list_of_full_rows = [] 
        for i in range(const.board_h):
            check=0
            for j in range(const.board_w):
                if self.board[i][j]:
                    check+=1
            #if row is full, then check = 10, so add ito the list of full rows
            if check == 10:
                list_of_full_rows.append(i)
                
        for i in list_of_full_rows:
            for j in reversed(range(i+1)):
                if j!=0:
                    self.board[j] = [0,0,0,0,0,0,0,0,0,0]
                    self.board[j] = self.board[j-1] 
            self.lines_till_next_level-=1
            self.score += len(list_of_full_rows) * 10;
            self.level_score += len(list_of_full_rows) * 10
        if self.lines_till_next_level <= 0:
            self.level+=1
            self.lines+=1
            self.lines_till_next_level = 10
    def check_game_over(self):
        for i in range(const.board_w):
            if self.board[0][i]:
                self.alive = False
                return True
    def create_incomplete_row(self):
        a = random.choice(range(0,10))
        for i in range(const.board_w):
            for j in range(const.board_h-1):
                self.board[j][i] = self.board[j+1][i]
        for i in range(const.board_w):
            if i != a:
                self.board[19][i] = 8;
    def check_win_condition(self,opp_score, opp_alive):
        if self.game_mode == 2:
            #speed run
            if self.level ==10:
                return True
            else:
                return False
        elif self.game_mode == 1:
            #competitive
            if not opp_alive:
                return True
            else:
                return False
        elif self.game_mode == 0:
            #casual
            if not opp_alive:
                if opp_score < self.score:
                    return True
            else:
                return False
        return False
    def rotate_cw(self):
        if self.curr_piece[0] == 1:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0] + 2,self.curr_piece[1][0][1]-1))
                new_coords.append((self.curr_piece[1][1][0] + 1, self.curr_piece[1][1][1]))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1] +1))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]+2))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0] - 2,self.curr_piece[1][0][1]+1))
                new_coords.append((self.curr_piece[1][1][0] - 1, self.curr_piece[1][1][1]))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1] -1))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]-2))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0 
        elif self.curr_piece[0] == 2:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0] + 2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0] + 1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0],self.curr_piece[1][0][1]+2))
                new_coords.append((self.curr_piece[1][1][0] + 1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 2
            elif self.curr_piece[2] == 2:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0] -1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 3
            elif self.curr_piece[2] == 3:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0],self.curr_piece[1][0][1]-2))
                new_coords.append((self.curr_piece[1][1][0] -1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0
        elif self.curr_piece[0] == 3:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0],self.curr_piece[1][0][1]+2))
                new_coords.append((self.curr_piece[1][1][0] - 1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0]+1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0] -1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 2
            elif self.curr_piece[2] == 2:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0],self.curr_piece[1][0][1]-2))
                new_coords.append((self.curr_piece[1][1][0] +1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 3
            elif self.curr_piece[2] == 3:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]+2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0] +1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0		
        elif self.curr_piece[0] == 5:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]+1,self.curr_piece[1][0][1]-1))
                new_coords.append((self.curr_piece[1][1][0], self.curr_piece[1][1][1]))
                new_coords.append((self.curr_piece[1][2][0]+1, self.curr_piece[1][2][1]+1))
                new_coords.append((self.curr_piece[1][3][0], self.curr_piece[1][3][1]+2))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-1,self.curr_piece[1][0][1]+1))
                new_coords.append((self.curr_piece[1][1][0], self.curr_piece[1][1][1]))
                new_coords.append((self.curr_piece[1][2][0]-1, self.curr_piece[1][2][1]-1))
                new_coords.append((self.curr_piece[1][3][0], self.curr_piece[1][3][1]-2))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0
        elif self.curr_piece[0] == 6:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]+1,self.curr_piece[1][0][1]+1))
                new_coords.append((self.curr_piece[1][1][0] +1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0]-1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-1,self.curr_piece[1][0][1]+1))
                new_coords.append((self.curr_piece[1][1][0]+1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] -1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 2
            elif self.curr_piece[2] == 2:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-1,self.curr_piece[1][0][1]-1))
                new_coords.append((self.curr_piece[1][1][0] -1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 3
            elif self.curr_piece[2] == 3:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]+1,self.curr_piece[1][0][1]-1))
                new_coords.append((self.curr_piece[1][1][0] -1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0] +1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0	
        elif self.curr_piece[0] == 7:
            if self.curr_piece[2] == 0:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]+2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0]+1, self.curr_piece[1][1][1]+1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0]-1, self.curr_piece[1][3][1]+1))
                for i,j in new_coords:
                    
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return

                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 1 
            elif self.curr_piece[2] == 1:
                new_coords = []
                new_coords.append((self.curr_piece[1][0][0]-2,self.curr_piece[1][0][1]))
                new_coords.append((self.curr_piece[1][1][0]-1, self.curr_piece[1][1][1]-1))
                new_coords.append((self.curr_piece[1][2][0], self.curr_piece[1][2][1]))
                new_coords.append((self.curr_piece[1][3][0]+1, self.curr_piece[1][3][1]-1))
                for i,j in new_coords:
                    if j>19 or j<0:
                        return
                    if i>9 or i<0:
                        return
                    if self.board[j][i]:
                        return
                self.curr_piece[1] = new_coords
                self.curr_piece[2] = 0

