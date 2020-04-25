from kivy.uix.image import Image
from kivy.graphics import Rectangle

class Trap(Image):
	enemies = [] #зомби, отвлеченные этим чучелом
	def __init__(self, pos):
		super().__init__()
		self.source = 'Data/Trap.png'
		self.center = pos
		self.size = (45,30)
		self.anim_delay = 0.05
		self.anim_loop = 1

		self.price = 5 #Цена
		self.resistance = 5 #Сопротивление
		self.style = 'Trap' #Стиль
		self.consumption = 0 #Потребление