import pygame
import random
import sys
import math

from termcolor import colored, cprint

from pyfader import IFader

pygame.init()

# IMPORTANT: DEBUG
debug = True
edu = True

vir = []

v_num = "1.0.1"
v_type = "Edu"
v_text = "Space Invader " + v_num + " [" + v_type + "]"

game_state = "ingame"

lost = False

if debug:
    v_text = v_text + " - Debug [ON]"

cprint(f'[INFO] Starting game log...', 'green')

# COLOR
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 165, 126)
blue = (30, 144, 255)

# IMPORT FONT
debug_font = pygame.font.Font('./asset/additional/debug_font.ttf', 15)
health_font = pygame.font.Font('./asset/additional/main_font.ttf', 17)

# pygame.display.set_icon(pygame.image.load('./asset/game_icon.png'))
pygame.display.set_caption(v_text)

# WEIGH,HEIGHT
w = 1200
h = 750

# OPTIMIZED FOR SCREEN
default_player_coord = [int(w / 2), int(h / 2)]

game_display = pygame.display.set_mode((w, h))
screen = pygame.Surface((w, h))

# IMPORT ASSET
ingame_bg_no = pygame.image.load("./asset/background/1.jpg")
ingame_equipment = pygame.image.load("./asset/ingame/equipment.png")
ingame_inventory = pygame.image.load("./asset/ingame/inventory.png")
pause_fade_no = pygame.image.load("./asset/pause/fade.png")
box = pygame.image.load("./asset/ingame/box.png")

quit_game_normal = pygame.image.load("./asset/UI/quit_game_normal.png")
quit_game_mention = pygame.image.load("./asset/UI/quit_game_metion.png")

cursor_no = pygame.image.load("./asset/UI/cursor.png")

# FPS
clock = pygame.time.Clock()

# OPTIMIZED FOR SCREEN
ingame_bg = pygame.transform.scale(ingame_bg_no, (w, h))
cur_img = pygame.transform.scale(cursor_no, (40, 40))
pause_fade = pygame.transform.scale(pause_fade_no, (w, h))


def ingame_background():
    screen.blit(ingame_bg, [0, 0])


def print_screen(text, color, size, x, y):
    gen_font = pygame.font.Font('./asset/additional/main_font.ttf', size)
    gen_text = gen_font.render(text, True, color)
    screen.blit(gen_text, [x, y])


def print_screen_left(text, color, size, y):
    gen_font = pygame.font.Font('./asset/additional/main_font.ttf', size)
    gen_text = gen_font.render(text, True, color)
    gen_text_width, gen_text_height = gen_font.size(text)
    screen.blit(gen_text, [w - gen_text_width - 15, y])


def print_screen_center(text, color, size, y):
    gen_font = pygame.font.Font('./asset/additional/main_font.ttf', size)
    gen_text = gen_font.render(text, True, color)
    gen_text_width, gen_text_height = gen_font.size(text)
    screen.blit(gen_text, [w / 2 - gen_text_width / 2, y])


def cout_debug(text, line):
    cout_text = debug_font.render(text, True, white)
    screen.blit(cout_text, [0, 15 * (line - 1)])


def get_bullet_name(id):
    if id == 1:
        return "pistol"
    elif id == 2:
        return "pistol"


def get_weapon_info(id, purpose):
    type = 1
    name = ""
    max_bullet = 200
    shot_delay = 5
    bullet_countdown = 50
    bullet_speed = 20
    bullet_w, bullet_h = 0, 0
    dmg = 0
    limit = 0
    if id == 1:
        type = 1
        name = "pistol"
        max_bullet = 50
        shot_delay = 100
        bullet_countdown = 75
        bullet_speed = 20
        bullet_w, bullet_h = 10, 20
        dmg = 10
        limit = -1
    elif id == 2:
        type = 1
        name = "lazer"
        max_bullet = 100000000
        shot_delay = 0
        bullet_countdown = -1
        bullet_speed = 0
        bullet_w, bullet_h = 10, 20
        dmg = 100
        limit = 100

    if purpose == "type":
        return type
    elif purpose == "name":
        return name
    elif purpose == "max_bullet":
        return max_bullet
    elif purpose == "shot_delay":
        return shot_delay
    elif purpose == "bullet_countdown":
        return bullet_countdown
    elif purpose == "bullet_speed":
        return bullet_speed
    elif purpose == "w,h":
        return [bullet_w, bullet_h]
    elif purpose == "dmg":
        return dmg
    elif purpose == "limit":
        return limit


