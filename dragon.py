from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader

from arrow import Arrow
from random import choice
from random import randrange

class Dragon(Image):
	sound = SoundLoader.load('Data/Sounds/flying_dragon.wav')
	sound.volume = 0.2
	sound.loop = True
	
	def __init__(self, ai_settings, invasion_number):
		super().__init__()
		self.ai_settings = ai_settings
		self.level = invasion_number/10 #Уровень
		self.damage = self.level*5
		self.health_points = self.level*self.level*100
		self.speed = 1
		self.arrow_speed = 3
		self.style = 'Dragon'
		self.price = 200 #деньги, которые даются за убийство дракона
		self.income = 200 + int(invasion_number/10)*50 #доход, который даётся за убийство дракона
		self.hp = Image(source = 'Data/hp.png', size = (45,45), pos = (ai_settings.screen_width/2, 0))
		self.hp_label = Label(text = str(self.health_points), font_size = 42,
		 color = [.6,0,0,1], center = (self.hp.pos[0] - 10*len(str(self.health_points)), self.hp.pos[1] + 22), font_name = 'Data/MATURASC.TTF')

		self.fireballs = []

		self.source = 'Data/Dragon/Dragon.gif' #по умолчанию враг смотрит вправо
		self.pos = (80, ai_settings.screen_height/2)
		self.size = (100, 90)
		self.anim_delay = 0.05

	def random_walk(self): #свободное блуждание
		x_step = self.generate_x_step()
		y_step = self.generate_y_step()
		self.pos = (self.pos[0] + x_step, self.pos[1] + y_step)

	def generate_x_step(self):
		'''Генерирует шаг по x'''
		s = self.speed
		x_direction = choice([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1]) #Очень низкий шанс идти назад.
		x_distance = choice([s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s*2,s*2])
		x_step = x_distance * x_direction/2

		return x_step

	def generate_y_step(self):
		'''Генерирует шаг по y'''
		y_direction = 1
		if self.y < 0:
			y_direction = choice([1,1])
		elif self.top > self.ai_settings.screen_width*0.87: #компенсация доски
			y_direction = choice([-1,-1])
		else:
			y_direction = choice([-1,1])
		y_distance = choice([1,1,1,1,2,2,2,3,3,3,4,5])
		y_step = y_distance * y_direction

		return y_step

	def fireball(self, screen):
		'''Создание и обновление файерболла'''
		if self.fireballs == []:
			self.attack(screen)
		else:
			self.check_fireball_position(screen)

	def attack(self, screen):
		self.fireballs.append(Arrow(direction = 1, pos = (self.right, self.center_y - 30), style = 'Fire', damage = self.damage, speed = (self.arrow_speed, self.arrow_speed)))
		screen.add_widget(self.fireballs[-1])

	def check_fireball_position(self, screen):
		'''Отслеживание и обновление позиции файерболла дракона'''
		if self.fireballs[-1].y > 0:
			self.fireballs[-1].move()
			self.check_fireball_tower_collisions(screen, screen.bow_towers)
			self.check_fireball_tower_collisions(screen, screen.magic_towers)
		else:
			screen.remove_widget(self.fireballs[-1])
			self.fireballs = []

	def check_position(self, game, right_edge, castle):
		'''Проверка позиции дракона'''
		if self.right > right_edge: #Вылет за правый край
			game.death_enemy(self, 'Right')
		elif self.collide_widget(castle): #Дошёл до замка
			game.death_enemy(self, 'Castle')

	def check_fireball_tower_collisions(self, screen, towers):
		if self.fireballs != []:
			for i in range(len(towers)):
				if towers[i].collide_widget(self.fireballs[-1]) and towers[i].stats['Resistance'] <= self.damage:
					screen.remove_arrows(i, towers) #Удаление стрел башне, по которой попал файерболл
					screen.remove_widget(towers[i]) #Удаление башни
					towers.remove(towers[i])
					screen.remove_widget(self.fireballs[-1])
					self.fireballs = []
					break

	def initialize_death(self, screen):
		'''Изменения, происходящие в случае смерти'''
		self.source = 'Data/Dragon/DragonDeath.gif' #Анимация смерти
		self.sound.stop()
		screen.dragon_is_true = False
		if len(self.fireballs) > 0: #Что удалять, если файерболлов нет. Борьба с исключениями
			screen.remove_widget(self.fireballs[-1]) #Удаление файерболлов с экрана
			self.fireballs = []
		screen.remove_widget(self.hp) #удаление изображения хп врага
		screen.remove_widget(self.hp_label) #удаление метки хп врага