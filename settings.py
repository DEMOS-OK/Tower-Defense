class Settings():
	def __init__(self, window_size):
		'''Инициализация игровых настроек'''
		self.screen_width = window_size[0]
		self.screen_height = window_size[1]

		self.castle_income = 50 #сколько дохода заберёт зомби, если дойдёт до замка
		self.enemy_quantities = {'Enemy': 10, 'Magician': 0, 'Giant': 0, 'EnemyMax': 30, 'MagicianMax': 15, 'GiantMax': 5}
		self.enemy_spawn = {'Enemy': 0, 'Magician': 20, 'Giant': 40} #С какого нашествия начинается их появление.

		self.ww_stats = {'WWDamage': 3, 'WWTime': 600} #Максимальные статы варвика, передаётся в класс, выводится в метках

		self.magic_factors = {'Kill': 1.4, 'Cold': 1.6, 'Slow': 1.4, 'Immortal': 1.5} #множители для цены
		self.magic_prices = {'Kill': 1000, 'Cold': 250, 'Slow': 100, 'Immortal': 1500, 'Warwick': 200} #Цены на магию