class Wage:
    def __init__(self, wage_num):
        self.need_kill_list = [10, 20]
        self.wage_num = wage_num
        self.enemy_spawn_delay = 0
        self.enemy_spawn_per = 0
        self.enemy_shot_delay = 0
        self.asteroid_shot_delay = 0
        self.total_ship = 0
        self.total_asteroid = 0

    def update(self):
        self.wage_num = player.ingame_wage
        self.enemy_spawn_delay = 1500 / self.wage_num
        self.enemy_spawn_per = 5 * self.wage_num
        self.enemy_shot_delay = 2000 / self.wage_num
        self.asteroid_shot_delay = 10000
        self.total_asteroid = self.wage_num * 30
        self.total_ship = self.wage_num * 10


class Mine(pygame.sprite.Sprite):
    def __init__(self, x, y, health, head_health):

        pygame.sprite.Sprite.__init__(self)

        self.inventory_point = 0
        self.image = pygame.image.load("./asset/player/main.png")
        self.transform = pygame.transform.scale(self.image, (100, 90))
        self.rect = self.transform.get_rect()
        self.rect.center = [x, y]

        self.max_health = health
        self.ingame_health = health

        self.head_ingame_health = head_health
        self.head_max_health = head_health

        self.regen_box = 10
        self.regen_health = int(self.max_health / 5)

        self.ingame_score = 0
        self.ingame_wage = 1
        self.ingame_kill = 0

        self.bullet_list = [(1, 1, 200), (2, 2, -1)]
        self.bullet_use = self.bullet_list[self.inventory_point]
        self.bullet_type = self.bullet_use[0]
        self.bullet_id = self.bullet_use[1]
        self.bullet_name = ""
        self.ingame_bullet = self.bullet_use[2]
        self.max_bullet = 0
        self.shot_delay = 0
        self.bullet_countdown = 0
        self.bullet_speed = 0
        self.last_shoot = pygame.time.get_ticks()
        self.countdown_reload = False
        self.countdown_time = 0
        self.bullet_size = [0, 0]
        self.bullet_dmg = 0
        self.bullet_limit = 0

    def update(self, player_cursor_x, player_cursor_y):

        self.bullet_use = self.bullet_list[self.inventory_point]
        self.bullet_use = self.bullet_list[self.inventory_point]
        self.bullet_type = self.bullet_use[0]
        self.bullet_id = self.bullet_use[1]

        self.bullet_name = get_weapon_info(self.bullet_type, "name")
        self.max_bullet = get_weapon_info(self.bullet_type, "max_bullet")
        self.shot_delay = get_weapon_info(self.bullet_type, "shot_delay")
        self.bullet_countdown = get_weapon_info(self.bullet_type, "bullet_countdown")
        self.bullet_speed = get_weapon_info(self.bullet_type, "bullet_speed")
        self.bullet_size = get_weapon_info(self.bullet_type, "w,h")
        self.bullet_dmg = get_weapon_info(self.bullet_type, "dmg")
        self.bullet_limit = get_weapon_info(self.bullet_type, "limit")
        self.transform = pygame.transform.scale(self.image, (self.bullet_size[0], self.bullet_size[1]))
        # print(f"{self.bullet_id} - {self.bullet_name} - {self.max_bullet} - {self.shot_delay} - {
        # self.bullet_countdown} - {self.bullet_speed} - {self.bullet_size}")

        # CURRENT TIME
        current = pygame.time.get_ticks()

        # HEALTH CONTROL
        if self.ingame_health > self.max_health:
            self.ingame_health = self.max_health
        elif self.ingame_health < 0:
            self.ingame_health = 0

        # BULLET CONTROL
        if self.ingame_bullet > self.max_bullet:
            self.ingame_bullet = self.max_bullet
        elif self.ingame_bullet < 0:
            self.ingame_bullet = 0

        #        YOUR SPACESHIP
        # screen.blit(self.image, [player_cursor_x, player_cursor_y])

        key = pygame.key.get_pressed()

        # DEBUG
        if debug:

            if key[pygame.K_LEFT]:
                self.ingame_health -= 1
            if key[pygame.K_RIGHT]:
                self.ingame_health += 1
            if key[pygame.K_DOWN]:
                self.ingame_bullet -= 1
            if key[pygame.K_UP]:
                self.ingame_bullet += 1

        # print(str(self.inventory_point) + " " + str(self.bullet_use))

        #     INVENTORY CONTROL
        # if key[pygame.K_1]:
        #     self.inventory_point = 0
        # elif key[pygame.K_2]:
        #     self.inventory_point = 1
        # elif key[pygame.K_3] and len(self.bullet_list) <= 3:
        #     self.inventory_point = 2
        # elif key[pygame.K_4] and len(self.bullet_list) <= 4:
        #     self.inventory_point = 3
        # elif key[pygame.K_5] and len(self.bullet_list) <= 5:
        #     self.inventory_point = 4

        #     SHOOT:
        if pygame.mouse.get_pressed() == (
                1, 0, 0) and current - self.last_shoot > self.shot_delay and self.ingame_bullet > 0:
            bullet = Player_Bullet(self.rect.centerx, self.rect.top, self.bullet_name, self.bullet_id,
                                   self.bullet_speed, self.bullet_name, self.bullet_size[0], self.bullet_size[1],
                                   self.bullet_dmg)
            bullet_gr.add(bullet)
            self.last_shoot = current
            self.ingame_bullet -= 1

        if game_state == "ingame" and not lost:
            self.rect.x = player_cursor_x
            self.rect.y = player_cursor_y
        if lost:
            self.rect.y += 3

        if self.ingame_bullet == 0 and not self.countdown_reload:
            self.countdown_time = self.bullet_countdown
            self.countdown_reload = True

        if self.countdown_reload:
            if self.countdown_time > 0:
                self.countdown_time -= 1
            elif self.countdown_time == 0:
                self.ingame_bullet = self.max_bullet
                self.countdown_reload = False

        if self.ingame_health <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery + 5, 3)
            explosion_gr.add(explosion)
            self.kill()

    def update_head(self, purpose, value):
        if purpose == "hurt":
            self.head_ingame_health -= value

    def bar(self):
        #   BAR:
        #   HEALtTH BAR (top left)
        #     pygame.draw.rect(screen, (0,0,0) , [15,15,290,71])
        if self.bullet_limit == -1:
            bullet_limit_text = float("inf")
        else:
            bullet_limit_text = str(self.bullet_limit)
        print_screen(str(self.bullet_name), white, 23, 15, 15)
        print_screen(f"{bullet_limit_text} {self.ingame_bullet}", white, 20, 15, 37)

        screen.blit(ingame_equipment, [15, h - 85 - 15])
        screen.blit(ingame_inventory, [w - 15 - 275, h - 85 - 15])

        #     MAIN SHIP BAR:
        pygame.draw.rect(screen, black, [w / 2 - 200, h - 37, 400, 17])
        pygame.draw.rect(screen, (211, 115, 6),
                         [w / 2 - 200, h - 37, int(400 * (self.head_ingame_health / self.head_max_health)), 17])
        print_screen_center(f"Main Base: {self.head_ingame_health} / {self.head_max_health}", white, 14, h - 36)

        #     HEALTH BAR:
        pygame.draw.rect(screen, black, [w / 2 - 200, h - 59, 400, 17])
        pygame.draw.rect(screen, (4, 169, 158),
                         [w / 2 - 200, h - 59, int(400 * (self.ingame_health / self.max_health)), 17])
        print_screen_center("Health {}/{}".format(self.ingame_health, self.max_health), white, 14, h - 58)

    def wage(self):
        wage_text = "wage {}".format(str(self.ingame_wage))
        print_screen_left(wage_text, white, 25, 13)

    def score(self, purpose):
        if purpose == "run":
            self.ingame_score += 0.5
        else:
            print_screen_left(str(int(self.ingame_score)).rjust(9, "0"), white, 23, 39)

    def ikill(self):
        print_screen_left(f"Kill: {self.ingame_kill}", white, 18, 63)

    def regen(self, purpose):
        if purpose == "print":
            print_screen(str(self.regen_box), white, 20, 82.25, 696)
        elif purpose == "regen":
            if self.regen_box > 0 and self.ingame_health < self.max_health:
                self.regen_box -= 1
                self.ingame_health += self.regen_health

    def inventory_bar(self):
        for location in range(4):
            if len(self.bullet_list) - 1 >= location >= 0:
                info = self.bullet_list[location]
                x = 0
                y = 0
                dir_name = get_bullet_name(info[0])
                dir_id = info[1]
                image_render = pygame.image.load(f"./asset/inventory/{dir_name}/{dir_id}.png")
                y = h - 78
                if location == 0:
                    x = w - 290
                elif location == 1:
                    x = w - (1200 - 963.95)
                elif location == 2:
                    x = w - (1200 - 1018)
                elif location == 3:
                    x = w - (1200 - 1072.4)
                elif location == 4:
                    x = w - (1200 - 1126)
                screen.blit(image_render, [x, y])


