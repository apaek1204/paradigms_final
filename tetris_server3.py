#!/usr/bin/python3
'''#!/usr/bin/env/python'''

PORT = 41016

import pygame
import os
import sys
import random
import const
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue

from twisted.internet import task

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

def draw_screen(surface, game_state, OPP_level, OPP_score, OPP_lines):
    
    pygame.draw.rect(surface, (125,125,125), (const.left-5, const.top-5, const.board_w*const.block_size+10, const.board_h*const.block_size+10))
    pygame.draw.rect(surface, (20,20,20), (const.left,const.top,const.board_w*const.block_size, const.board_h*const.block_size))
    
    font = pygame.font.SysFont('Arial', 25)
    smallfont = pygame.font.SysFont('Arial', 15)
    pygame.draw.rect(surface, (125,125,125), (270,45,110,150))
    surface.blit(font.render('Next', True, (255,255,255)), (300,50))
    if game_state.next_piece:
        for i, j in game_state.next_piece[1]:
            pygame.draw.rect(surface, const.color_list[game_state.next_piece[0]], (230+i*const.block_size,100+j*const.block_size, const.block_size, const.block_size))

    pygame.draw.rect(surface, (125,125,125), (270, 200, 110, 125))
    surface.blit(font.render("YOU:", True, (255,255,255)), (300,210))
    surface.blit(smallfont.render("Score: ", True, (255,255,255)), (280, 245))
    surface.blit(smallfont.render(str(game_state.score),True, (255,255,255)),(350, 245))
    surface.blit(smallfont.render("Level: ", True, (255,255,255)), (280, 270))
    surface.blit(smallfont.render(str(game_state.level), True, (255,255,255)), (350,270))
    surface.blit(smallfont.render("Attacks: ", True, (255,255,255)), (280,295))
    surface.blit(smallfont.render(str(game_state.lines), True, (255,255,255)), (350,295))
    pygame.draw.rect(surface, (125,125,125), (270, 330, 110, 125))
    surface.blit(font.render("OPP:", True, (255,255,255)), (300,340))
    surface.blit(smallfont.render("Score: ", True, (255,255,255)), (280, 375))
    surface.blit(smallfont.render(str(OPP_score),True, (255,255,255)),(350, 375))
    surface.blit(smallfont.render("Level: ", True, (255,255,255)), (280, 400))
    surface.blit(smallfont.render(str(OPP_level), True, (255,255,255)), (350,400))
    surface.blit(smallfont.render("Attacks: ", True, (255,255,255)), (280,425))
    surface.blit(smallfont.render(str(OPP_lines), True, (255,255,255)), (350,425))
    
    
    
    
    for i in range( const.board_h):
        for j in range(const.board_w):
            curr = game_state.board[i][j]
            if curr != 0:
                current_color = const.color_list[curr]
                pygame.draw.rect(surface, current_color, (const.left+j*const.block_size, const.top+i*const.block_size, const.block_size,const.block_size))
         
    if game_state.curr_piece:        
        for i,j in game_state.curr_piece[1]:
            curr = game_state.curr_piece[0]
            if curr != 0:
                current_color = const.color_list[curr]
                pygame.draw.rect(surface, current_color, (const.left+i*const.block_size, const.top+j*const.block_size, const.block_size,const.block_size))
 
    pygame.display.flip()
    
def game_over_lost():
    pygame.init()
    surface = pygame.display.set_mode((400,500))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        font = pygame.font.SysFont('Arial', 30)
        smallfont = pygame.font.SysFont('Arial', 20)
        surface.blit(font.render('GAME OVER!', True, (255,255,255)), (100,150))
        pygame.display.flip()
        surface.blit(smallfont.render('Sorry you lost :(', True, (255,255,255)), (120, 300))
            

def game_over_win():
    pygame.init()
    surface = pygame.display.set_mode((400,500))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        font = pygame.font.SysFont('Arial', 30)
        smallfont = pygame.font.SysFont('Arial', 20)
        surface.blit(font.render('CONGRATULATIONS!', True, (255,255,255)), (50,150))
        pygame.display.flip()
        surface.blit(smallfont.render('You won! :D', True, (255,255,255)), (150, 300))
            
def rage_quit(PacketConnectionObject):
    pygame.init()
    surface = pygame.display.set_mode((400,500))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("sad for c")
                running=False
                PacketConnectionObject.m.stop()
        font = pygame.font.SysFont('Arial', 30)
        smallfont = pygame.font.SysFont('Arial', 20)
        surface.blit(font.render('GAME OVER!', True, (255,255,255)), (100,150)) 
        surface.blit(smallfont.render('Why did you quit? :C', True, (255,255,255)), (100, 300))
        pygame.display.flip()

