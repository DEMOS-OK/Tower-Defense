from kivy.uix.image import Image

class Castle(Image):
	def __init__(self, ai_settings):
		super().__init__()
		self.source = 'Data/Castle.png'
		self.size = (110,275)
		self.right = ai_settings.screen_width
		self.center_y = ai_settings.screen_height/2