player = Mine(default_player_coord[0], default_player_coord[1], 100, 1000)
wage = Wage(player.ingame_wage)


class Player_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, name, id, speed, type, bullet_w, bullet_h, dmg):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.coord = [x, y]
        self.asset_dir = "./asset/bullet/" + name + "/" + str(self.id) + ".png"
        self.size = (bullet_w, bullet_h)
        self.image_norender = pygame.image.load(self.asset_dir)
        self.image = pygame.transform.scale(self.image_norender, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.bullet_speed = speed
        self.name = type
        self.dmg = dmg

    def update(self):
        self.rect.y -= self.bullet_speed
        if self.rect.bottom < 0:
            self.kill()

        attack_list = pygame.sprite.spritecollide(self, enemy_gr, False)

        if attack_list:
            enemy_heart_list.append(attack_list[0])
            attack_list[0].ingame_health -= self.dmg
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 1)
            explosion_gr.add(explosion)
            if attack_list[0].ingame_health <= 0:
                player.ingame_kill += 1
            self.kill()


def cursor(player_cursor_x, player_cursor_y):
    game_display.blit(cur_img, [player_cursor_x, player_cursor_y])


def get_dmg_wage(max_health, wage_num):
    if wage_num % 3 == 0:
        return max_health / int(wage_num / 3 + 1)


