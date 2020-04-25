from kivy.uix.image import Image

class Arrow(Image):
	def __init__(self, direction, pos, style, damage, speed):
		super().__init__()
		self.size = (25,25)
		self.center_x = pos[0]
		self.center_y = pos[1]
		self.allow_stretch = True
		self.keep_ratio = False

		self.direction = direction
		self.damage = damage
		self.speed = speed
		self.style = style

		if direction == -1:
			self.source = 'Data/Arrows/' + str(style) + 'ArrowL.png'
		elif direction == 1:
			self.source = 'Data/Arrows/' + str(style) + 'ArrowR.png'
			if style == 'Necro': self.size = (32,15) 

	def move(self):
		self.pos = (self.pos[0] + self.direction*self.speed[0], self.pos[1] - self.speed[1])

	def attack_enemy(self, enemy, dragon_is_true):
		'''Если хп больше 0, то убирает 1 хп'''
		if enemy.health_points > 0:
			e = enemy.health_points #Сохранение значения хп врага
			if self.damage > 0:
				enemy.health_points -= self.damage #убираем хп врагу
			if int(enemy.health_points) > 0 and enemy.style == 'Enemy': #Если это не дракон и ещё живой
				dictionary = {1: 3, 0.9: 3, 0.8: 2, 0.7: 2, 0.6: 1, 0.5: 1, 0.4: 1, 0.3: 1, 0.2: 1, 0.1: 1, 0.0: 1}
				enemy.source = 'Data/Enemy/Enemy'+str(dictionary[round(enemy.health_points/enemy.max_hp, 1)])+'.gif'
			self.damage -= e #Стрела ослабела на количество хп врага

	def check_position(self, screen, tower):
		'''проверка, не вылетели ли стрелы за поле'''
		if self.y < 0: #если положение стрелы по y < 0
			for arrow in tower.arrows:
				screen.remove_widget(arrow)
			tower.arrows = []