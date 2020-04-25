from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.config import Config
Config.set('graphics', 'resizable', '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set("graphics", "show_cursor", 0)
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from random import randint

from settings import Settings
from bowtower import BowTower
from magictower import MagicTower
from player import Player
from enemy import Enemy
from magician import Magician
from giant import Giant
from dragon import Dragon
from castle import Castle
from trap import Trap
from warwick import Warwick

Window.size = (1000, 600)
Window.set_icon('Data/BowTower.ico')

background_music = SoundLoader.load('Data/Sounds/background_music.wav')
background_music.volume = 0.5
background_music.loop = True
background_music.play()

building_sound = SoundLoader.load('Data/Sounds/building_sound.wav')
building_sound.volume = 0.1
building_sound.loop = False

magic_sound = SoundLoader.load('Data/Sounds/magic_sound.wav')
magic_sound.volume = 0.1
magic_sound.loop = False

class ImageButton(Image): #Это кнопки строительства
	def __init__(self, class_name, center_x = Window.width*2/3, size = (60,60), source = '', center_y = 0):
		'''Инициализация параметров'''
		super().__init__()
		self.source = source
		self.size = size
		self.center_x = center_x
		self.center_y = center_y

		self.class_name = class_name
		self.mode = 0 #режим, когда равен 1, можно построить башню

class Game(Widget):
	def __init__(self):
		super().__init__()
		self.player = Player() #игрок и его статы
		self.ai_settings = Settings(Window.size) #настройки
		self.time = 1800 #таймер обратного отсчёта
		self.invasion_number = 1 #Номер нашествия
		self.bow_towers = [] #список со всеми башнями лучников
		self.magic_towers = [] #список со всеми магическими башнями
		self.building_tower = None #Башня, которая сейчас строится
		self.c_tower = None #Башня, которую хотят скопировать
		self.immortal_towers = [] #неуязвимые башни
		self.enemies = [] #список с врагами 
		self.enemy_types = {'Enemy': Enemy, 'Magician': Magician, 'Giant': Giant}
		self.frozen_enemies = [] #замороженные враги
		self.slowed_enemies = [] #замедленные враги
		self.bodies = [] #трупы
		self.traps = [] #ловушки
		self.old_traps = [] #ловушки, которые поймали кого-то
		self.money_was_getted = False #Отвечает за начисление денег при убийстве всех врагов
		self.improvement_menu = False #Меню для улучшения башни
		self.dragon_is_true = False #Наличие дракона в данный момент
		self.warwick_is_true = False #Наличие варвика в данный момрени*()
		self.builders = {'BowTower': None, 'MagicTower': None, 'Trap': None} #билдеры = Классы, отвечающие за строительство. 1-й клик включает билдер, а далее клик по экрану что-то строит
		self.buildings = {'BowTower': BowTower, 'MagicTower': MagicTower, 'Trap': Trap}
		self.elements = {'Remover': None, 'Updater': None, 'Copy': None} #элементы = Классы, работ  ающие с построенным башнями. 1-й клик включает элемент, а второй клик должен быть по башне.
		self.magic_menu = False #Наличие магического меню на экране
		self.magic_buttons = {'Kill': None, 'Cold': None, 'Slow': None, 'Immortal': None, 'Warwick': None} #Кнопки в меню с магией
		self.magic_labels = {'Kill': False, 'Cold': False, 'Slow': False, 'Immortal': False, 'Warwick': False} #Словарь для меток
		self.magic_spells = {'Kill': self.kill_all_enemies, 'Cold': self.froze_all_enemies, 'Slow': self.slow_all_enemies, 'Immortal': self.immortal_for_towers}

#ДОБАВЛЕНИЕ ИГРОВЫХ ЭЛЕМЕНТОВ НА ЭКРАН
	def add_buttons(self):
		'''Создаёт различные игровые кнопки'''
		for key in self.builders:
			self.builders[key] = ImageButton(class_name = key, source = 'Data/Buttons/Shop'+key+'.png') #кнопка строительства bt
			self.add_widget(self.builders[key]) #добавление кнопок на экран
		for key in self.elements:
			self.elements[key] = ImageButton(class_name = key, source = 'Data/Buttons/'+key+'.png')
			self.add_widget(self.elements[key])
		self.magic = ImageButton(class_name = 'Magic', source = 'Data/Buttons/Magic.png')
		self.add_widget(self.magic)
		self.next = ImageButton(class_name = 'Next', source = 'Data/Buttons/Next.png', size = (40,40), center_x = 120, center_y = 50)
		self.add_widget(self.next)

	def draw_game(self):
		'''Рисует основные игровые элементы'''
		self.background = Image(size = Window.size, pos = (0,0), source = 'Data/Background.png', allow_stretch = True, keep_ratio = False)
		self.add_widget(self.background) #Фон
		self.board = Image(size = (Window.size[0], Window.size[1]/7.5), pos = (0,Window.size[1]- Window.size[1]/7.5), source = 'Data/Board.png', allow_stretch = True, keep_ratio = False)
		self.add_widget(self.board) #доска
		self.cursor = Image(size = (40,40), center = (Window.center), source = 'Data/cursor.png')
		self.add_widget(self.cursor) #курсор
		self.add_buttons() #Кнопки
		self.create_enemies('Enemy') #Создание врагов типа 'Enemy'
		self.create_castle() #Создание замка
		self.create_one_tower() #фикс бага
		self.create_labels() #Создание меток




#СОЗДАНИЕ ИГРОВЫХ ЭЛЕМЕНТОВ
	def create_labels(self):
		'''Создание меток'''
		self.money = Label(text = '', font_size = 48, color = [0,0,0,1],
		 center_x = Window.width*3/10, center_y = self.board.center_y, font_name = 'Data/MATURASC.TTF')
		self.add_widget(self.money)

		self.income = Label(text = '', font_size = 48, color = [0,0,0,1],
		 center_x = 50, center_y = self.board.center_y, font_name = 'Data/MATURASC.TTF')
		self.add_widget(self.income)

		self.time_label = Label(text = '', font_size = 48, color = [0,0,0,1],
		 center_x = Window.width-50, center_y = self.board.center_y, font_name = 'Data/MATURASC.TTF')
		self.add_widget(self.time_label)

		self.invasion_label = Label(text = '', font_size = 48, color = [0,0,0,1],
		 pos = (0,0), font_name = 'Data/MATURASC.TTF')
		self.add_widget(self.invasion_label)

		self.timer_label = Label(text = '', font_size = 24, color = [0,0,0,1],
		 center = (Window.width-50, self.board.y - 20), font_name = 'Data/MATURASC.TTF')
		self.add_widget(self.timer_label)

	def create_one_tower(self):
		'''Багфикс для стрел башен'''
		self.bow_towers.append(BowTower((-100,-100)))
		self.add_widget(self.bow_towers[-1])

	def create_castle(self):
		'''Создаёт замок'''
		self.castle = Castle(self.ai_settings)
		self.add_widget(self.castle)

	def create_dragon(self):
		'''Создание дракона'''
		self.dragon = Dragon(self.ai_settings, self.invasion_number); self.add_widget(self.dragon)
		self.add_widget(self.dragon.hp); self.add_widget(self.dragon.hp_label)
		self.dragon_is_true = True
		self.dragon.sound.play() #Звук летящего дракон

	def create_enemies(self, style):
		'''Создаёт врагов разных типов'''
		for i in range(int(self.ai_settings.enemy_quantities[style])):
			self.enemies.append(self.enemy_types[style](self.ai_settings, self.invasion_number))
			self.add_widget(self.enemies[-1])
			self.add_widget(self.enemies[-1].hp)
			self.add_widget(self.enemies[-1].hp_label)




#ОБНОВЛЕНИЕ ВСЕГО
	def update(self, frequency):
		'''Обновление игровых элементов'''
		self.update_labels() #обновление меток
		self.update_enemies() #обновление врагов
		self.update_towers() #обновление башен
		self.update_time() #обновление времени
		self.update_sizes()
		if self.dragon_is_true:
			self.update_dragon()
		if self.warwick_is_true:
			if self.warwick.update(self.enemies, self.frozen_enemies, self, self.bow_towers, self.magic_towers) == 'Killed':
				self.warwick_is_true = False
				self.remove_ww_menu() #При смерти варвика удаляется меню его характеристик

	def update_labels(self):
		'''Обновление всех меток'''
		self.update_game_labels() #Обновление общих игровых меток
		self.update_enemy_labels() #Обновление меток врагов
		if self.improvement_menu == True: #Если открыто меню улучшений
			self.update_IM_labels()

	def update_game_labels(self):
		'''Обновляет общие игровые метки'''
		self.money.text = str(self.player.money) + '$'
		self.time_label.text = str(int(self.time/60))
		if int(self.player.income) >= 0:
			self.income.text = '+' + str(self.player.income)
		elif int(self.player.income) < 0:
			self.income.text = str(self.player.income)
		self.income.x = 30
		self.invasion_label.text = str(self.invasion_number)
		self.timer_label.text = str(self.player.time['hours'])+':'+str(self.player.time['minutes'])+':'+str(int(self.player.time['seconds']/60))

	def update_enemy_labels(self):
		'''Обновляет метки врагов'''
		if len(self.enemies) > 0:
			for enemy in self.enemies:
				enemy.hp.center = (enemy.center_x, enemy.top + 10)
				enemy.hp_label.center = (enemy.hp.pos[0] - 4*len(str(enemy.health_points)), enemy.top + 12)
				enemy.hp_label.text = str(int(enemy.health_points))
		if self.dragon_is_true:
			self.dragon.hp_label.text = str(int(self.dragon.health_points))

	def update_IM_labels(self):
		'''Обновляет метки в меню улучшений'''
		for key in self.sb_labels:
			self.sb_labels[key].text = str(int(self.sb_tower.stats[key]))
			self.sb_price_labels[key].text = str(int(self.sb_tower.prices[key]))			

	def update_sizes(self, *args):
		'''Обновляет размеры и позиции статичных объектов'''
		self.background.pos = (0,0); self.background.size = Window.size
		self.board.pos = (0,Window.size[1]- Window.size[1]/7.5); self.board.size = (Window.size[0], Window.size[1]/7.5)
		self.builders['BowTower'].center = (Window.width*61/96, self.board.center_y)
		self.builders['MagicTower'].center = (Window.width*41/72, self.board.center_y)
		self.builders['Trap'].center = (Window.width*145/288, self.board.center_y)
		self.castle.right = Window.width; self.castle.center_y = Window.height/2
		self.elements['Remover'].center = (Window.width*49/64, self.board.center_y)
		self.elements['Updater'].center = (Window.width*227/324, self.board.center_y)
		self.elements['Copy'].center = (Window.width*5/6, self.board.center_y)
		self.money.center = (Window.width*3/10, self.board.center_y)
		self.income.center = (75 ,self.board.center_y)
		self.time_label.center = (Window.width - 50, self.board.center_y)
		self.magic.center = (Window.width*21/48,self.board.center_y)
		self.timer_label.center = (Window.width-50, self.board.y - 20)





#ФУНКЦИИ ТАЙМЕРА
	def update_time(self):
		'''Обновляет таймер'''
		self.update_full_time()
		if self.time > 0:
			self.time -= 1
		else: self.update_game_parameters() #Обновление игры при обнулении таймера

	def update_full_time(self):
		'''Обновляет общее игровое время'''
		if self.player.time['seconds'] < 3600:
			self.player.time['seconds'] += 1
		else:
			self.player.time['seconds'] = 0
			if self.player.time['minutes'] < 60:
				self.player.time['minutes'] += 1
			else:
				self.player.time['minutes'] = 0
				self.player.time['hours'] += 1

	def update_game_parameters(self):
		'''Обновление игры при обнулении таймера'''
		self.time = 1800 #Сброс таймера
		self.invasion_number += 1 #Смена номера нашествия
		self.update_enemy_parameters() #Обновляет параметры врагов
		self.remove_old_traps() #удаление старых ловушек
		self.remove_old_bodies() #удаление трупов
		self.reset_magic() #Сброс действия заклинаний
		self.update_magic_prices() #Обновление цен на заклинания
		self.player.money += self.player.income #Доход добавляется к деньгам
		if self.player.money < 0: 
			self.remove_one_tower()

	def update_enemy_parameters(self):
		'''Обновляет параметры врагов'''
		for key in self.enemy_types:
			if (self.invasion_number % 2 == 0) and (self.ai_settings.enemy_quantities[key] < self.ai_settings.enemy_quantities[key+'Max']) and self.invasion_number > self.ai_settings.enemy_spawn[key]:
				self.ai_settings.enemy_quantities[key] += 1 #Увеличивается количество врагов
			if self.invasion_number > self.ai_settings.enemy_spawn[key]: #Если пришло время появления
				self.create_enemies(key) #Создание новых врагов
		if self.invasion_number % 10 == 0: #Каждый 10 нашествий появляется дракон
			self.create_dragon()

	def remove_old_bodies(self):
		'''Удаляет трупы при обнулении таймера'''
		for body in self.bodies:
			self.remove_widget(body)
		self.bodies = []

	def remove_old_traps(self):
		'''Удаление старых ловушек'''
		for trap in self.old_traps:
			self.remove_widget(trap)
		self.old_traps = []

	def reset_magic(self):
		'''Сбрасывает действие заклятий'''
		if len(self.frozen_enemies) > 0:
			self.freedom_for_enemies()
		if len(self.slowed_enemies) > 0:
			self.speed_for_enemies()
		if len(self.immortal_towers) > 0:
			self.mortal_for_towers()

	def update_magic_prices(self):
		'''Увеличение цен на заклинания'''
		if self.invasion_number % 10 == 0:
			for key in self.ai_settings.magic_factors:
				self.ai_settings.magic_prices[key] = int(self.ai_settings.magic_prices[key]*self.ai_settings.magic_factors[key])

	def freedom_for_enemies(self):
		'''СВОБОДУ ЗОМБАКАМ'''
		for enemy in self.frozen_enemies:
			if enemy.style == 'Enemy': enemy.source = 'Data/Enemy/Enemy2.gif'
			else: enemy.source = 'Data/Enemy/{}Enemy.gif'.format(str(enemy.style))
		self.frozen_enemies = []

	def speed_for_enemies(self):
		'''СКОРОСТЬ ЗОМБАКАМ'''
		for enemy in self.slowed_enemies:
			enemy.initialize_speed() #Восстановление базовой скорости
		self.slowed_enemies = []

	def mortal_for_towers(self):
		'''СМЕРТЬ БАШНЯМИ'''
		for tower in self.immortal_towers:
			tower.stats['Resistance'] = tower.saved_resistance
		self.immortal_towers = []




#ФУНКЦИИ ДРАКОНА
	def update_dragon(self):
		'''Обновляет дракона'''
		self.dragon.random_walk() #Рандомная "ходьба" дракона
		self.dragon.fireball(self) #Создание файерболла, self здесь нужен, чтобы добавлять и удалять с экрана внутри класса дракона
		self.dragon.check_position(self, Window.width, self.castle) #Проверка позиции дракона




#ФУНКЦИИ ДЛЯ ОБНОВЛЕНИЯ БАШЕН
	def update_towers(self): 
		'''Обновление всех башен'''
		if len(self.bow_towers) > 1: #1 из-за старого доброго багфикса (главное, что это работает)
			for bow_tower in self.bow_towers: #для каждой башни засекается время на строительство
				if bow_tower.building_time == 60: self.update_tower(bow_tower)
		if len(self.magic_towers) > 0:
			for magic_tower in self.magic_towers: #для каждой башни засекается время на строительство
				if magic_tower.building_time == 60: self.update_tower(magic_tower)

	def update_tower(self, tower):
		'''Обновление конкретной башни'''
		self.arrows_need_or_not(tower) #нужно ли создавать стрелы?
		tower.move_arrows() #движение стрел
		for arrow in tower.arrows:
			arrow.check_position(self, tower) #проверка, не вылетели ли стрелы за поле
		for enemy in self.enemies:
			self.check_arrows_enemy_collision(tower, enemy) #проверка коллизии стрелы и врага
		if self.dragon_is_true: #Если присутствует дракон, то стоит проверить коллизии и для него
			self.check_arrows_enemy_collision(tower, self.dragon) #Было решено сделать дракона отдельным от других, возможно зря.

	def arrows_need_or_not(self, tower):
		'''Нужно ли создавать стрелы?'''
		if tower.arrows == []: #Если стрел нет
			tower.create_arrows() #то начинается производство стрел
			self.add_widget(tower.arrows[0]) #и добавление стрел на экран
			self.add_widget(tower.arrows[1])




#ФУНКЦИИ СТРЕЛ
	def check_arrows_enemy_collision(self, tower, enemy):
		'''Проверка коллизии стрелы и врага'''
		for arrow in tower.arrows:
			if arrow.collide_widget(enemy): #Если стрела контактирует с врагов
				arrow.attack_enemy(enemy, self.dragon_is_true) #отнимает хп
				if arrow.damage <= 0: #Если стрела в край ослабла
					self.remove_widget(arrow) #то она удаляется с экрана
					tower.arrows.remove(arrow) #и из списка стрел башни
				if enemy.health_points <= 0: #если умер, то он умер
					self.death_enemy(enemy, 'Kill')
				break

	def death_enemy(self, enemy, how):
		'''Убивает врага, если у того нет хп'''
		if how == 'Kill' or how == 'Magic': #Если враг был убит:
			self.enemy_killed(enemy, how)
		elif how == 'Castle': #Если враг дошёл до замка
			self.player.income -= self.ai_settings.castle_income*enemy.damage
		enemy.initialize_death(self)
		if how != 'Magic' and how != 'Kill': self.remove_widget(enemy) #Если враг был просто убит, то нужно показать эффект смерти, перед удалением с экрана
		if enemy in self.enemies and how != 'Magic': self.enemies.remove(enemy) #непонятный баг иногда возникает

	def enemy_killed(self, enemy, how):
		'''Враг был убит'''
		enemy.anim_loop = 1 #Анимация смерти проигрывается один раз
		enemy.sound.play() #Звук смерти врага запускается
		if how != 'Magic': #Деньги даются, если враг был убит без помощи магии (Варвик делает обычное убийство)
			self.player.money += enemy.price + enemy.price*(int(self.invasion_number/10)) #деньги
			self.player.income += enemy.income + enemy.income*(int(self.invasion_number/10)) #доход
		self.bodies.append(enemy) #трупы, нужно делать уборку, чтобы не было срача




#ФУНКЦИИ ДЛЯ ОБНОВЛЕНИЯ ВРАГОВ
	def update_enemies(self):
		'''Обновляет врагов'''
		if len(self.enemies) > 0:
			for enemy in self.enemies:
				enemy.update_position(self.bow_towers, self.magic_towers, self.frozen_enemies, self.old_traps, self.traps)
				self.check_enemy_position(enemy) #Отслеживание позиции
				self.check_enemy_castle_collision(enemy) #Коллизии замка и врага
				if enemy.style != 'Giant': enemy.check_trap_collision(self.traps, self.old_traps)
				if enemy.style == 'Magician' and enemy not in self.frozen_enemies:
					enemy.attack(self, self.bow_towers, self.magic_towers, magic_sound, self.bodies)
			self.check_enemy_tower_collision(self.bow_towers) #Коллизии врага и башен
			self.check_enemy_tower_collision(self.magic_towers)
			self.money_was_getted = False
		elif self.money_was_getted == False:
			self.get_money()

	def check_enemy_position(self, enemy): 
		'''Проверка позиции врага, если вышел за правый край, то он погибает'''
		if enemy.right > Window.size[0]:
			self.death_enemy(enemy, 'Right')

	def check_enemy_castle_collision(self, enemy):
		'''Проверка коллизии врага и замка'''
		if enemy.collide_widget(self.castle):
			self.death_enemy(enemy, 'Castle')

	def check_enemy_tower_collision(self, towers):
		'''Проверяет коллизии башни с врагами'''
		for i in range(len(towers)):
			if len(self.enemies) > 0:
				result = self.get_len_of_collisions(towers[i])
				if result >= towers[i].stats['Resistance']: #Если урон врагов больше чем может выдержать башня
					if self.improvement_menu: self.remove_stats_board()
					self.remove_arrows(i, towers) #удаляются стрелы башни
					self.remove_widget(towers[i])
					if self.c_tower != None: #Если эту башню хотели скопировать, то стоит удалить её цену
						self.reset_copy_tower()
					del towers[i]
					break

	def get_len_of_collisions(self, tower):
		'''Возвращает урон врагов, контактирующих с башней одновременно'''
		collisions_result = [enemy.damage for enemy in self.enemies if tower.collide_widget(enemy)] #результаты коллизий
		result = sum(collisions_result) #общий урон от врагов по башне
		return result

	def get_money(self):
		'''Получить деньги'''
		self.player.money += 45 + 5*self.invasion_number
		self.money_was_getted = True




#ОБРАБОТКА КАСАНИЙ И РЕЖИМЫ
	def on_touch_down(self, touch):
		'''Отвечает за обработку всех касаний и за режимы кнопок'''
		self.check_mode(touch)
		self.check_touch(touch)

	def on_touch_up(self, touch):
		'''Меняет изображения кнопок при отпускании мыши'''
		self.next.source = 'Data/Buttons/Next.png'
		if self.improvement_menu:
			for key in self.sb_buttons:
				self.sb_buttons[key].source = 'Data/Buttons/' + str(key) + '.png'
		if self.magic_menu:
			for key in self.magic_buttons:
				if key != 'Warwick': self.magic_buttons[key].source = 'Data/Buttons/' + str(key) + '.png'
		if self.warwick_is_true:
			for key in self.ww_buttons:
				self.ww_buttons[key].source = 'Data/Buttons/' + str(key) + '.png'
 
	def check_touch(self, touch):
		'''Проверка всех касаний'''
		for key in self.builders:
			self.builder_check_touch(touch, self.builders[key])
		for key in self.elements:
			self.element_check_touch(touch, self.elements[key])
		self.element_check_touch(touch, self.magic)
		self.button_check_touch(touch, self.next)
		if self.improvement_menu:
			for key in self.sb_buttons:
				self.stats_board_check_touch(touch, self.sb_buttons[key], self.sb_tower)
		if self.magic_menu:
			for key in self.magic_buttons:
				if key != 'Warwick': #Поведение кнопки Варвика отличается, оно похоже с билдерами
					self.button_check_touch(touch, self.magic_buttons[key])
				else: self.builder_check_touch(touch, self.magic_buttons[key])
		if self.c_tower != None: #Если сейчас какая-то башня копируется
			self.copy_tower(touch)
		if self.warwick_is_true:
			for key in self.ww_buttons:
				self.button_check_touch(touch, self.ww_buttons[key])

	def check_mode(self, touch):
		'''Проверка, активирован ли строительный режим'''
		for key in self.builders:
			if self.builders[key].mode == 1: #если режим активирован, то создаётся
				test_tower = self.buildings[key](pos = (touch.x, touch.y)) #тестовая башня
				self.build_mode(test_tower) #попытка построить
		if self.magic_menu and self.magic_buttons['Warwick'].mode == 1: #Проверка режима варвика только если включено магическое меню
			test_mob = Warwick(pos = (touch.x, touch.y), ww_stats = self.ai_settings.ww_stats)  #тестовый моб
			self.create_mob(test_mob) #попытка создать

	def builder_check_touch(self, touch, builder):
		'''Проверка касания'''
		if builder.collide_point(touch.x, touch.y): #В случае нажатия по билдеру
			if builder.mode == 0: #Перевод в режим 1, если был 0
				builder.mode = 1
				if builder.class_name != 'Warwick': self.reset_other_mods(builder) #Сброс режимов остальных билдеров на 0
				builder.source = 'Data/Buttons/Active' + str(builder.class_name) + '.png'
			else:
				builder.mode = 0 #Если режим был равен 1, то сбрасывается в 0
				builder.source = 'Data/Buttons/Shop' + str(builder.class_name) + '.png'

	def button_check_touch(self, touch, button):
		'''Проверка касания по кнопкам и обработка'''
		if button.collide_point(touch.x, touch.y):
			button.source = 'Data/Buttons/' + str(button.class_name) + 'Down.png'
			if button.class_name == 'Next' and not self.dragon_is_true and str(self.invasion_number)[-1] != '9':
				self.time = 0
			for key in self.magic_spells:
				if button.class_name == key:
					self.magic_spells[key]()
			if button.class_name == 'WWDamage' and self.player.money >= self.ww_prices['WWDamage']:
				self.increase_ww_state(button.class_name, 1)
			elif button.class_name == 'WWTime' and self.player.money >= self.ww_prices['WWTime']:
				self.increase_ww_state(button.class_name, 10)

	def reset_other_mods(self, builder):
		'''Сбрасывает другие режимы'''
		for key in self.elements:
			self.elements[key].mode = 0; self.elements[key].source = 'Data/Buttons/' + str(key) + '.png'
		for key in self.builders:
			if builder.class_name != key:
				self.builders[key].mode = 0; self.builders[key].source = 'Data/Buttons/Shop' + str(key) + '.png'
		if self.improvement_menu:
			self.remove_stats_board()
		if self.magic_menu:
			self.remove_magic_menu()
		self.magic.mode = 0; self.magic.source = 'Data/Buttons/Magic.png'
		if self.c_tower != None:
			self.reset_copy_tower()





#СТРОИТЕЛЬСТВО БАШЕН И ЛОВУШЕК
	def build_mode(self, test_tower):
		'''Включает режим строителя'''
		if (test_tower.top < Window.size[1] - 70) and (test_tower.y > 0) and self.building_tower == None and not test_tower.collide_widget(self.castle): #Проверка диапазона
			if (self.check_place(test_tower)) and (self.player.money >= test_tower.price): #проверка местности на коллизии с другими башнями
				self.build_tower(test_tower) #Если башни есть и деньги есть, тогда проверяется местность

	def check_place(self, tower):
		'''Проверяет место для башни на коллизии с другими'''
		collisions_result = [tower.collide_widget(bow_tower) for bow_tower in self.bow_towers] #результаты коллизий
		collisions_result2 = [tower.collide_widget(enemy) for enemy in self.enemies]
		collisions_result3 = [tower.collide_widget(magic_tower) for magic_tower in self.magic_towers]
		collisions_result4 = [tower.collide_widget(trap) for trap in self.traps]
		if (collisions_result == [False for i in range(len(self.bow_towers))]) and (collisions_result2 == [False for i in range(len(self.enemies))]) and (collisions_result3 == [False for i in range(len(self.magic_towers))]) and (collisions_result4 == [False for i in range(len(self.traps))]) and not tower.collide_widget(self.next):
			return True #Если они соответствуют норме, то функция возвращает истину

	def build_tower(self, test_tower):
		'''Строительство одной башни'''
		building_sound.play()
		if test_tower.style == 'Classic':
			self.bow_towers.append(test_tower) #добавление башни в список
		elif test_tower.style == 'Magic':
			self.magic_towers.append(test_tower)
		elif test_tower.style == 'Trap':
			self.traps.append(test_tower)
		self.add_widget(test_tower)
		self.start_building(test_tower) #Начать процесс строительства
		self.player.money -= test_tower.price #Минус деньги
		self.player.income -= test_tower.consumption #Минус доход

	def start_building(self, test_tower):
		'''Начат процесс строительства'''
		if test_tower.style != 'Trap': #Для ловушки не нужно время
			test_tower.source = 'Data/Building' + str(test_tower.class_name) + 'Tower.png'
			self.building_tower = test_tower #Башня, которая сейчас строится
			self.building_timer = Clock.schedule_interval(self.building_process, 1/60) #Время для постройки

	def building_process(self, dt):
		'''Отвечает за таймер при строительстве'''
		self.building_tower.building_time += 1
		if self.building_tower.building_time == 60: #Башня строится 1 секунду
			self.building_tower.source = 'Data/' + str(self.building_tower.class_name) + 'Tower.png'
			self.building_tower = None #Больше никакая башня не строится
			self.building_timer.cancel() #Соответственно процесс постройки прекращается




#ОБЩИЕ ФУНКЦИИ ЭЛЕМЕНТОВ
	def element_check_touch(self, touch, element):
		'''Проверка касания по элементам'''
		if element.collide_point(touch.x, touch.y): 
			if element.mode == 0:
				element.mode = 1
				element.source = 'Data/Buttons/Active' + str(element.class_name) + '.png'
				self.reset_builders_mods(element) #Если ремувер/апдейтер активен, то режимы билдеров становятся равны 0
			else:
				element.mode = 0
				if element.class_name == 'Magic': self.remove_magic_menu() #Отключается и меню
				if element.class_name == 'Updater' and self.improvement_menu: self.remove_stats_board()
				if element.class_name == 'Copy' and self.c_tower != None: self.reset_copy_tower()
				element.source = 'Data/Buttons/' + str(element.class_name) + '.png'
		if element.mode == 1: #Он находится вне collide_point, потому что ждёт клика по башне 
			if element.class_name != 'Magic':
				self.check_touch_to_towers(touch, self.bow_towers, element.class_name)
				self.check_touch_to_towers(touch, self.magic_towers, element.class_name)
			else: self.create_magic_menu() #Магия - это исключение из элементов

	def check_touch_to_towers(self, touch, towers, action):
		'''Проверка касания по башням для элементов'''
		try: #Ловит исключение при удалении башни ремувером
			for i in range(len(towers)):
				if towers[i].collide_point(touch.x, touch.y):
					if action == 'Remover':
						self.remove_tower(towers, i)
					elif action == 'Updater':
						if self.improvement_menu: self.remove_stats_board()
						towers[i].source = 'Data/SB' + str(towers[i].class_name) + 'Tower.png'
						self.create_improvement_menu(towers, i)
					elif action == 'Copy':
						if self.c_tower != None:
							self.reset_copy_tower()
						self.c_tower = towers[i]
						towers[i].source = 'Data/Copy' + str(towers[i].class_name) + 'Tower.png'
						self.create_c_tower_label()					
		except:
			pass

	def reset_builders_mods(self, element):
		'''При нажатии на элемент, сбрасываются все режимы билдеров'''
		for key in self.builders:
			self.builders[key].mode = 0; self.builders[key].source = 'Data/Buttons/Shop' + str(key) + '.png'
		for key in self.elements:
			if element.class_name != key:
				self.elements[key].mode = 0; self.elements[key].source = 'Data/Buttons/' + str(key) + '.png'
		if self.improvement_menu and element.class_name != 'Updater':
			self.remove_stats_board()
		if self.magic_menu and element.class_name != 'Magic':
			self.remove_magic_menu()
		if self.c_tower != None and element.class_name != 'Copy':
			self.reset_copy_tower()
		if element.class_name == 'Magic':
			for key in self.elements: 
				self.elements[key].mode = 0; self.elements[key].source = 'Data/Buttons/' + str(key) + '.png'
		else:
			self.magic.mode = 0; self.magic.source = 'Data/Buttons/Magic.png'




#МЕНЮ С ЗАКЛИНАНИЯМИ
	def create_magic_menu(self):
		'''Создаёт меню с заклинаниями'''
		if not self.magic_menu:
			self.create_magic_board()
			self.add_magic_buttons()

	def create_magic_board(self):
		self.magic_menu = True
		self.magic_board = 	Image(source = 'Data/MagicBoard.png', size = (400,100), right = Window.width, y = 0)
		self.add_widget(self.magic_board)

	def add_magic_buttons(self):
		'''Добавляет кнопки в меню с заклинаниями'''
		i = 0
		for key in self.magic_buttons:
			i += 1
			self.magic_buttons[key] = ImageButton(class_name = str(key), source = 'Data/Buttons/'+str(key)+'.png', size = (60,60), center_x = self.magic_board.x + self.magic_board.width*i/6, center_y = self.magic_board.center_y)
			self.add_widget(self.magic_buttons[key])	
		self.magic_buttons['Warwick'].source = 'Data/Buttons/ShopWarwick.png'

	def check_mouse_position(self, window, position):
		self.remove_widget(self.cursor); self.add_widget(self.cursor) #Отображение курсора поверх всего
		self.cursor.center = position
		if self.magic_menu:
			for key in self.magic_buttons.keys():
				if self.magic_buttons[key].collide_point(position[0], position[1]) and self.magic_labels[key] == False:
					self.magic_labels[key] = Label(text = str(self.ai_settings.magic_prices[key]), center = (self.magic_buttons[key].center_x, self.magic_buttons[key].top), color = [0,0,0,1])
					self.add_widget(self.magic_labels[key])
				elif self.magic_labels[key] != False and not self.magic_buttons[key].collide_point(position[0], position[1]):
					self.remove_widget(self.magic_labels[key])
					self.magic_labels[key] = False

	def remove_magic_menu(self):
		'''Удаляет магическое меню'''
		self.magic_menu = False
		self.remove_widget(self.magic_board)
		for key in self.magic_buttons:
			self.remove_widget(self.magic_buttons[key])

	def kill_all_enemies(self):
		'''Уничтожает всех врагов'''
		if len(self.enemies) > 0 and self.player.money >= self.ai_settings.magic_prices['Kill']:
			self.player.money -= self.ai_settings.magic_prices['Kill']
			for enemy in self.enemies:
				self.death_enemy(enemy, 'Magic')
			self.enemies = []

	def froze_all_enemies(self):
		'''Замораживает всех врагов'''
		if len(self.enemies) > 0 and self.player.money >= self.ai_settings.magic_prices['Cold'] and len(self.frozen_enemies) == 0:
			self.player.money -= self.ai_settings.magic_prices['Cold']
			self.froze_time = 0
			self.frozen_screens = [] #для создания эффекта заморозки
			self.froze = Clock.schedule_interval(self.froze_screen, 1/60)
			for enemy in self.enemies:
				self.frozen_enemies.append(enemy)
				enemy.source = 'Data/Enemy/Frozen'+ str(enemy.style) + '.png'
			
	def froze_screen(self, dt):
		'''Плавный эффект заморозки (Blue Screen)'''
		self.froze_time += 1
		if self.froze_time <= 30:
			with self.canvas:
				Color(.5,1,1,.01)
				self.frozen_screens.append(Rectangle(size = (Window.size), pos = (0,0)))
		elif self.froze_time <= 60:
			self.canvas.remove(self.frozen_screens[-1])
			self.frozen_screens.remove(self.frozen_screens[-1])
		else:
			self.froze.cancel()

	def slow_all_enemies(self):
		'''Замедляет всех врагов'''
		if len(self.enemies) > 0 and self.player.money >= self.ai_settings.magic_prices['Slow'] and len(self.slowed_enemies) == 0:
			self.player.money -= self.ai_settings.magic_prices['Slow']
			for enemy in self.enemies:
				enemy.speed = enemy.speed/2
				self.slowed_enemies.append(enemy)

	def immortal_for_towers(self):
		'''Делает все башни неуязвимыми'''
		if (len(self.bow_towers) > 0 or len(self.magic_towers) > 0) and self.player.money >= self.ai_settings.magic_prices['Immortal'] and len(self.immortal_towers) == 0:
			self.player.money -= self.ai_settings.magic_prices['Immortal']
			self.get_immortal_for_towers(self.bow_towers)
			self.get_immortal_for_towers(self.magic_towers)

	def get_immortal_for_towers(self, towers):
		'''Даёт неуязвимость башням'''
		if len(towers) > 0:
			for tower in towers:
				tower.saved_resistance = tower.stats['Resistance']
				tower.stats['Resistance'] = 99999
				self.immortal_towers.append(tower)

	def create_mob(self, mob):
		'''Создаёт варвика'''
		if (mob.top < Window.size[1] - 70) and (mob.y > 0) and not mob.collide_widget(self.castle) and not self.warwick_is_true: #Проверка диапазона
			if (self.check_place(mob)) and (self.player.money >= self.ai_settings.magic_prices[mob.class_name]) and not mob.collide_widget(self.magic_board): #проверка местности на коллизии с другими башнями
				self.player.money -= self.ai_settings.magic_prices[mob.class_name]
				self.warwick = mob
				self.warwick_is_true = True 
				self.add_widget(mob)
				self.create_ww_menu() #создание меню с характеристиками варвика

	def create_ww_menu(self):
		'''Создаёт доску характеристик варвика'''
		self.ww_buttons = {} #Кнопки в меню характеристик Варвика
		self.ww_prices = {'WWDamage': 10, 'WWTime': 60} #Цены на прокачку стат Варвика
		self.ww_labels = {} #Словарь с метками стат Варвика
		self.ww_price_labels = {} #Словарь с метками цен на прокачку Варвика
		self.create_ww_board()
		self.create_ww_buttons()
		self.create_ww_labels()

	def create_ww_board(self):
		self.ai_settings.ww_stats_board = Image(source = 'Data/StatsBoard.png', size = (Window.width/6.7,Window.height/5), center_x = Window.width/2, y = 0, allow_stretch = True, keep_ratio = False)
		self.add_widget(self.ai_settings.ww_stats_board)

	def create_ww_buttons(self):
		self.ww_buttons['WWDamage'] = ImageButton(class_name = 'WWDamage', source = 'Data/Buttons/WWDamage.png', size = (42,42), center_x = Window.width*0.455, center_y = Window.height*0.15)
		self.add_widget(self.ww_buttons['WWDamage'])

		self.ww_buttons['WWTime'] = ImageButton(class_name = 'WWTime', source = 'Data/Buttons/WWTime.png', size = (42,42), center_x = Window.width*0.455, center_y = Window.height*0.05)
		self.add_widget(self.ww_buttons['WWTime'])

	def create_ww_labels(self):
		self.ww_labels['WWDamage'] = Label(text = str(self.warwick.stats['WWDamage']), font_size = 16, center_x = self.ai_settings.ww_stats_board.center_x, center_y = Window.height*0.15, font_name = 'Data/MATURASC.TTF', color = [.1,.1,.1,1])
		self.add_widget(self.ww_labels['WWDamage'])
		self.ww_price_labels['WWDamage'] = Label(text = str(self.ww_prices['WWDamage']), font_size = 16, center_x = self.ai_settings.ww_stats_board.x + self.ai_settings.ww_stats_board.width*13/16, center_y = Window.height*0.15, font_name = 'Data/MATURASC.TTF', color = [.1,.1,.1,1])
		self.add_widget(self.ww_price_labels['WWDamage'])
		self.ww_labels['WWTime'] = Label(text = str(self.warwick.max_health_time), font_size = 14, center_x = self.ai_settings.ww_stats_board.center_x, center_y = Window.height*0.05, font_name = 'Data/MATURASC.TTF', color = [.1,.1,.1,1])
		self.add_widget(self.ww_labels['WWTime'])
		self.ww_price_labels['WWTime'] = Label(text = str(self.ww_prices['WWTime']), font_size = 16, center_x = self.ai_settings.ww_stats_board.x + self.ai_settings.ww_stats_board.width*13/16, center_y = Window.height*0.05, font_name = 'Data/MATURASC.TTF', color = [.1,.1,.1,1])
		self.add_widget(self.ww_price_labels['WWTime'])

	def remove_ww_menu(self):
		'''Создаёт доску характеристик варвика'''
		self.remove_widget(self.ai_settings.ww_stats_board)
		for key in self.ww_buttons:
			self.remove_widget(self.ww_buttons[key])
			self.remove_widget(self.ww_price_labels[key])
			self.remove_widget(self.ww_labels[key])

	def increase_ww_state(self, state, value):
		'''Увеличивает статы вв'''
		self.player.money -= self.ww_prices[state] #Забирает деньги
		self.ai_settings.ww_stats[state] += value #Увеличивает стату на значение
		self.ww_labels[state].text = str(self.ai_settings.ww_stats[state]) #обновление метки со статой
		self.ww_prices[state] = int(self.ww_prices[state]*1.1) #увеличение цены
		self.ww_price_labels[state].text = str(self.ww_prices[state]) #обновление метки с ценой




#ФУНКЦИИ REMOVER'A
	def remove_tower(self, towers, i):
		'''Удаляет башню при нажатии'''
		self.player.income += towers[i].consumption #прибавка к доходу потребления башни
		self.player.money += int(towers[i].price*0.9) + int(towers[i].spent_money * 0.9) #возврат части потраченных денег
		self.remove_arrows(i, towers) #удаление стрел этой башни
		self.remove_widget(towers[i]) #удаление самой башни
		del towers[i]

	def remove_one_tower(self):
		'''Автоматическое удаление башни при недостатке денег'''
		if len(self.magic_towers) > 0: #Сначала удаляются магические башни, потому их потребление больше
			self.remove_tower(self.magic_towers, -1)
		elif len(self.bow_towers) > 0:
			self.remove_tower(self.bow_towers, -1)

	def remove_arrows(self, number, towers):
		'''Удаляет стрелы указанной башни'''
		for i in range(len(towers[number].arrows)):
			self.remove_widget(towers[number].arrows[i])
		towers[number].arrows = []




#ФУНКЦИИ АПДЕЙТЕРА
	def create_improvement_menu(self, towers, i):
		'''Создаёт меню улучшения башни'''
		if self.improvement_menu == False:
			self.sb_tower = towers[i]
			self.sb_buttons = {'Damage': None, 'Speed': None , 'Resistance': None}
			self.sb_labels = {'Damage': None, 'Speed': None , 'Resistance': None}
			self.sb_price_labels = {'Damage': None, 'Speed': None , 'Resistance': None}
			self.create_stats_board()
			self.create_sb_buttons()
			self.create_sb_labels(towers[i])

	def create_stats_board(self):
		'''Создаёт доску для характеристик башни'''
		self.stats_board = Image(source = 'Data/StatsBoard.png', size = (Window.width/6.7,Window.height*0.25), pos = (Window.width - Window.width/6.7, 0), allow_stretch = True, keep_ratio = False)
		self.add_widget(self.stats_board)
		self.improvement_menu = True

	def create_sb_buttons(self):
		'''Создаёт кнопки на доске характеристик'''
		y_factor = 0.2
		for key in self.sb_buttons:
			self.sb_buttons[key] = ImageButton(class_name = str(key), source = 'Data/Buttons/'+str(key)+'.png', size = (40,40), center_x = Window.width*0.88, center_y = Window.height*y_factor)
			self.add_widget(self.sb_buttons[key])
			y_factor -= 0.08

	def create_sb_labels(self, tower):
		'''Добавляет метки на доске характеристик'''
		y_factor = 0.2
		for key in self.sb_labels:
			self.sb_labels[key] = Label(text = str(tower.stats[key]), font_size = 20, center_x = Window.width*0.925, center_y = Window.height*y_factor, font_name = 'Data/MATURASC.TTF', color = [0,0,0,1])
			self.add_widget(self.sb_labels[key]) #УРОН 
			self.sb_price_labels[key] = Label(text = str(int(tower.prices[key])), font_size = 20, center_x = Window.width*0.97, center_y = Window.height*y_factor, font_name = 'Data/MATURASC.TTF', color = [0,0,0,1])
			self.add_widget(self.sb_price_labels[key]) #ЦЕНА УРОНА
			y_factor -= 0.08

	def stats_board_check_touch(self, touch, button, tower):
		'''Проверяет касания по кнопкам на доске характеристик'''
		if button.collide_point(touch.x, touch.y): #В случае нажатия определяется тип кнопки
			button.source = 'Data/Buttons/' + str(button.class_name) + 'Down.png' #Картинка меняется на активную
			for key in tower.stats.keys():
				if (button.class_name == key) and (self.player.money >= tower.prices[key]):
					tower.spent_money += tower.prices[key]
					self.player.money -= tower.prices[key]
					tower.stats[key] += 1
					tower.prices[key] = int(tower.prices[key] * 1.3)

	def remove_stats_board(self):
		'''Удаляет доску характеристик башни'''
		self.remove_widget(self.stats_board)
		for key in self.sb_buttons:
			self.remove_widget(self.sb_buttons[key])
			self.remove_widget(self.sb_labels[key])
			self.remove_widget(self.sb_price_labels[key])
		self.sb_tower.source = 'Data/' + str(self.sb_tower.class_name) + 'Tower.png'
		self.improvement_menu = False




#ФУНКЦИИ COPY
	def copy_tower(self, touch):
		'''Копирует башню'''
		if self.player.money >= (self.c_tower.spent_money + self.c_tower.price) and self.c_tower not in self.immortal_towers:
			if self.c_tower.style == 'Classic': test_tower = BowTower(pos = (touch.x, touch.y))
			elif self.c_tower.style == 'Magic': test_tower = MagicTower(pos = (touch.x, touch.y))
			if (self.check_place(test_tower)) and (test_tower.top < Window.size[1] - 70) and (test_tower.y > 0) and self.building_tower == None and not test_tower.collide_widget(self.castle):
				self.player.money -= self.c_tower.spent_money
				self.build_tower(test_tower)
				test_tower.stats = self.c_tower.stats.copy()
				test_tower.prices = self.c_tower.prices.copy()
				test_tower.spent_money = self.c_tower.spent_money
				self.reset_copy_tower()

	def create_c_tower_label(self):
		self.c_tower_label = Label(text = str(self.c_tower.spent_money + self.c_tower.price), center = (self.c_tower.center_x, self.c_tower.top + 5), color = [1,1,1,1])
		if self.player.money < int(self.c_tower_label.text):
			self.c_tower_label.color = [1,0,0,1]
		self.add_widget(self.c_tower_label)
			
	def reset_copy_tower(self):
		self.c_tower.source = 'Data/' + str(self.c_tower.class_name) + 'Tower.png'
		self.c_tower = None
		self.remove_widget(self.c_tower_label)




class GameApp(App):
	def build(self):
		self.title = 'Tower Defense'
		self.game = Game()
		self.game.draw_game()
		Window.bind(mouse_pos = self.game.check_mouse_position)
		Clock.schedule_interval(self.game.update, 1/60)
		return self.game
 
GameApp().run()