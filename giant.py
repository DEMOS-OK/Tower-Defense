from kivy.uix.image import Image
from enemy import Enemy
from random import randrange

class Giant(Enemy):
	'''Появляется на 40-м нашествии'''
	def __init__(self, ai_settings, number):
		super().__init__(ai_settings, number)
		self.ai_settings = ai_settings
		self.source = 'Data/Enemy/GiantEnemy.gif'
		self.pos = (120, randrange(0,self.ai_settings.screen_height*0.87))
		self.size = (70, 100)
		self.anim_delay = 0.05

		self.health_points = 200
		self.speed = 2
		self.style = 'Giant'
		#Вычисление статы зомби
		if number < 70:
			for i in range(int((number - 40)/10)):
				self.health_points *= 2
		else:
			for i in range(int((number - 40)/10)):
				self.health_points *= 1.1
		self.max_hp = self.health_points #нужно для определения количества хп в процентах
		self.level = number #Уровень зомби
		self.damage = 5+(number-40 + 1) #Для расчёта убытка для замка
		self.price = 100 #деньги за зомби
		self.income = 50

	def initialize_death(self, screen):
		'''Изменения, происходящие в случае смерти'''
		self.size = (100,100)
		self.source = 'Data/Enemy/GiantDeath.gif'
		screen.remove_widget(self.hp) #удаление изображения хп врага
		screen.remove_widget(self.hp_label) #удаление метки хп врага
