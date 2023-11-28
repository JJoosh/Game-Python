import pygame, random, math

WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = (0, 255, 0)

pygame.init()
pygame.mixer.init()

#tamaño de pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))

#se carga fondo
#se declaran variables x/y x1/y1 para el paralaje
bg = pygame.image.load("assets/background.png")
background_rect = bg.get_rect()
x = 0
y = 0

x1 = 0
y1 = -HEIGHT

#contador de frames
clock = pygame.time.Clock()
tiempo_transcurrido = pygame.time.get_ticks()

#fuentes de texto
def draw_text(surface, text, size, x, y):
	font = pygame.font.SysFont("serif", size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surface.blit(text_surface, text_rect)

#CLASES

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = ship_anim[0] #se inicia el objeto con el primer frame de la animacion correspondiente
		self.rect = self.image.get_rect()
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 30 
		self.rect.centerx = WIDTH // 2
		self.rect.bottom = HEIGHT - 10
		self.speed_x = 0
		self.shield = 5

	def update(self):

		now = pygame.time.get_ticks()
		self.speed_x = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_LEFT] or keystate[ord('a')]: #MOVIMIENTO
			self.speed_x = -5
		if keystate[pygame.K_RIGHT] or keystate[ord('d')]:
			self.speed_x = 5
		self.rect.x += self.speed_x #Desplazamiento horizontal
		if self.rect.right > WIDTH:
			self.rect.right = WIDTH
		if self.rect.left < 0:
			self.rect.left = 0

		if now - self.last_update > self.frame_rate: #cambio de frame de animación
			self.last_update = now
			self.frame += 1
			if self.frame > len(ship_anim)-1: #si el frame es el ultimo (tamaño lista), vuelve al primero (0)
				self.frame = 0
				self.image = ship_anim[0]
			else: 
				self.image = ship_anim[self.frame]

	#Disparo
	def shoot(self):
		bullet = Bullet(self.rect.centerx, self.rect.top)
		all_sprites.add(bullet)
		bullets.add(bullet)
		#laser_sound.play()

