from random import *
import pygame
from pygame.locals import *

class Menu:
	"""
	Class to draw the menu and keep it updated
	
	Gives aboutrmation to the main file for which
	self.surface to display and which game to play.
	"""
	
	def __init__(self, surface):
		self.surface = surface

		self.singlePlayer=1
		self.matchPlayer=0
		self.about=0
		self.gameStart=0
		self.aboutDone=0
	
	def draw_menu(self):

		center = (self.surface.get_width()/2, self.surface.get_height()/2)

		background_color=(0,0,0)
		font_color = (255,255,255)
		
		self.surface.fill(background_color)

		tetris_font = pygame.font.Font("freesansbold.ttf",64)
		tetris_font.set_bold(1)
		
		label_1 = tetris_font.render("TETRIS",1, font_color)
		label_1_rect = label_1.get_rect()
		label_1_rect.center = (center[0],center[1]-60)
		
		tetris_font = pygame.font.SysFont("monospace", 10)
		
		label_5 = tetris_font.render("By earayu",1, font_color)
		label_5_rect = label_5.get_rect()
		label_5_rect.center = (center[0]+100,center[1]-30)
		
		self.surface.blit(label_1, label_1_rect)
		self.surface.blit(label_5, label_5_rect)
	
	def draw_about(self):
		background_color=(255,255,255)
		font_color = (0,0,0)

		pygame.draw.rect(self.surface, background_color, (50,50,self.width-100,self.height-100),0)
		
		tetris_font = pygame.font.Font("freesansbold.ttf",32)
		tetris_font.set_bold(1)
		
		label_1 = tetris_font.render("about",1, font_color)
		label_1_rect = label_1.get_rect()
		label_1_rect.center = (150, 100)
		
		
		tetris_font = pygame.font.SysFont("monospace", 12)
		
		label_2 = tetris_font.render("Move shape left, right",1, font_color)
		label_2_rect = label_2.get_rect()
		label_2_rect.center = (150, 150)
		
		label_7 = tetris_font.render("and down using arrow keys.",1, font_color)
		label_7_rect = label_7.get_rect()
		label_7_rect.center = (150, 160)

		label_3 = tetris_font.render("Rotate shape using",1, font_color)
		label_3_rect = label_3.get_rect()
		label_3_rect.center = (150, 200)
		
		label_8 = tetris_font.render("the UP arrow key",1, font_color)
		label_8_rect = label_8.get_rect()
		label_8_rect.center = (150, 210)
		
		label_4 = tetris_font.render("Drop shape using space bar",1, font_color)
		label_4_rect = label_4.get_rect()
		label_4_rect.center = (150, 260)
		
		tetris_font = pygame.font.SysFont("monospace", 10)
		label_5 = tetris_font.render("Score=(number of lines^2)*100",1, font_color)
		label_5_rect = label_5.get_rect()
		label_5_rect.center = (150, 300)
		
		label_6 = tetris_font.render("Press any button to continue",1, font_color)
		label_6_rect = label_6.get_rect()
		label_6_rect.center = (150, 350)
		
		self.surface.blit(label_1, label_1_rect)
		self.surface.blit(label_2, label_2_rect)
		self.surface.blit(label_3, label_3_rect)
		self.surface.blit(label_4, label_4_rect)
		self.surface.blit(label_5, label_5_rect)
		self.surface.blit(label_6, label_6_rect)
		self.surface.blit(label_7, label_7_rect)
		self.surface.blit(label_8, label_8_rect)
		
	# updates the menu to display the current users selection
	def update_menu(self):
		center = (self.surface.get_width() / 2, self.surface.get_height() / 2)

		tetris_font = pygame.font.SysFont("SimHei",16)
		tetris_font.set_bold(0)
		
		singlePlayerBG=(255*self.singlePlayer,255*self.singlePlayer,255*self.singlePlayer)
		matchPlayerBG=(255*self.matchPlayer,255*self.matchPlayer,255*self.matchPlayer)
		aboutBG=(255*self.about,255*self.about,255*self.about)

		singlePlayerFont=(255*(1-self.singlePlayer),255*(1-self.singlePlayer),255*(1-self.singlePlayer))
		matchPlayerFont=(255*(1-self.matchPlayer),255*(1-self.matchPlayer),255*(1-self.matchPlayer))
		aboutFont=(255 * (1 - self.about), 255 * (1 - self.about), 255 * (1 - self.about))

		pygame.draw.rect(self.surface, singlePlayerBG, (center[0]-60,center[1]-10+30,120,20),0)
		label_2 = tetris_font.render("双人游戏",1, singlePlayerFont)
		label_2_rect = label_2.get_rect()
		label_2_rect.center = (center[0],center[1]+30)
		
		pygame.draw.rect(self.surface, matchPlayerBG, (center[0]-60,center[1]-10+55,120,20),0)
		label_3 = tetris_font.render("匹配游戏",1, matchPlayerFont)
		label_3_rect = label_3.get_rect()
		label_3_rect.center = (center[0],center[1]+55)
		
		pygame.draw.rect(self.surface, aboutBG, (center[0]-60,center[1]-10+80,120,20),0)
		label_4 = tetris_font.render("关于作者",1, aboutFont)
		label_4_rect = label_4.get_rect()
		label_4_rect.center = (center[0],center[1]+80)
		
		self.surface.blit(label_2, label_2_rect)
		self.surface.blit(label_3, label_3_rect)
		self.surface.blit(label_4, label_4_rect)

		pygame.display.update()

	# 显示正在匹配的画面
	def matching_screen(self):
		self.surface.fill((0,0,0))

		center = (self.surface.get_width() / 2, self.surface.get_height() / 2)

		font_color = (255, 255, 255)

		tetris_font = pygame.font.Font("freesansbold.ttf", 64)
		tetris_font.set_bold(1)

		label_1 = tetris_font.render("Matching...", 1, font_color)
		label_1_rect = label_1.get_rect()
		label_1_rect.center = (center[0], center[1] - 60)

		self.surface.blit(label_1, label_1_rect)

		pygame.display.update()



	def process_key_event(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				return "terminate"
			if event.type == KEYDOWN:
				if event.key == K_DOWN:
					self.move_cursor(-1)
				elif event.key == K_UP:
					self.move_cursor(1)
				elif event.key in [K_RETURN, K_KP_ENTER]:
					if self.matchPlayer == 1:
						return "match"
					elif self.singlePlayer == 1:
						return "single"
					elif self.about == 1:
						return "about"


	def move_cursor(self,direction):
		if self.matchPlayer:
			if direction == 1:
				self.matchPlayer = 0
				self.singlePlayer = 1
			elif direction == -1:
				self.matchPlayer=0
				self.about=1

		elif self.singlePlayer:
			if direction == 1:
				self.singlePlayer = 0
				self.about = 1
			elif direction == -1:
				self.matchPlayer = 1
				self.singlePlayer = 0

		elif self.about:
			if direction == 1:
				self.matchPlayer = 1
				self.about = 0

			elif direction == -1:
				self.singlePlayer = 1
				self.about = 0

	# function to reset game initialization variables
	def reset_game(self):
		self.matchPlayer = 0
		self.singlePlayer = 1
		self.about = 0
		self.gameStart = 0
		self.aboutDone=0