enemy_heart_list = []


def print_enemy_heart():
    length = len(enemy_heart_list) - 1
    i = 0
    while i <= length:
        if not enemy_heart_list[i].alive():
            del enemy_heart_list[i]
            i -= 1
            length -= 1
        i += 1
    if len(enemy_heart_list):
        self = enemy_heart_list[len(enemy_heart_list) - 1]
        pygame.draw.rect(screen, (0, 0, 0), [15, 91, 264, 17])
        pygame.draw.rect(screen, (209, 0, 0), [15, 91, int(264 * (self.ingame_health / self.max_health)), 17])
        health_text_render = health_font.render("{} {}/{}".format(self.name, self.ingame_health, self.max_health), True,
                                                white)
        screen.blit(health_text_render, [15, 69])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, type, x, y, speed, direction, health):
        pygame.sprite.Sprite.__init__(self)
        self.id = random.randint(1, 4)
        self.image = pygame.image.load("./asset/enemy/" + str(self.id) + ".png")
        self.rect = self.image.get_rect()
        self.name = type
        self.rect.center = [x, y]
        self.enemy_speed = speed
        self.direction = direction
        self.ingame_health = health
        self.max_health = health

    def update(self):
        # if self.id
        if self.id != 3:
            self.rect.y += self.enemy_speed
        else:
            self.rect.y += self.enemy_speed * 2
            if self.rect.y < player.rect.y:
                if self.rect.x < player.rect.x:
                    self.rect.x += self.enemy_speed / 2
                elif self.rect.x > player.rect.x:
                    self.rect.x -= self.enemy_speed / 2

        if pygame.sprite.spritecollide(self, player_gr, False, pygame.sprite.collide_mask):
            self.kill()
            # reduce spaceship health
            player.ingame_health -= int(player.max_health / 5)
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_gr.add(explosion)

        # pygame.sprite.spritecollide(self, enemy_gr, True)

        if self.rect.top > h:
            self.kill()
            player.head_ingame_health -= int(player.head_max_health / 200)
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 2)
            explosion_gr.add(explosion)

        # if pygame.sprite.spritecollide(self, bullet_gr, True):
        #     self.ingame_health -= damage_list[0]
        #     print(f"Enemy has been attacked:  {self.ingame_health} / {self.max_health } -{damage_list[0]}")
        #     damage_list[0] = 0

        if self.ingame_health <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_gr.add(explosion)
        #   BAR:
        #   HEALTTH BAR (top left)
        #     pygame.draw.rect(screen, (0,0,0) , [15,15,290,71])


