from bowtower import BowTower
from arrow import Arrow

class MagicTower(BowTower):
	def __init__(self, pos):
		'''Инициализация параметров изображения для магической башни'''
		super().__init__(pos)
		self.source = 'Data/MagicTower.png'

		self.style = 'Magic'
		self.class_name = 'Magic'
		self.arrows_pos = (self.center_x, self.top)

		self.price = 100 #цена башни
		self.consumption = 30 #потребление башни
		self.stats = {'Resistance': 10, 'Speed': 2, 'Damage': 3}
		self.prices = {'Damage': int(self.price), 'Resistance': int(self.price/10), 'Speed': int(self.price*2)}

