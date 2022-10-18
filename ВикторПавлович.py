import pygame
import random




pygame.init()

width = 800
height = 600

#time 
time = pygame.time.get_ticks()
time_box = pygame.time.get_ticks()
appear_box = 12000
appear_time = 6000

#colors
bg_color = (10, 19, 55)
black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

#main action bools
mov_left = False
mov_right = False
shoot = False

#enemy actions
e_mov_left = False
e_mov_right = False

#image downloads
sphere = pygame.image.load('sphere.png')
sphere = pygame.transform.scale(sphere, (sphere.get_width()//2.5, sphere.get_height()//2.5))
sphere_bar = pygame.transform.scale(sphere, (sphere.get_width()//1.5, sphere.get_height()//1.5))
bg_image = pygame.image.load('bgimage.png')
bg_image = pygame.transform.scale(bg_image, (width, height))


medicine = pygame.image.load('medicine.png')

#Gravity
GRAVITY = 0.75
#FPS controler
clock = pygame.time.Clock()
FPS = 60

#kills
count_kills = 0

sc = pygame.display.set_mode((width, height))
pygame.display.set_caption('ВикторПавлович')


def draw_bg():
    sc.blit(bg_image, (0, 0))

class Charact(pygame.sprite.Sprite):

    
    def __init__(self, x, y, scale, img, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img)
        self.flip = False
        self.rotate = False
        self.speed = speed
        self.direction = 1
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))        
        self.rect = self.image.get_rect(center = (x, y))
        self.jump = False
        self.double_jump = False
        self.in_air = False
        self.vel_y = 0
        self.killed = False
        self.ammo = ammo
        self.start_ammo = ammo
        self.health = 100
        self.max_health = 100
        self.enemy_left = False
        self.enemy_right = False
        #time codes
        self.shoot_cooldown = 0
        self.enemy_disappear_time = 600


    def move(self, mov_left, mov_right):
        x_change = 0
        y_change = 0
        if not mov_left and not mov_right:
            self.rotate = False
        if mov_left:
            x_change = -self.speed
            self.direction = -1
            self.flip = True
            self.rotate = True
        if mov_right:
            x_change = self.speed
            self.direction = 1
            self.flip = False
            self.rotate = True
        
        #JUMP

        self.Jump()
        if self.double_jump:
            self.vel_y = -10
            self.in_air = True
            self.double_jump = False
        
            self.vel_y += GRAVITY
            if  self.vel_y > 9:
                self.vel_y = 0
                self.double_jump = False
            
        #collision with line
        if self.rect.y + y_change > 528:
            self.in_air = False
            y_change = 592 - self.rect.bottom

        
        #collision with enemy
        for enemy in enemy_group:
            if not enemy.killed:
                if abs(enemy.rect.x - self.rect.x) <= 64 and\
                    abs(enemy.rect.y - self.rect.y) < 59:
                    x_change -= self.speed
                    self.collsion_enemy(enemy)
        self.rect.x += x_change
        self.rect.y += y_change

    
    def move_enemy(self, mov_left, mov_right):
        x_change = 0
        y_change = 0
        if not mov_left and not mov_right:
            self.rotate = False
        if mov_left:
            x_change = -self.speed
            self.direction = -1
            self.flip = True
            self.rotate = True
        if mov_right:
            x_change = self.speed
            self.direction = 1
            self.flip = False
            self.rotate = True

        
        #collision with line
        if self.rect.y + y_change > 528:
            self.in_air = False
            y_change = 592 - self.rect.bottom

        self.rect.x += x_change
        self.rect.y += y_change



    def enemy_disappear(self):
        if self.killed == True:
            self.enemy_disappear_time -= 3

        if self.enemy_disappear_time == 0:
            self.kill()
    

        

    def update(self):
        self.check_killed()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.enemy_disappear()



    def Jump(self):
        if self.jump and not self.in_air:
            self.vel_y = -12
            self.in_air = True
            self.jump = False
        
        self.vel_y += GRAVITY
        if  self.vel_y > 10:
            self.vel_y = 0
        
        self.rect.y += self.vel_y
    
    #check collision with player and enemy
    def kill_jump(self, other):
        if not other.killed:
            if abs(self.rect.x - other.rect.x) <= 64 and abs(self.rect.y - other.rect.y) in range(60, 70):
                other.health -= 35
                self.double_jump = True
                
                
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
    
    def check_killed(self):
        if not self.killed :
            if self.health <= 0:
                self.speed = 0
                self.health = 0
                self.image = pygame.transform.rotate(self.image, 90)
                self.killed = True
   

    def collsion_enemy(self, enemy):
        ricashet_speed = 7
        self.health -= 30

        while ricashet_speed > 0:
            self.update()
            self.rect.x += (enemy.direction * ricashet_speed)
            ricashet_speed -= 0.2

    

    def draw(self):
        img = pygame.transform.flip(self.image, self.flip, False)
        if self.rotate:
            img = pygame.transform.rotate(img, 5 if self.flip else -5)
        sc.blit(img, self.rect)



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = sphere
        self.speed = 10
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction


    def update(self):
        self.rect.x += (self.direction * self.speed)

        #check if the bullet disappeared from screen
        if self.rect.right < 0 or self.rect.left > width:
            self.kill()

        #the collision of the bullet with enemies
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if not enemy.killed:
                    self.kill()
                    enemy.health -= 34

class Bullet_bar:
    def __init__(self, x, y, ammo):
        self.x = x
        self.y = y
        self.ammo = ammo
        self.img_list = []
        self.x = 20
        for i in range(self.ammo):
            self.img_list.append((sphere_bar, self.x))
            self.x += 30

    def draw(self, new_ammo):
        for img, x in self.img_list[:new_ammo]:         
            sc.blit(img, (x, self.y))
    



class Healer_bar:
    def __init__(self, x, y, health, health_max, width, height):
        self.x = x
        self.y = y
        self.health = health
        self.health_max = health_max
        self.width = width
        self.height = height


    def draw(self, player_health):
        #helth of player right now
        self.health = player_health
        #health ratio is equal to
        ratio = self.health / self.health_max
        pygame.draw.rect(sc, black, (self.x, self.y, self.width, self.height)) # 154 24
        pygame.draw.rect(sc, red, (self.x + 2, self.y + 2, self.width - 4, self.height - 4)) 
        pygame.draw.rect(sc, green, (self.x + 2, self.y + 2, (self.width - 4) * ratio, self.height-4))



class Boxes(pygame.sprite.Sprite):
    appear_new = 5000
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.y_change = 3
        self.image = img
        self.image = pygame.transform.scale(self.image, (self.image.get_width()//1.3, self.image.get_height() // 1.3))
        self.rect = self.image.get_rect(center = (x, y))
        self.appear = False


    def moving(self):
        if self.rect.y + self.y_change > 528:
            self.y_change = 0
        
        self.rect.y += self.y_change 

    

    def update(self):
        for icon in healing_icons:
            icon.moving()
        if pygame.sprite.spritecollide(main, healing_icons, False):
            self.kill()
            if main.health <= 60:
                main.health += 40
            else:
                main.health = 100

#making boxes of bullets and medicine
'''
class Boxes(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.y_change = 3
        self.img = pygame.image.load(img)

        self.rect = self.img.get_rect(center = (self.x, self.y))
    def draw(self):
        sc.blit(self.img, self.rect)

    def moving(self):
        if self.rect.y + self.y_change > height:
            self.y_change = 0
        
        self.rect.y += self.y_change

    def upadte(self, main):
'''

#logic movement of enemies
def AI(enemy):
    global e_mov_left
    global e_mov_right

    if enemy.rect.x > main.rect.x:
            e_mov_left = True
            e_mov_right = False
    elif enemy.rect.x < main.rect.x:
            e_mov_left = False
            e_mov_right = True
    #in air


def creating_objects(enemies: pygame.sprite.Group(), healer_icons: pygame.sprite.Group()):
    global time
    global appear_time
    global appear_box
    time_new = pygame.time.get_ticks()

    if appear_time < 1000:
        appear_time = random.randint(500, 2000)
    if time_new - time > appear_time:
        x1 = (random.randint(-100, 0))
        x2 = random.randint(width + 200, width + 300)
        enem_left = Charact(x1, 560, 1, 'enemy.png', 1, 5)
        enem_right = Charact(x2, 560, 1, 'enemy.png', 1, 5)

        enemies.add(enem_left)
        enemies.add(enem_right)
        time = pygame.time.get_ticks()
        appear_time -= 200

    if time_new - time > appear_box:
        icon = Boxes(random.randont(50, width - 50), -40, medicine)
        healer_icons.add(icon)
        time_box = pygame.time.get_ticks()





bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


main = Charact(300, 560, 1, 'main.png', 5, 5)

bullet_bar = Bullet_bar(10, 50, main.ammo)
healer_bar = Healer_bar(10, 10, main.health, 100, 154, 24)


healing_icons = pygame.sprite.Group()
healing_icon1 = Boxes(random.randint(100, width-50), -40, medicine)
healing_icons.add(healing_icon1)




#main loop
game_exit = False

while not game_exit:
    draw_bg()

    creating_objects(enemy_group, healing_icons)

    for enm in enemy_group:
        enm.update()
        enm.draw()
        if not enm.killed:
            healer_bar_e = Healer_bar(enm.rect.x, enm.rect.y-10, enm.health, 100, 64, 9)
            healer_bar_e.draw(enm.health)
            if not main.killed:
                AI(enm)
            enm.move_enemy(e_mov_left, e_mov_right)
            main.kill_jump(enm)

    if not main.killed:
        if shoot:
            main.shoot()
        main.move(mov_left, mov_right)

    main.draw()
    main.update()

    bullet_group.update()
    bullet_group.draw(sc)

    healer_bar.draw(main.health)
    bullet_bar.draw(main.ammo)

    healing_icons.update()
    healing_icons.draw(sc)
    
    #bullet groups
    
    
        

    
    for event in pygame.event.get():

        #quit game
        if event.type == pygame.QUIT:
            game_exit = True
        
        #keyboard presses
        if event.type == pygame.KEYDOWN:
        
            if event.key == pygame.K_LEFT:
                mov_left = True
            elif event.key == pygame.K_RIGHT:
                mov_right = True
            elif event.key == pygame.K_UP:
                if not main.in_air:
                    main.jump = True
            elif event.key == pygame.K_SPACE:
                shoot = True
       

        #keyboard unpresses
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                mov_left = False
            elif event.key == pygame.K_RIGHT:
                mov_right = False
            elif event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
