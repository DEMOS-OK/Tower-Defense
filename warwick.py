from kivy.uix.image import Image
from kivy.uix.label import Label
from random import choice

class Warwick(Image):
	def __init__(self, pos, ww_stats):
		super().__init__()
		self.source = 'Data/Warwick/Warwick.gif'
		self.center = pos
		self.size = (80,80)
		self.anim_delay = 0.1

		self.walking = True #Ходьба
		self.attack = False #Атака
		self.class_name = 'Warwick'
		self.killing_enemy = None #Зомби, которого сейчас убивает Варвик
		self.speed = 1
		self.stats = {'WWDamage': ww_stats['WWDamage'], 'WWTime': ww_stats['WWTime']}
		self.begin_time = 0 #Когда начата анимация атаки
		self.max_health_time = ww_stats['WWTime']
		self.stats['WWTime'] = self.max_health_time

	def update(self, enemies, frozen_enemies, screen, bow_towers, magic_towers):
		'''Обновление позиции'''
		self.check_enemies(enemies, frozen_enemies)
		result1 = self.check_towers(bow_towers)
		result2 = self.check_towers(magic_towers)
		if self.stats['WWTime'] > 0:
			if self.walking:
				self.move(result1, result2)
			elif self.attack and (self.begin_time - self.stats['WWTime']) == 30:
				self.attack_move(screen)
			self.stats['WWTime'] -= 1
		else:
			self.anim_loop = 1
			self.size = (133,80)
			self.source = 'Data/Warwick/WarwickDeath.gif'
			screen.bodies.append(self)
			return 'Killed'

	def move(self, result1, result2):
		'''Движение'''
		y_move = choice([1,-1])
		x_move = 0
		if result1 == False or result2 == False:
			y_move = -1
			x_move = 2
		self.pos = (self.x - 1 + x_move, self.y + y_move)

	def attack_move(self, screen):
		'''Атака'''
		self.killing_enemy.health_points -= self.stats['WWDamage']
		self.begin_time = self.stats['WWTime']
		if self.killing_enemy.health_points <= 0:
			self.walking = True
			self.attack = False
			self.anim_loop = 0
			self.anim_delay = 0.1
			self.source = 'Data/Warwick/Warwick.gif'
			screen.death_enemy(self.killing_enemy, 'Kill')
			self.killing_enemy = None

	def check_enemies(self, enemies, frozen_enemies):
		'''Проверяет позицию врагов по отношению к Варвику'''
		for enemy in enemies:
			if set(range(int(enemy.y), int(enemy.top))) & set(range(int(self.y), int(self.top))) and int(self.x - 100) in range(int(enemy.x), int(enemy.right)) and enemy not in frozen_enemies:
				self.ready_mode()
			if self.collide_widget(enemy) and self.attack == False and self.killing_enemy == None:
				self.attack_mode(enemy)
				break

	def ready_mode(self):
		'''Режим ожидания зомби'''
		self.size = (120,80)
		self.source = 'Data/Warwick/WarwickWOW2.gif'
		self.walking = False

	def attack_mode(self, enemy):
		'''Режим атаки'''
		self.walking = False
		self.attack = True
		self.begin_time = self.stats['WWTime']
		self.anim_loop = 0
		self.anim_delay = 0.05
		self.size = (133,80)
		self.source = 'Data/Warwick/WarwickAttack.gif'
		self.killing_enemy = enemy

	def check_towers(self, towers):
		'''Проверяет коллизии с башнями, это определяет поведение варвика'''
		if len(towers) > 0:
			collisions_result = [self.collide_widget(tower) for tower in towers]
			if collisions_result == [False for i in range(len(towers))]:
				return True
			else:
				return False
		else:
			return True


