from enemy import Enemy
from random import randrange
from arrow import Arrow

class Magician(Enemy):
	def __init__(self, ai_settings, number):
		super().__init__(ai_settings, number)
		self.ai_settings = ai_settings
		self.source = 'Data/Enemy/MagicianEnemy.gif' #по умолчанию враг смотрит вправо
		self.pos = (80, randrange(0,self.ai_settings.screen_height*0.87))
		self.size = (60, 60)
		self.anim_delay = 0.1

		self.health_points = 10
		self.style = 'Magician'
		self.speed = 1 #скорость мага
		self.magic_speed = 2 #скорость магии
		self.damage = 3 + int(number/10) #урон по замку (20*3 = -60 дохода)
		self.price = 10
		self.income = 5
		self.magic_damage = 1 #урон по башне
		self.spells = []
		self.time = 0

	def attack(self, screen, bow_towers, magic_towers, sound, bodies):
		'''Обновление файерболла'''
		if self.time == 0:
			self.spells.append(Arrow(direction = 1, pos = (self.right, self.center_y), style = 'Necro', damage = self.magic_damage, speed = (self.magic_speed, 0)))
			screen.add_widget(self.spells[0])
			self.time += 1
			sound.play()
		else:
			if self.time <= 180:
				self.time += 1
				if len(self.spells) != 0:
					self.spells[0].move()
					self.check_collisions(bow_towers, screen)
					self.check_collisions(magic_towers, screen)
			else:
				self.time = 0
				if len(self.spells) != 0:
					self.spells[-1].anim_loop = 1
					self.spells[-1].anim_delay = 0.05
					self.spells[-1].source = 'Data/Arrows/NecroArrow.gif'
					bodies.append(self.spells[-1])
					self.spells = []

	def check_collisions(self, towers, screen):
		if len(self.spells) > 0:
			for tower in towers:
				if self.spells[0].collide_widget(tower):
					tower.stats['Resistance'] -= 1
					screen.remove_widget(self.spells[0])
					self.spells = []
					break

	def initialize_death(self, screen):
		'''Изменения, происходящие в случае смерти'''
		self.size = (90,60)
		self.source = 'Data/Enemy/MagicianDeath.gif'
		if len(self.spells) != 0:
			screen.remove_widget(self.spells[-1])
		screen.remove_widget(self.hp) #удаление изображения хп врага
		screen.remove_widget(self.hp_label) #удаление метки хп врага