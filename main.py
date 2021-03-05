import pygame
import neat
import math
import random
import sys
from PIL import Image

class Time():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.time = 0.1

	def timer(self):
		''' Считает прошедшее время '''
		self.clock.tick()
		self.time += self.clock.get_rawtime()

	def check_timer(self,num):
		''' Обнуляет счетчик времени и возвращает истину, если достигло указанного времени '''
		if self.time >= num:
			self.time = 0.1
			return True
		return False

class Bird():
	def __init__(self,i):
		global win_height
		self.index = i
		self.img_main = pygame.image.load('bird.png')
		self.img_jump = pygame.image.load('jump_bird.png')
		self.img_fall = pygame.image.load('fall_bird.png')
		self.img = self.img_main
		self.x = 200
		self.y = win_height//2
		self.pos = [self.x,self.y]
		self.width = self.img.get_width()
		self.height = self.img.get_height()
		self.radius = self.width//3
		self.center = [self.x+self.width//2,self.y+self.height//2]
		self.y0 = self.y
		self.t_fall = 0
		self.is_alive = True

	def rotate_img(self):
		''' Поворачивает картинку на определенный угол '''
		self.rot_img = pygame.transform.rotate(self.img,self.angle)

	def draw(self,win):
		''' Выводит на экран изображение птицы '''
		win.blit(self.img,(self.x,self.y,self.width,self.height))

	def move(self):
		''' Смещает птицу по оси y '''
		self.t_fall += 1
		self.y = self.y0 - 22*self.t_fall + self.t_fall**2

	def jump(self):
		''' Отвечает за прыжок птицы '''
		self.t_fall = 0
		self.y0 = self.y

	def choice_image(self):
		''' Выбирает картинку птицы в зависимости от направления движения. Прыгающая, падающая или летящая прямо '''
		s = - 22*self.t_fall + self.t_fall**2
		if -50 <= s <= 50:
			self.img = self.img_main
		elif s < -50:
			self.img = self.img_jump
		elif s > 50:
			self.img = self.img_fall

	def check_collision(self,columns):
		''' Проверяет коллизию '''
		for column in columns:
			if column.x+column.width > self.x and column.x < self.x + self.width:
				if self.y < column.y1 or self.y+self.height > column.y2:
					# self.is_alive = False
					pygame.draw.circle(win,(210,0,0),[self.x+self.width//2,self.y+self.height//2],17)
			if self.y < 0 or self.y + self.height > win_height:
				# self.is_alive = False
				pygame.draw.circle(win,(210,0,0),[self.x+self.width//2,self.y+self.height//2],17)


class Column():
	def __init__(self):
		global win_width,win_height
		self.width = 120
		self.x = win_width
		self.space_len = 240
		self.y1 = random.randint(10,win_height-self.space_len-10)
		self.y2 = self.y1+self.space_len
		self.len1 = self.y1
		self.len2 = win_height-self.y2
		

	def draw(self,win):
		''' Выводит на экран изображение колонн '''
		pygame.draw.rect(win,[20,180,5],(self.x,0,self.width,self.len1))
		pygame.draw.rect(win,[20,180,5],(self.x,self.y2,self.width,self.len2))
		pygame.draw.rect(win,[0,0,0],(self.x,0,self.width,self.len1),4)
		pygame.draw.rect(win,[0,0,0],(self.x,self.y2,self.width,self.len2),4)
		
def check_need_column(columns):
	''' Проверяет, пора ли добавить новую колонну. Если да, добавляет её '''
	global win_width
	if win_width-columns[-1].x >= 500:
		columns.append(Column())
	if columns[0].x+columns[0].width<0:
		columns.pop(0)
	return columns

win_width = 800
win_height = 800
pygame.init()
win = pygame.display.set_mode((win_width,win_height))
pygame.display.set_caption('Flappy Bird Neat')
timer_column = Time()
timer_bird = Time()

def start():
	birds = [Bird(i) for i in range(1)]
	columns = [Column()]

	run = True
	jump = False
	while len(birds) > 0:
		''' Вывод на экран изображений '''
		win.fill((9,91,174))

		for column in columns:
			column.draw(win)
		
		for bird in birds:
			if bird.is_alive:
				bird.draw(win)

		''' Таймеры '''
		timer_column.timer()
		timer_bird.timer()

		''' Смещение объектов '''
		if timer_column.check_timer(5):
			for column in columns:
				column.x -= 1

		for bird in birds:
			if bird.is_alive:
				bird.check_collision(columns)
				if timer_bird.check_timer(30):
					bird.move()
					bird.choice_image()
				if jump==True:
					bird.jump()

		check_need_column(columns)		

		''' Обработка событий '''
		jump = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					jump = True 

		pygame.display.update()	
		
start()