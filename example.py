 # -*- coding: utf-8 -*
import pygame
import random
import os
#-------------------------------------------------------------------
FPS = 60

#顏色
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)

#長寬
WIDTH = 500
HEIGHT = 600
#-------------------------------------------------------------------

#遊戲初始化及創建視窗
pygame.init()
pygame.mixer.init() #聲音初始化
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("雷電X")
clock = pygame.time.Clock() #建立clock物件

#-------------------------------------------------------------------

#載入圖片
background_img = pygame.image.load(os.path.join("image", "background.jpg")).convert()
player_img = pygame.image.load(os.path.join("image", "airforce.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25,19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join("image", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("image", f"rock{i}.png")).convert())


#爆炸效果
expl_anim = {}
expl_anim["lg"] = []
expl_anim["sm"] = []
expl_anim["player"] = []

for i in range(9):
    #石頭爆炸
    expl_img = pygame.image.load(os.path.join("image", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK) #設定顏色
    expl_anim["lg"].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim["sm"].append(pygame.transform.scale(expl_img, (30, 30)))
    #飛船爆炸
    player_expl_img = pygame.image.load(os.path.join("image", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK) #設定顏色
    expl_anim["player"].append(player_expl_img)

#石頭掉寶
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("image", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("image", "gun.png")).convert()


#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
explore_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "BGM.mp3"))
pygame.mixer.music.set_volume(0.4) #設定音量


#載入計分板
font_name = os.path.join("font.ttf") #載入字體
def draw_text(surf, text, size, x, y): #將文字呈現在畫面上
    font = pygame.font.Font(font_name, size) #創建一個文字物件
    text_surface = font.render(text, True, WHITE) #把文字物件渲染出來 #True代表是使用滑順字體
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


#定義增加石頭的函式
def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)


#載入生命條
def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100) * BAR_LENGTH #生命值百分比
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) #生命條外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT) #填滿生命條外框
    pygame.draw.rect(surf, GREEN, fill_rect) #畫生命條
    pygame.draw.rect(surf, WHITE, outline_rect, 2) #畫外框 #2代表2pixels

#定義飛船生命條
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surf.blit(img, img_rect)

#定義初始畫面
def draw_init():
    screen.blit(background_img, (0,0))
    draw_text(screen, 'X雷電', 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, '← →移動飛船 按空白鍵發射子彈', 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, '按任意鍵開始遊戲!', 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                waiting = False
                return False

#-------------------------------------------------------------------

#飛船物件
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.transform.scale(player_img, (50,38)) #修改圖片大小
        self.image.set_colorkey(BLACK) #將黑色變成透明
        self.rect = self.image.get_rect()
        #self.rect.center = (WIDTH/2, HEIGHT/2) #在畫面正中央
        self.radius = 20 #碰撞的判斷範圍
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius) 
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100 #血量
        self.lives = 3 #生命值
        self.hidden = False #死亡後是否是隱藏狀態
        self.hide_time = 0 #死亡到復活的隱藏時間
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx

        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0

        # 範圍視窗限制範例
        # self.rect.x += 2
        # if self.rect.left > WIDTH:
        #     self.rect.right = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet) #將子彈加入子彈的個別群組
                shoot_sound.play() #音效
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1) #將子彈加入子彈的個別群組
                bullets.add(bullet2)
                shoot_sound.play() #音效

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

#石頭物件
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs) 
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360 #取360 mod才不會超過360度
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center #原先定位的中心點
        self.rect = self.image.get_rect() #對轉動後的圖片做重新定位
        self.rect.center = center #將中心點設定回原本的中心點


    def update(self):
        self.rotate()
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        #若已到達邊邊地區，則重新給予隨機生成
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width) #石頭掉下來的水平位置
            self.rect.y = random.randrange(-100, -40) #石頭掉下來的垂直位置
            self.speedy = random.randrange(2, 10) #垂直速度
            self.speedx = random.randrange(-3, 3) #水平速度


#子彈物件
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK) #將黑色變成透明
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


#爆炸物件
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size #大爆炸或小爆炸
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 #目前更新到第幾張圖片
        self.last_update = pygame.time.get_ticks() #記錄最後一次更新圖片的時間
        self.frame_rate = 50 #至少過多久才更新到下一張圖片(動畫速度)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


#寶物物件
class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#-------------------------------------------------------------------

#將物件打包成一個sprite群組
all_sprites = pygame.sprite.Group()

#分別群組
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()

#加入飛船
player = Player()
all_sprites.add(player)

#加入石頭
for i in range(8):
    new_rock()

#初始化分數
score = 0

#播放音樂
pygame.mixer.music.play(-1) #-1代表無限重複播放

#-------------------------------------------------------------------

#建立遊戲迴圈
show_init = True #顯示初始畫面

running = True

while running:
    if show_init:
        close = draw_init()
        if close:
            break
        #將物件打包成一個sprite群組
        all_sprites = pygame.sprite.Group()
        #分別群組
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        #加入飛船
        player = Player()
        all_sprites.add(player)
        #加入石頭
        for i in range(8):
            new_rock()

        #初始化分數
        score = 0

    clock.tick(FPS) #每秒更新的次數

    #取得input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #更新遊戲
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True) #判斷各個群組有無碰撞(True代表是否要刪掉)
    # hits為一個字典，rocks 和 bullets 分別是 key 和 value

    for hit in hits: #若將一個石頭消滅，則會再補一顆石頭進來
        random.choice(explore_sounds).play() #隨機播放爆炸的聲音
        score += hit.radius #將碰撞到的那顆石頭的半徑加到分數上
        expl = Explosion(hit.rect.center, "lg") #建立爆炸物件
        all_sprites.add(expl)
        if random.random() > 0.95:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    #判斷飛船是否有撞到石頭
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits: #若hits這個list裡面有值
        new_rock()
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, "sm") #建立爆炸物件
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, "player")
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide() #死亡到復活的緩衝時間


    #判斷寶物是否有撞到石頭
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == "gun":
            player.gunup()
            gun_sound.play()
            
    if player.lives == 0 and not(death_expl.alive()):
        show_init = True

    #畫面顯示
    screen.fill(BLACK)
    screen.blit(background_img, (0,0)) #(0,0)代表畫面的左上角
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 7, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH -100, 15)
    pygame.display.update()

pygame.quit() #結束遊戲