def run_game(PacketConnectionObject):
    pygame.init()
    surface = pygame.display.set_mode((400,500))
    running = True
    clock = pygame.time.Clock()
    #game_state = PacketConnectionObject.game_state
    game_over = False
    downclock = 0
    game_win = False
    #while running and not game_over and not game_win:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c and PacketConnectionObject.game_state.curr_piece:
                PacketConnectionObject.game_state.rotate_cw()
            if event.key == pygame.K_q: 
                running = False
            if event.key == pygame.K_SPACE:
                #Needs to set packet to send new row
                None
    if PacketConnectionObject.game_state.curr_piece == None:
       PacketConnectionObject.game_state.make_piece()
    #need to check packet if a row was sent, then call game.state.create_incomplete_row() 
    PacketConnectionObject.game_state.checkRow()
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_RIGHT]: PacketConnectionObject.game_state.moveRight();
    if pressed[pygame.K_LEFT]: PacketConnectionObject.game_state.moveLeft();
    if pressed[pygame.K_DOWN]: PacketConnectionObject.game_state.moveDown();
    
    if(downclock%10==0): 
        if PacketConnectionObject.game_state.curr_piece:
           PacketConnectionObject.game_state.moveDown()
    
    game_over= PacketConnectionObject.game_state.check_game_over()
# score level, lines, alive

    #OPP_score = 0
    #OPP_level = 0
    #OPP_lines = 0
    #OPP_alive = True
    game_win = PacketConnectionObject.game_state.check_win_condition(PacketConnectionObject.OPP_score, PacketConnectionObject.OPP_alive)
    draw_screen(surface, PacketConnectionObject.game_state,PacketConnectionObject.OPP_score, PacketConnectionObject.OPP_level,PacketConnectionObject.OPP_lines)
    downclock+=1
    #clock.tick(50*PacketConnectionObject.game_state.level)
    if game_win:
        PacketConnectionObject.m.stop()
        game_over_win()
    elif game_over:
        PacketConnectionObject.m.stop()
        game_over_lost()
    elif not running:
        PacketConnectionObject.m.stop()
        PacketConnectionObject.m = task.LoopingCall(rage_quit, (PacketConnectionObject))
        PacketConnectionObject.m.start(1/60)
        #rage_quit()

def main(PacketConnectionObject): 
    pygame.init()
    surface = pygame.display.set_mode((400,500))
    running = True
    #connection = False
    game = False
    #while running:
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
             running=False

    font = pygame.font.SysFont('Arial', 30)
    smallfont = pygame.font.SysFont('Arial', 20)
    surface.blit(font.render('Tetris', True, (255,255,255)), (165,150))
    if PacketConnectionObject.connection:
        surface.blit(smallfont.render('Connected! Press enter to continue', True, (255,255,255)), (50, 300))
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RETURN]:
            running = False
            game = True
    else:
        surface.blit(smallfont.render('Connecting... Please wait', True, (255,255,255)), (100,300))
    pygame.display.flip()
    if game:
        PacketConnectionObject.m.stop()
        PacketConnectionObject.m = task.LoopingCall(run_game, (PacketConnectionObject))
        PacketConnectionObject.m.start(1/60)


class PacketConnection(Protocol):
    def __init__(self):
        self.connection=False
        self.m = task.LoopingCall(main, (self))
        self.m.start(1/60)
        self.game_state=GameState()
	    #run_game()
        self.OPP_score = 0
        self.OPP_level = 0
        self.OPP_lines = 0
        self.OPP_alive = True
    def connectionMade(self):
        print("Connection Made")
        self.connection=True
        self.m.stop()
        #main(self.connection)
        self.m = task.LoopingCall(main, (self))
        self.m.start(1/60)
        
        self.StartForwarding()
    def dataReceived(self, data):
        # assume data will always come in packets of opp_score, opp_level, opp_lines, opp_alive
        self.OPP_score = data[0]
        self.OPP_level = data[1]
        self.OPP_lines = data[2]
        self.OPP_alive = data[3]

        self.StartForwarding()

    def StartForwarding(self):
        # Forward my data
        #d = []
        #d[0] = self.game_state.score
        #d[1] = self.game_state.level
        #d[2] = self.game_state.lines
        #d[3] = self.game_state.alive

        self.transport.write(self.game_state.level)
    #if connection != True:
	#	connection = True
	#	return
class PacketConnectionFactory(ClientFactory):
    def __init__(self):
    	self.myconn = PacketConnection()
    def buildProtocol(self, addr):
    	return self.myconn

if __name__=='__main__':
    #connection = False
    #m = task.LoopingCall(main, (connection))
    #m.start(1/60)
    
    reactor.connectTCP("localhost", PORT, PacketConnectionFactory())
    reactor.run()    