class Health_Bar(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = shield[5] #se inicia la barra de energia en el ultimo frame de la colección (barra llena)
        self.rect = self.image.get_rect(topleft=(x, y)) #ubicación de la barra de energia

    def update(self):
        if player.shield != 0:
            self.image = shield[player.shield] #se le asigna el valor de la energia de la nave (inicia en 5) a la barra de energia,
											   #si la energia disminuye, la barra lo hace de igual manera

class Alien(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.aleatorio = random.choice(alien_images) #selecciona aleatoriamente un skin para el alien desde la colección alien_images
		self.image = self.aleatorio[0] #asigna el primer frame de la skin seleccionada anteriormente
		self.rect = self.image.get_rect()
		self.rect.y = -20	#ubicacion 20 pixeles por encima del tope de pantalla, evita aparición abrupta
		self.rect.x = random.randrange(0, 800) #ubicación aleatoria sobre el eje x
		self.speedy = 2
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 120 

	def update(self):
		now = pygame.time.get_ticks()
		self.rect.y += self.speedy
		if now - self.last_update > self.frame_rate: #cambio de frame de animación
			self.last_update = now
			self.frame += 1
			if self.frame > 5-1:
				self.frame = 0
				self.image = self.aleatorio[0]
			else: 
				self.image = self.aleatorio[self.frame]
		
		if self.rect.top > HEIGHT + 10 or self.rect.left < -40 or self.rect.right > WIDTH + 40: #RECICLAJE: si un alien escapa,
			self.rect.x = random.randrange(WIDTH - self.rect.width)								#vuelve a generarse en la parte superior
			self.rect.y = -20
			self.speedy = 3

class Meteor(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = random.choice(meteor_images) #selecciona una imagen aleatoria de la colección de meteoros
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = -20
		self.speedy = random.randrange(1, 10)
		self.speedx = random.randrange(-5, 5)

	def update(self):
		self.rect.y += self.speedy
		self.rect.x += self.speedx

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.image.load("assets/laser1.png") #asigna imagen de disparo
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.y = y		#direccionamiento lineal sobre el eje y
		self.rect.centerx = x
		self.speedy = -10	#velocidad continua

	def update(self):
		self.rect.y += self.speedy
		if self.rect.bottom < 0:
			self.kill()		#si llega a la parte superior, se elimina

class Explosion(pygame.sprite.Sprite):
	def __init__(self, center):
		super().__init__()
		self.image = explosion_anim[0]
		self.rect = self.image.get_rect()
		self.rect.center = center 
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 50 # VELOCIDAD DE LA EXPLOSION

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

class Meteor_Explosion(pygame.sprite.Sprite):
	def __init__(self, center):
		super().__init__()
		self.image = meteor_explosion_anim[0]
		self.rect = self.image.get_rect()
		self.rect.center = center 
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 50 # VELOCIDAD DE LA EXPLOSION

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(meteor_explosion_anim):
				self.kill()
			else:
				center = self.rect.center
				self.image = meteor_explosion_anim[self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

#defino pantalla de inicio
def show_tittle_screen():
	screen.blit(background, [0,0])
	draw_text(screen, "Navecita", 80, WIDTH // 2, HEIGHT // 4)
	draw_text(screen, "Movimiento: Izquierda/'a'  Derecha/'d'", 25, WIDTH // 2, HEIGHT // 2)
	draw_text(screen, "Disparo: Barra espaciadora", 25, WIDTH // 2, HEIGHT // 2+25)
	draw_text(screen, "Presionar cualquier tecla...", 25, WIDTH // 2, HEIGHT * 3/4)
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False

#pantalla game over
def show_game_over_screen():
	screen.blit(background, [0,0])
	draw_text(screen, "GAME OVER", 70, WIDTH // 2, HEIGHT // 4)
	draw_text(screen, "Puntos: " + str(score_aux), 30, WIDTH // 2, HEIGHT * 2/4)
	draw_text(screen, "Distancia: " + str(distance)+"m", 30, WIDTH // 2, HEIGHT * 2/4 + 30)
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False

#colección de meteoros
meteor_images = []
meteor_list = ["assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png", "assets/meteorGrey_big4.png",
				"assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png", "assets/meteorGrey_small2.png",
				"assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"]
for img in meteor_list:
	meteor_images.append(pygame.image.load(img).convert())

####----------------NAVE ANIMACION-------------------
ship_anim = []
for i in range(3):
	file = "assets/arwing{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (100,100))
	ship_anim.append(img_scale)

####----------------BARRA ENERGIA-------------------
shield = []
for i in range(6):
	file = "assets/barra_energia{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (162,30))
	shield.append(img_scale)

####----------------ALIENS ANIMACION-------------------

alien1_anim = []
for i in range(5):
	file = "assets/alien{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	alien1_anim.append(img_scale)

alien2_anim = []
for i in range(5):
	file = "assets/alien2{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	alien2_anim.append(img_scale)

alien3_anim = []
for i in range(5):
	file = "assets/alien3{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	alien3_anim.append(img_scale)

alien4_anim = []
for i in range(5):
	file = "assets/alien4{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	alien4_anim.append(img_scale)

alien5_anim = []
for i in range(5):
	file = "assets/alien5{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	alien5_anim.append(img_scale)

alien_images = [alien1_anim, alien2_anim, alien3_anim, alien4_anim, alien5_anim]

####----------------EXPLOSIONES ANIMACION --------------
explosion_anim = []
for i in range(9):
	file = "assets/regularExplosion0{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (100,100))
	explosion_anim.append(img_scale)

meteor_explosion_anim = []
for i in range(9):
	file = "assets/meteorExplosion0{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (100,100))
	meteor_explosion_anim.append(img_scale)

background = pygame.image.load("assets/background.png").convert()

# Cargar sonidos
laser_sound = pygame.mixer.Sound("assets/laser5.ogg")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.set_volume(0.2)


#pygame.mixer.music.play(loops=-1)

#### ----------GAME OVER
game_over = True
running = True
while running:

	if game_over:

		show_tittle_screen()	#menu principal

		game_over = False

		#listas de sprites y objetos a utilizar
		all_sprites = pygame.sprite.Group()
		meteor_list = pygame.sprite.Group()
		bullets = pygame.sprite.Group()
		enemy_list = pygame.sprite.Group()
		alien_list = pygame.sprite.Group()


		#se instancia jugador y barra de energia
		#se guardan sprites en lista principal de sprites
		energia = Health_Bar(10, 5)
		player = Player()
		all_sprites.add(energia)
		all_sprites.add(player)

		tiempo_transcurrido = pygame.time.get_ticks()

		#se inicializa puntaje y distancia en 0
		score = 0
		distance = 0

		#se generan 5 alien por vez
		for i in range(5):
		
			alien = Alien()
			all_sprites.add(alien)
			alien_list.add(alien)	
	
	clock.tick(60)
	distance = (pygame.time.get_ticks() - tiempo_transcurrido)//1000 #distancia = reloj interno dividido 1000 (para que muestre solo segundos transcurridos)
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				player.shoot()

		if distance != 0 and distance % 10 == 0: #se generan meteoros cada 10 m de distancia
			for i in range(1):
				meteor = Meteor()
				all_sprites.add(meteor)
				meteor_list.add(meteor)

	all_sprites.update()	

	#colisiones - meteoro - laser
	hits = pygame.sprite.groupcollide(meteor_list, bullets, True, True)
	for hit in hits:
		score += 30
		#explosion_sound.play()
		meteor_explosion = Meteor_Explosion(hit.rect.center)
		all_sprites.add(meteor_explosion)
		meteor = Meteor()
		all_sprites.add(meteor)
		meteor_list.add(meteor)

	# Checar colisiones - jugador - meteoro
	hits = pygame.sprite.spritecollide(player, meteor_list, True)
	for hit in hits:
		player.shield -= 1
		meteor = Meteor()
		all_sprites.add(meteor)
		meteor_list.add(meteor)
		if player.shield <= 0:
			show_game_over_screen()
			game_over = True

	#colisiones - alien - laser
	hits = pygame.sprite.groupcollide(alien_list, bullets, True, True)
	for hit in hits:
		score += 50
		#explosion_sound.play()
		explosion = Explosion(hit.rect.center)
		all_sprites.add(explosion)
		alien = Alien()
		all_sprites.add(alien)
		alien_list.add(alien)

	# Checar colisiones - jugador - alien
	hits = pygame.sprite.spritecollide(player, alien_list, True)
	for hit in hits:
		player.shield -= 1
		alien = Alien()
		all_sprites.add(alien)
		alien_list.add(alien)
		score_aux = score
		if player.shield <= 0:
			show_game_over_screen()
			game_over = True

	

	##scrolling vertical
	y1 += 4
	y += 4

	screen.blit(bg, [x, y])
	screen.blit(bg,(x1,y1))

	if y > HEIGHT:
    		y = -HEIGHT
        
	if y1 > HEIGHT:
    		y1 = -HEIGHT

	
	all_sprites.draw(screen)

	#Marcador
	draw_text(screen, str(score), 25, WIDTH // 2, 10)
	draw_text(screen, str(distance)+ "m", 25, 700, 10)
	

	pygame.display.flip()
pygame.quit()
