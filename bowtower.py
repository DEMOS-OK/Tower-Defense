from kivy.uix.image import Image
from arrow import Arrow

class BowTower(Image):
	def __init__(self, pos):
		'''Инициализация параметров изображения для башни с луком'''
		super().__init__()
		self.source = 'Data/BowTower.png'
		self.size = (50, 75)
		self.center = pos

		self.arrows = [] #список со стрелами
		self.arrows_pos = self.center
		self.style = 'Classic'
		self.class_name = 'Bow'

		self.price = 20 #цена башни
		self.consumption = 10 #потребление башни

		self.spent_money = 0 #деньги, которые ушли на улучшение башни
		self.saved_resistance = 0
		self.building_time = 0 #сколько времени потрачено строительство
		self.stats = {'Resistance': 5, 'Speed': 2, 'Damage': 1}
		self.prices = {'Damage': int(self.price), 'Resistance': int(self.price*2), 'Speed': int(self.price)}

	def create_arrows(self):
		self.arrows.append(Arrow(direction = -1, pos = self.arrows_pos, style = self.style, damage = self.stats['Damage'], speed = (self.stats['Speed'], self.stats['Speed'])))
		self.arrows.append(Arrow(direction = 1, pos = self.arrows_pos, style = self.style, damage = self.stats['Damage'], speed = (self.stats['Speed'], self.stats['Speed'])))

	def move_arrows(self):
		for arrow in self.arrows:
			arrow.move()

