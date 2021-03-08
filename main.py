import pygame
import neat
import random
import sys

class Time():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.time = 0

	def timer(self): 
		''' Считает прошедшее время '''
		self.clock.tick()
		self.time += self.clock.get_rawtime()

	def check_timer(self,num):
		''' Обнуляет счетчик времени и возвращает истину, если достигло указанного времени '''
		if self.time >= num:
			self.time = 0
			return True
		return False

class Bird():
	def __init__(self,i):
		global win_height
		self.img_main = pygame.image.load('Birds/bird%d.png'%(i+1))
		self.img_jump = pygame.image.load('Birds/jump_bird%d.png'%(i+1))
		self.img_fall = pygame.image.load('Birds/fall_bird%d.png'%(i+1))
		self.img = self.img_main
		self.x = 200
		self.y = win_height//2
		self.width = self.img.get_width()
		self.height = self.img.get_height()
		self.y0 = self.y
		self.t_fall = 0
		self.score = 0
		self.score_columns = 0
		self.is_jump = False
		self.is_alive = True
		self.timer = Time()

	def draw(self,win):
		''' Выводит на экран изображение птицы '''
		win.blit(self.img,(self.x,self.y,self.width,self.height))

	def move(self):
		''' Смещает птицу по оси y '''
		self.t_fall += 1
		self.y = self.y0 - 22*self.t_fall + self.t_fall**2

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
					self.is_alive = False
			if self.y < 0 or self.y + self.height > win_height-ground_height:
				self.is_alive = False

	def get_data(self,columns):
		''' Возвращает расстояние до ближайшей колонны, высоту от верхней колонны до птицы, высоту от нижней колонны до птицы '''
		for column in columns:
			if column.x+column.width > self.x:
				return [
					column.x - self.x,
					self.y - column.y1,
					column.y2 - (self.y + self.height)
					]

	def get_score(self):
		''' Увеличивает очки живой птицы за пройденное расстояние '''
		self.score += 0.001

	def get_score_columns(self,columns):
		''' Считает пройденные колонны '''
		for column in columns:
			if self.x == column.x+column.width:
				self.score_columns += 1

	def jump(self,i,nets,birds,columns):
		''' Отвечает за прыжок птицы '''
		n = nets[i].activate(self.get_data(columns))
		a = n.index(max(n[:2]))
		if a == 0:
			self.t_fall = 0
			self.y0 = self.y


class Column():
	def __init__(self):
		global win_width,win_height,ground_height
		self.width = 120
		self.x = win_width
		self.space_len = 240
		self.y1 = random.randint(10,win_height-self.space_len-ground_height-10)
		self.y2 = self.y1+self.space_len
		self.len1 = self.y1
		self.len2 = win_height-self.y2-ground_height
		

	def draw(self,win):
		''' Выводит на экран изображение колонн '''
		pygame.draw.rect(win,[20,180,5],(self.x,0,self.width,self.len1))
		pygame.draw.rect(win,[20,180,5],(self.x,self.y2,self.width,self.len2))
		pygame.draw.rect(win,[30,190,7],(self.x,0,self.width//3,self.len1))
		pygame.draw.rect(win,[30,190,7],(self.x,self.y2,self.width//3,self.len2))				
		pygame.draw.rect(win,[60,210,20],(self.x+self.width//12,0,self.width//24,self.len1))
		pygame.draw.rect(win,[60,210,20],(self.x+self.width//12,self.y2,self.width//24,self.len2))			
		pygame.draw.rect(win,[15,150,2],(self.x+self.width-self.width//4-self.width//10,0,self.width//14,self.len1))
		pygame.draw.rect(win,[15,150,2],(self.x+self.width-self.width//4-self.width//10,self.y2,self.width//14,self.len2))	
		pygame.draw.rect(win,[15,150,2],(self.x+self.width-self.width//4,0,self.width//4,self.len1))
		pygame.draw.rect(win,[15,150,2],(self.x+self.width-self.width//4,self.y2,self.width//4,self.len2))
		pygame.draw.rect(win,[0,0,0],(self.x,0,self.width,self.len1),5)
		pygame.draw.rect(win,[0,0,0],(self.x,self.y2,self.width,self.len2),5)
		

def check_need_column(columns):
	''' Проверяет, пора ли добавить новую колонну. Если да, добавляет её '''
	global win_width
	if win_width-columns[-1].x >= 500: columns.append(Column())
	if columns[0].x+columns[0].width<0: columns.pop(0)

def draw_ground(win):
	''' Выводит на экран изображение земли '''
	pygame.draw.rect(win,[150,70,5],(0,win_height-ground_height,win_width,ground_height))	
	pygame.draw.rect(win,[190,100,3],(0,win_height-ground_height,win_width,ground_height//3))	
	pygame.draw.rect(win,[0,0,0],(0,win_height-ground_height,win_width,ground_height),4)

def print_text(win,text,width,height,size,font = 'Comic Sans MS',color = (0,0,0),center = True):
	''' Выводит на экран текст '''
	font = pygame.font.SysFont(font, size)
	text = font.render(text, True, color)
	text_rect = text.get_rect()
	if center == True: text_rect.center = (width, height)
	else: text_rect.midleft = (width, height)
	win.blit(text, text_rect)


def start(genomes,config):
	global best_score
	global generation
	current_best_score = 0
	generation += 1
	nets = []
	birds = []
	columns = [Column()]	

	for i, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)	
		g.fitness = 0
		nets.append(net)
		birds.append(Bird(i%8))

	run = True
	alives = len(birds)
	while alives > 0:
		''' Вывод на экран изображений '''
		win.fill((9,91,174))
		win.blit(bcground,(0,win_height-win_height//2))
		draw_ground(win)

		for column in columns:
			column.draw(win)
		
		for bird in birds:
			if bird.is_alive: bird.draw(win)

		''' Вывод на экран текста '''
		print_text(win,'Generation: %d'%(generation),10,20,30,center = False)
		print_text(win,'Best score: %d'%(best_score),10,60,30,center = False)
		print_text(win,'%d'%(current_best_score),win_width//2+2,60+2,60,color = (0,0,0))
		print_text(win,'%d'%(current_best_score),win_width//2-2,60-2,60,color = (0,0,0))
		print_text(win,'%d'%(current_best_score),win_width//2,60,60,color = (255,250,0))		

		''' Таймеры '''
		timer_column.timer()
		for bird in birds:
			bird.timer.timer()

		''' Смещение объектов '''
		if timer_column.check_timer(3):
			for column in columns:
				column.x -= 1

		alives = 0
		for i,bird in enumerate(birds):
			if bird.is_alive:
				alives += 1		
				if bird.timer.check_timer(24):
					bird.check_collision(columns)
					bird.move()
					bird.choice_image()
				bird.jump(i,nets,birds,columns)
				bird.get_score()
				bird.get_score_columns(columns)
				genomes[i][1].fitness += bird.score

		check_need_column(columns)	
		current_best_score = max(bird.score_columns for bird in birds)
		best_score = max(current_best_score,best_score)

		''' Обработка событий '''
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

		pygame.display.update()	

pygame.init()

generation = 0
best_score = 0

win_width = 800
win_height = 800
ground_height = 30

pygame.display.set_caption('Flappy Bird Neat')
bcground = pygame.image.load('bcground.png')
win = pygame.display.set_mode((win_width,win_height))

timer_column = Time()

config_path = './config-feedforward.txt'
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

p.run(start, 1000)