class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, name, id, speed):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.coord = [x, y]
        self.size = get_weapon_info(id, "w,h")
        self.asset_dir = "./asset/bullet/" + name + "/" + str(self.id) + ".png"
        self.image_norender = pygame.image.load(self.asset_dir)
        self.image = pygame.transform.scale(self.image_norender, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.bullet_speed = speed

    def update(self):
        self.rect.y += self.bullet_speed
        if self.rect.top > h:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 1)
            explosion_gr.add(explosion)

        if pygame.sprite.spritecollide(self, player_gr, False, pygame.sprite.collide_mask):
            self.kill()
            vir.append(1)
            player.ingame_health -= int(player.max_health / 20)
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 2)
            explosion_gr.add(explosion)


# create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 4):
            img = pygame.image.load(f"./asset/effect/explode/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (80, 80))
            # add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # UPDATE ANIMATION
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # DELETE EFFECT
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


def enemy_gen(random_x, x, random_y, y):
    # if player.ingame_kill < 10:
    if random_x:
        x = int(round(random.randint(1, int(w / 80) - 1) * 80))
    if random_y:
        y = int(round(random.randint(1, int(h / 50) - 1) * 80))

    enemy = Enemy("Normal Ship", x, y, 2, "follow_y", 20)
    enemy_gr.add(enemy)


class Notification(pygame.sprite.Sprite):
    def __init__(self, text, ):
        pygame.sprite.Sprite.__init__(self)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, as_w, as_h, angle):
        pygame.sprite.Sprite.__init__(self)
        self.id = random.randint(1, 22)
        self.x = random.randint(0, w)
        self.y = -100
        self.asset_dir = "./asset/asteroid/" + str(self.id) + ".png"
        self.image = pygame.image.load(self.asset_dir)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]
        self.angle = angle
        self.ast = [as_w, as_h]

    def update(self):
        if self.angle == "cross":
            self.rect.x += random.randint(3, 4)
            self.rect.y += random.randint(3, 4)
        else:
            self.rect.y += 5

        if self.rect.top > h:
            self.kill()

        if pygame.sprite.spritecollide(self, player_gr, False, pygame.sprite.collide_mask):
            self.kill()
            vir.append(1)
            player.ingame_health -= int(player.max_health / 10)
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 2)
            explosion_gr.add(explosion)

        attack_list = pygame.sprite.spritecollide(self, enemy_gr, False)

        if attack_list:
            enemy_heart_list.append(attack_list[0])
            attack_list[0].ingame_health -= 1000
            explosion = Explosion(self.rect.centerx, self.rect.centery - 5, 1)
            explosion_gr.add(explosion)
            self.kill()


