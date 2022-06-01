import pygame
import os
from Network import Network
pygame.font.init()

#Frame per sec
FPS = 60

#font
HP_font = pygame.font.SysFont('comicsans', 40)
winner_font = pygame.font.SysFont('comicsans', 80)

#Window Size
bulletA_color = (255,0,0)
bulletB_color = (0,255,0)
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
BORDER = pygame.Rect((WIDTH//2)-5,0,10,HEIGHT) #x,y=0 mean from the top of the screen,width = any, height = height of the screen

#name of window
pygame.display.set_caption("Client Game")
#How many client
clientNumber = 0
#Background Default Color
WHITE = (255, 255, 255)

#CHARACTER image
spaceShipA = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
spaceShipB = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
space_bg = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')),(WIDTH,HEIGHT))
#scale down
shipH,shipW = 60,40
spaceShipA = pygame.transform.rotate(pygame.transform.scale(spaceShipA, (shipH,shipW)),90)
spaceShipB = pygame.transform.rotate(pygame.transform.scale(spaceShipB, (shipH,shipW)),270)

#player event
ship_hit = pygame.USEREVENT + 2


class player():
	def __init__(self, x, y, WID, HEI, image, hp, id ='none'):
		self.x = x
		self.y = y
		self.hp = hp
		self.id = id
		self.WIDTH = WID
		self.HEIGHT = HEI
		self.image = image
		self.rect = pygame.Rect(x, y, WID, HEI)
		self.moveSpeed = 2
		self.bullet_speed = 5
		self.max_bullets = 5
		self.bul = []

	def move(self):
		keys_pressed = pygame.key.get_pressed()

		if keys_pressed[pygame.K_a] and (self.x - self.moveSpeed > 0 if self.id == 0 else self.x - self.moveSpeed > BORDER.x):
			self.x -= self.moveSpeed
		if keys_pressed[pygame.K_w] and self.y - self.moveSpeed > 0:
			self.y -= self.moveSpeed	
		if keys_pressed[pygame.K_d] and (self.x + self.moveSpeed < BORDER.x - self.WIDTH if self.id == 0 else self.x + self.moveSpeed < WIDTH - self.WIDTH):
			self.x += self.moveSpeed	
		if keys_pressed[pygame.K_s] and self.y + self.moveSpeed < HEIGHT - self.HEIGHT:
			self.y += self.moveSpeed
		self.update()

	def bullet(self, otherShip):
		for bullet in self.bul:
			if self.id == 0:
				bullet.x += self.bullet_speed
				if otherShip.rect.colliderect(bullet):
					pygame.event.post(pygame.event.Event(ship_hit))  # event player B got hit
					self.bul.remove(bullet)
				elif bullet.x > WIDTH:
					self.bul.remove(bullet)

			else:
				bullet.x -= self.bullet_speed
				if otherShip.rect.colliderect(bullet):
					pygame.event.post(pygame.event.Event(ship_hit))  # event player B got hit
					self.bul.remove(bullet)
				elif bullet.x < 0:
					self.bul.remove(bullet)
		self.update()

	def update(self):
		self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
		self.bul = self.bul

def draw_winner(text):
	win_text = winner_font.render(text,1,WHITE)
	WIN.blit(win_text,(WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))
	pygame.display.update()
	pygame.time.delay(5000) #delay the win screen then restart the game?

def draw_window(WIN, player1, player2):
	#WIN.fill(WHITE)
	WIN.blit(space_bg, (0, 0))
	WIN.blit(player1.image, (player1.x, player1.y))
	WIN.blit(player2.image, (player2.x, player2.y))

	for bullet in player1.bul:
		pygame.draw.rect(WIN, bulletA_color, bullet)

	for bullet in player2.bul:
		pygame.draw.rect(WIN, bulletB_color, bullet)

	HP_text_A = HP_font.render("HP: " + str(player2.hp), 1, WHITE)
	HP_text_B = HP_font.render("HP: " + str(player1.hp), 1, WHITE)

	if player1.id == 0:
		WIN.blit(HP_text_A, (10, 10))
		WIN.blit(HP_text_B, (WIDTH - HP_text_B.get_width() - 10, 10))
	else:
		WIN.blit(HP_text_B, (10, 10))
		WIN.blit(HP_text_A, (WIDTH - HP_text_A.get_width() - 10, 10))

	pygame.display.update()


def main():
	clock = pygame.time.Clock()
	run = True

	#start connect
	n = Network()
	#geting position of each player from server after connection
	string_POS = n.getPos()
	startPos = string_POS

	#create player 100,200
	if(startPos[2] == 0):
		p1 = player(startPos[0], startPos[1], shipW, shipH, spaceShipA, startPos[4], startPos[2] )
		p2 = player(800, 200, shipW, shipH, spaceShipB, hp =10)
	else:
		p1 = player(startPos[0], startPos[1], shipW, shipH, spaceShipB, startPos[4], startPos[2])
		p2 = player(100, 200, shipW, shipH, spaceShipA, hp =10)

	#bul = [] #bullet holder
	#bul2 = []

	while  run:
		#player 1 send his position to server and receive position of player 2
		p2Pos = n.send_data([p1.x, p1.y, p1.hp, p1.bul])
		p2.x = p2Pos[0]
		p2.y = p2Pos[1]
		p2.hp = p2Pos[4]
		p2.rect = pygame.Rect(p2.x, p2.y, p2.WIDTH, p2.HEIGHT) #update p2 rect
		p2.bul = p2Pos[3] #get bullet pos of other player

		if p2Pos[5]!="":
			draw_winner(p2Pos[5])
			break


		clock.tick(FPS)  #control the speed of the while loop

		for event in pygame.event.get():  #get event happen
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()  #if client quit program -> quit

			if event.type == pygame.KEYDOWN: #press each time to shoot bullet
				if event.key == pygame.K_LCTRL and len(p1.bul) < p1.max_bullets:  # left ctrl
					bullet = pygame.Rect(p1.x + p1.WIDTH, p1.y + p1.HEIGHT // 2 - 2, 10, 5)  # x,y,width,height || fire bullet
					p1.bul.append(bullet)  # add bullet in list
					#bullet_fire_sound.play()

			if event.type == ship_hit:
				p1.hp -= 1

		p1.move()
		p1.bullet(p2)

		draw_window(WIN, p1, p2)
		#print(p2.rect)
	pygame.quit()
	#main()

if __name__ == "__main__":
	main()