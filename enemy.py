from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader

from random import choice
from random import randrange, randint

class Enemy(Image):
	sound = SoundLoader.load('Data/Sounds/killed_enemy.wav')
	sound.volume = 0.1
	sound.loop = False

	def __init__(self, ai_settings, number):
		super().__init__()
		self.ai_settings = ai_settings
		self.allow_stretch = True
		self.keep_ratio = False
		self.source = 'Data/Enemy/Enemy3.gif'
		self.pos = (80, randrange(0,self.ai_settings.screen_height*0.87))
		self.size = (40,50)
		self.anim_delay = 0.05

		self.health_points = 3
		self.max_hp = self.health_points 
		self.speed = 1
		self.damage = 1
		self.style = 'Enemy'
		self.level = number #Уровень зомби
		#Вычисление статы зомби
		if number <= 10:
			self.speed = 1 + 0.1*number
		else:
			self.speed += 1 
			self.max_hp += number - 10
			self.health_points += number - 10
			self.damage = 1 + int(number/10)#Для расчёта убытка для замка и урона по башням
		self.price = 1 #деньги за зомби
		self.income = 1 #Доход за зомби
		self.hp = Image(source = 'Data/hp.png', size = (15,15), center = (self.right - 40, self.top))
		self.hp_label = Label(text = str(self.health_points), font_size = 16, color = [.6,0,0,1],
		 pos = (self.center_x - 10, self.top), font_name = 'Data/MATURASC.TTF')

	def update_position(self, bow_towers, magic_towers, frozen_enemies, old_traps, traps):
		'''Обновление позиции зомби'''
		if self.check_enemy_freedom(frozen_enemies, old_traps, traps):
			self.random_walk(bow_towers, magic_towers) #свободное блуждание

	def check_enemy_freedom(self, frozen_enemies, old_traps, traps):
		'''Проверяет не пойман ли враг в ловушку'''
		if self in frozen_enemies:
			return False
		if len(traps) > 0: #Если ловушки есть
			collisions_result = [self not in trap.enemies for trap in old_traps] 
			if collisions_result == [True for i in range(len(old_traps))]:#Проверяем нет ли врага среди пойманных
				return True
		else: #Если ловушек нет,
			return True #то сразу возвращает True

	def random_walk(self, bow_towers, magic_towers): #свободное блуждание
		result1 = self.check_towers(bow_towers) #Контактирует ли зомби с башнями лучников
		result2 = self.check_towers(magic_towers) #Контактирует ли зомби с магическими башнями
		x_step = self.generate_x_step(result1, result2)
		y_step = self.generate_y_step(result1, result2)
		self.pos = (self.pos[0] + x_step, self.pos[1] + y_step)

	def generate_x_step(self, result1, result2):
		'''Генерирует шаг по x'''
		s = self.speed
		if ((result1 == False) or (result2 == False)):
			s = 2
			x_direction = -1 #направление
		else:
			x_direction = 1 #Очень низкий шанс идти назад.
		x_distance = choice([s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s*2,s*2])
		x_step = x_distance * x_direction/2

		return x_step

	def generate_y_step(self, result1, result2):
		'''Генерирует шаг по y'''
		s = self.speed
		y_direction = 1
		if (result1 == False) or (result2 == False):
			y_direction = -1
		elif self.y < 0:
			y_direction = 1
		elif self.top > self.ai_settings.screen_height*0.87: #компенсация доски
			y_direction = -1
		else:
			y_direction = choice([-1,1])
		y_distance = s
		y_step = y_distance * y_direction

		return y_step

	def check_towers(self, towers):
		'''Проверяет коллизии с башнями, это определяет поведение зомби'''
		if len(towers) > 0:
			collisions_result = [self.collide_widget(tower) for tower in towers]
			if collisions_result == [False for i in range(len(towers))]:
				return True
			else:
				return False
		else:
			return True

	def check_trap_collision(self, traps, old_traps):
		'''Проверка коллизии врага и ловушки'''
		for trap in traps:
			if int(self.center_x) in range(int(trap.x) + int(trap.width/3), int(trap.right) - int(trap.width/3)) and int(self.y) in range(int(trap .y), int(trap.top)):
				trap.enemies.append(self) #Враг становится захваченным
				trap.source = 'Data/Trap.gif' #Анимация закрытия
				old_traps.append(trap) #Ловушка становится старой
				traps.remove(trap) #Удаляется из списка ловушек
				break

	def initialize_speed(self):
		if self.level <= 10:
			self.speed = 1 + 0.1*self.level
		else:
			self.speed += 1

	def initialize_death(self, screen):
		'''Изменения происходящие в случае смерти'''
		self.source = 'Data/Enemy/EnemyDeath' + str(randint(1,3)) +  '.gif'
		screen.remove_widget(self.hp) #удаление изображения хп врага
		screen.remove_widget(self.hp_label) #удаление метки хп врага