class Planet(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.id = random.randint(1, 4)
        self.x = random.randint(0, w)
        self.y = -10 - size
        self.asset_dir = "./asset/planet/" + str(self.id) + ".png"
        self.image_norender = pygame.image.load(self.asset_dir)
        self.size = random.randint(100, size)
        self.image = pygame.transform.scale(self.image_norender, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        self.rect.y = self.rect.y + 1

        if self.rect.top > h:
            self.kill()


bg_coord = [-h, 0]


def print_background():
    for i in range(2):
        if bg_coord[i] == h:
            bg_coord[i] = -h
        else:
            bg_coord[i] += 1
        screen.blit(ingame_bg, [0, bg_coord[i]])


# class Head():
#     def __init__(self):

# GROUP
notification_gr = pygame.sprite.Group()
player_gr = pygame.sprite.Group()
bullet_gr = pygame.sprite.Group()
enemy_gr = pygame.sprite.Group()
enemy_bullet_gr = pygame.sprite.Group()
explosion_gr = pygame.sprite.Group()
asteroid_gr = pygame.sprite.Group()
planet_gr = pygame.sprite.Group()

# Add Group
player_gr.add(player)


def vsync_control(v_sync):
    if v_sync:
        return 60
    else:
        return 1200


def switch(value):
    if value:
        return False
    else:
        return True


def chance(perhundred):
    if 1 == random.randint(1, 100 / perhundred):
        return True
    else:
        return False


def screen_layer():
    # SCREEN LAYER
    print_background()
    # background_gr.draw(screen)
    # screen.blit(ingame_bg,[0,0])
    planet_gr.draw(screen)

    bullet_gr.draw(screen)
    enemy_gr.draw(screen)

    player_gr.draw(screen)
    enemy_bullet_gr.draw(screen)
    explosion_gr.draw(screen)
    asteroid_gr.draw(screen)

    player.bar()
    player.wage()
    player.score("print")
    player.ikill()
    player.regen("print")
    player.inventory_bar()

    if enemy_heart_list:
        print_enemy_heart()

    # DEBUG MODE
    if debug:
        cout_debug(
            "Space Invender Remastered (ver {} - {}) - fps: {} (limit: {}) - v_sync: {} - player_bullet: {} - "
            "enemy: {} - enemy_bullet: {} - asteroid: {}".format(
                v_num, v_type, str(round(int(clock.get_fps()))), ingame_fps, v_sync, len(bullet_gr),
                len(enemy_gr), len(enemy_bullet_gr), len(asteroid_gr)), 1)

    if edu:
        print_screen("Education purpose only, some features is hidden and it is not indicative of the final product.",
                     white, 12, 18, h - 17)

    if len(vir) != 0:
        if vir[0] == 1:
            game_display.blit(screen, [1, 1])
            del vir[0]
        else:
            game_display.blit(screen, [0, 0])
    else:
        game_display.blit(screen, [0, 0])


def player_update():
    player.update(player_cursor_x, player_cursor_y)
    player.wage()
    player.score("run")
    player.ikill()


def lost_info_layer(mouse_x, mouse_y):
    print_screen_center("YOU LOSE", white, 100, 104)
    print_screen_center(f"Total Score: {str(int(player.ingame_score))}", white, 30, 323)
    print_screen_center(f"Total Kill: {player.ingame_kill}", white, 30, 364)
    print_screen_center(f"Wage Passed: {player.ingame_wage - 1}", white, 30, 405)
    if w / 2 - 235 / 2 <= mouse_x <= w / 2 + 235 / 2 and 621 <= mouse_y <= 621 + 51:
        screen.blit(quit_game_mention, [483, 621])
        if pygame.mouse.get_pressed() == (1, 0, 0):
            sys.exit()
    else:
        screen.blit(quit_game_normal, [483, 621])


last_enemy_shot = last_asteroid = last_gen = last_asteroid_wage = last_planet = pygame.time.get_ticks()
# SETTING
v_sync = False
ingame_fps = 180

enemy_shot_cooldown = 1000

pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))

player_cursor_x = w / 2
player_cursor_y = h - 100

ship_spawned = 0
asteroid_spawned = 0

needed_asteroid = -1

vir_time = 0

wait_for_show = -1

while True:

    needed_ship = wage.total_ship
    # ENEMY SHOT
    current = pygame.time.get_ticks()
    wage.update()

    if player.ingame_health <= 0:
        lost = True

    if (game_state == "ingame" and not lost) or game_state == "menu" or game_state == "pause" or game_state == "lose":
        player_cursor_x = pygame.mouse.get_pos()[0]
        player_cursor_y = pygame.mouse.get_pos()[1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game_state == "ingame":
                    game_state = "pause"
                elif event.key == pygame.K_ESCAPE and game_state == "pause":
                    game_state = "ingame"
                elif event.key == pygame.K_q and game_state == "lose":
                    sys.exit()

    # HIDE CURSOR

    # ingame_background()
    if game_state == "ingame":
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1 and debug:
                    v_sync = switch(v_sync)
                elif event.key == pygame.K_r:
                    player.regen("regen")
                elif event.key == pygame.K_q and game_state == "lose":
                    sys.exit()
        ingame_fps = vsync_control(v_sync)

        # shoot
        if current - last_enemy_shot > wage.enemy_shot_delay and len(enemy_gr) > 0:
            random_enemy_shot = random.choice(enemy_gr.sprites())
            if random_enemy_shot.id != 3:
                # print(str(random.choice(enemy_gr.sprites())) + " " + str(random_enemy_shot.rect.centerx) + " " + str(random_enemy_shot.rect.bottom))
                enemy_bullet_add = Enemy_Bullet(random_enemy_shot.rect.centerx, random_enemy_shot.rect.bottom, "pistol",
                                                2,
                                                5)
                enemy_bullet_gr.add(enemy_bullet_add)
                last_enemy_shot = current

        # if current - last_asteroid > random.randint(5000, int(wage.asteroid_shot_delay)):
        #     asteroid_add = Asteroid(50, 100, "cross")
        #     asteroid_gr.add(asteroid_add)
        #     last_asteroid = current

        if current - last_gen > random.randint(1000, 2000) and needed_ship >= ship_spawned:
            enemy_gen(True, 0, False, -50)
            ship_spawned += 1
            last_gen = current

        if needed_ship == ship_spawned and needed_ship != 0:
            needed_asteroid = wage.total_asteroid

        if needed_asteroid != -1 and asteroid_spawned < needed_asteroid:
            if current - last_asteroid_wage > random.randint(150, 250):
                asteroid_added = Asteroid(50, 100, "bruh")
                asteroid_gr.add(asteroid_added)
                last_asteroid_wage = current
                asteroid_spawned += 1

        if needed_ship <= ship_spawned and asteroid_spawned >= needed_asteroid != -1:
            player.ingame_wage += 1
            ship_spawned = 0
            asteroid_spawned = 0
            needed_asteroid = -1

        if current - last_planet > random.randint(20000, 30000) and chance(10):
            planet_added = Planet(500)
            planet_gr.add(planet_added)
            ship_spawned += 1
            last_planet = current

        if lost and wait_for_show == -1:
            wait_for_show = 200
        if wait_for_show > 0:
            wait_for_show -= 1
        if wait_for_show == 0:
            game_state = "lose"

        # cprint(f"{ship_spawned} / {needed_ship} - {asteroid_spawned} / {needed_asteroid} ", 'blue')

        # while True:
        #     asteroid_add = Asteroid(10, 20)
        #     asteroid_gr.add(asteroid_add)
        player_update()
        screen_layer()

        planet_gr.update()

        bullet_gr.update()
        enemy_gr.update()

        enemy_bullet_gr.update()
        explosion_gr.update()
        asteroid_gr.update()


    elif game_state == "pause":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen_layer()
        game_display.blit(screen, [0, 0])
        game_display.blit(pause_fade, [0, 0])
        cursor(player_cursor_x, player_cursor_y)
    elif game_state == "menu":
        screen_layer()
        game_display.blit(screen, [0, 0])
        game_display.blit(pause_fade, [0, 0])
        cursor(player_cursor_x, player_cursor_y)
    elif game_state == "lose":

        planet_gr.update()

        bullet_gr.update()
        enemy_gr.update()

        enemy_bullet_gr.update()
        explosion_gr.update()
        asteroid_gr.update()

        screen_layer()
        screen.blit(pause_fade, [0, 0])
        lost_info_layer(player_cursor_x,player_cursor_y)
        game_display.blit(screen, [0, 0])

        cursor(player_cursor_x, player_cursor_y)

    pygame.display.update()

    clock.tick(ingame_fps)

    # print

pygame.quit()
