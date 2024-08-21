import math
import pygame

from spritesheet import Spritesheet


now_count = 0
GAME_OVER = False
GAME_END = False
START_MENU = True
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


def main():
    global START_MENU
    global now_count
    global GAME_OVER
    global GAME_END

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Kitty Go Home")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_icon(pygame.image.load('assets/icon.png'))

    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.health = 3
            self.x = x
            self.y = y
            self.do_jump = False
            self.running = False
            self.damage = False

            spritesheet = Spritesheet("assets/kitty_run.png", (675, 668), scale=0.25)
            self.run_spritesheet = spritesheet.get_sprites([(0, x) for x in range(4)])
            spritesheet = Spritesheet("assets/kitty_idle.png", (600, 702), scale=0.25)
            self.idle_spritesheet = spritesheet.get_sprites([(0, x) for x in range(4)])
            spritesheet = Spritesheet("assets/damage.png", (675, 668), scale=0.25)
            self.damage_spritesheet = spritesheet.get_sprites([(0, x) for x in range(1)])

            self.spritesheet = self.idle_spritesheet
            self.index = 0  # для смены кадров
            self.image = self.spritesheet[self.index]  # нынешняя картинка
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)

            self.run_timing = 0
            self.jump_timing = 0
            self.game_over_timing = 0
            self.damage_timing = 0

            self.alive = True

        def change_animation(self):
            self.running = not self.running
            if self.running:
                self.spritesheet = self.run_spritesheet
            else:
                self.spritesheet = self.idle_spritesheet

            self.index = 0
            self.run_timing = 0

        def update(self):
            self.rect.topleft = self.x, self.y
            if self.damage:
                self.damage_timing += 1
                self.image = self.damage_spritesheet[0]
                if self.damage_timing >= 15:
                    self.damage = False
                    self.damage_timing = 0
            elif self.alive:
                self.run_timing += 1
                if self.run_timing >= 15:
                    self.run_timing = 0
                    self.index += 1
                    if self.index >= len(self.spritesheet):
                        self.index = 0
                    self.image = self.spritesheet[self.index]

                if self.do_jump:
                    self.jump_timing += 1
                    if self.jump_timing <= 40:
                        self.y -= 6
                    elif self.jump_timing > 85:
                        self.jump_timing = 0
                        self.do_jump = False
                    elif self.jump_timing > 45:
                        self.y += 6
            else:
                self.y -= 1

            if self.health <= 0:
                self.kill()
                self.game_over_timing += 1
                if self.game_over_timing >= 200:
                    global GAME_OVER
                    GAME_OVER = True

        def kill(self):
            self.alive = False
            spritesheet = Spritesheet('assets/death.png', (675, 668), scale=0.3)
            self.image = spritesheet.get_sprite((0, 0))

    class Dog(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.x = x
            self.y = y
            self.running = False

            spritesheet = Spritesheet("assets/dog_run.png", (900, 696), scale=0.5)
            self.run_spritesheet = spritesheet.get_sprites([(0, x) for x in range(3)])
            spritesheet = Spritesheet("assets/dog_idle.png", (900, 696), scale=0.5)
            self.idle_spritesheet = spritesheet.get_sprites([(0, x) for x in range(3)])

            self.spritesheet = self.idle_spritesheet
            self.index = 0  # для смены кадров
            self.image = self.spritesheet[self.index]  # нынешняя картинка
            self.rect = self.image.get_rect()

            self.run_timing = 0

        def change_animation(self):
            self.running = not self.running
            if self.running:
                self.spritesheet = self.run_spritesheet
            else:
                self.spritesheet = self.idle_spritesheet

            self.index = 0
            self.run_timing = 0

        def update(self):
            if self.running:
                self.x += 6

            self.rect.x = self.x
            self.rect.y = self.y
            if self.x <= -500:
                self.kill()
            self.run_timing += 1
            if self.run_timing >= 15:
                self.run_timing = 0
                self.index += 1
                if self.index >= len(self.spritesheet):
                    self.index = 0
                self.image = self.spritesheet[self.index]

    # кол-во косточек
    need_count = 3

    bone_image = pygame.image.load('assets/bone.png')
    bone_image = pygame.transform.scale(bone_image, (80, 40))
    bone_image = pygame.transform.rotate(bone_image, 32)

    heart_image = pygame.image.load('assets/heart.png')
    heart_image = pygame.transform.scale(heart_image, (70, 70))

    class NewObject(pygame.sprite.Sprite):
        def __init__(self, x, y, image, scale):
            super().__init__()
            self.x = x
            self.y = y
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            self.mask = pygame.mask.from_surface(self.image)
            self.pick_up = False
            self.pick_up_timer = 0

        def update(self):
            self.rect.x = self.x
            self.rect.y = self.y
            if self.x <= -500:
                self.kill()

            if self.pick_up:
                self.pick_up_timer += 1
                self.y -= 5
                if self.pick_up_timer >= 60:
                    self.kill()
                    global now_count
                    now_count += 1

    # длина карты, при её пересечении происходит победа
    map_len = SCREEN_WIDTH + 7500

    # игрок
    player = Player(100, 550)
    player_group = pygame.sprite.Group(player)
    # кустики
    bush_file = 'assets/red_bush.png'
    bush_scale = (200, 100)
    bushes = [
        NewObject(SCREEN_WIDTH + 100, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 900, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 1500, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 2000, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 2800, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 3700, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 4200, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 4700, 610, bush_file, bush_scale),
        NewObject(SCREEN_WIDTH + 5600, 610, bush_file, bush_scale),
    ]

    # кости
    bone_file = 'assets/bone.png'
    bone_scale = (75, 30)
    bones = [
        NewObject(SCREEN_WIDTH + 1790, 680, bone_file, bone_scale),
        NewObject(SCREEN_WIDTH + 3050, 680, bone_file, bone_scale),
        NewObject(SCREEN_WIDTH + 5500, 680, bone_file, bone_scale),
    ]

    # собака
    dog = Dog(SCREEN_WIDTH + 6800, 400)
    dog_group = pygame.sprite.Group(dog)

    # все объекты
    objects_group = pygame.sprite.Group()
    objects_group.add(bushes)
    objects_group.add(bones)
    objects_group.add(dog)

    # фоновое изображение
    background = pygame.image.load('assets/background.jpg').convert()
    ratio = background.get_height() / SCREEN_HEIGHT
    background = pygame.transform.scale(background, (background.get_width() / ratio, SCREEN_HEIGHT))

    #Белый фон для меню
    white_background = pygame.image.load('assets/white_background.png').convert()

    # нужны для движения фона
    scroll = -1000
    tiles = math.ceil(SCREEN_WIDTH  / background.get_width()) + 1

    # считает тики в игре, чтобы некоторые события зависели от времени, а не FPS в игре
    # по большей части это нужно для движения фона
    clock = pygame.time.Clock()

    # шрифт
    font = pygame.font.SysFont('Comic Sans MS', 60)

    immunitet_bushes = []

    # проверка затрагивания кустика
    def check_touch_bush():
        for b in bushes:
            is_touch = pygame.sprite.collide_mask(player, b)

            if is_touch:
                if b not in immunitet_bushes:
                    immunitet_bushes.append(b)
                    player.health -= 1
                    player.damage = True

    # проверка на взятие косточки
    def check_pickup_bone():
        pick_up_bones = pygame.sprite.spritecollide(player, bones, False, collided=None)
        for b in pick_up_bones:
            b.pick_up = True
            # global now_count
            # now_count += 1

    # взаимодействие с собакой
    def check_dog():
        if dog.x <= player.x and not dog.running:
            if now_count == need_count:
                dog.change_animation()
            else:
                player.health = 0

    # конец игры
    def check_end():
        if player.x >= map_len:
            global GAME_END
            GAME_END = True

    # отобразить базовую часть меню
    def blit_menu():
        screen.blit(white_background, (0, 0))
        font = pygame.font.SysFont('Comic Sans MS', 25)
        text = font.render("prod. Пасторова Анна 2-мв-5", False, (0, 0, 0))
        screen.blit(text, (SCREEN_WIDTH - text.get_width() - 60, SCREEN_HEIGHT - text.get_height() - 50))
        screen.blit(
            pygame.transform.scale(pygame.image.load('assets/end_kitty.png'), (345, 300)),
            (-50, SCREEN_HEIGHT - 250)
        )

        image = pygame.image.load('assets/logo.png')
        screen.blit(
            pygame.transform.scale(image, (587, 148)),
            (SCREEN_WIDTH // 2 - image.get_width() // 2, SCREEN_HEIGHT // 2 - image.get_height())
        )

    # Основной цикл игры
    running = True
    while running:
        clock.tick(60)

        # упавление
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.change_animation()
                if event.key == pygame.K_DOWN:
                    pass
                if event.key == pygame.K_UP:
                    player.do_jump = True

                if event.key == pygame.K_r and (not player.alive or GAME_END):
                    now_count = 0
                    GAME_OVER = False
                    GAME_END = False
                    main()
                    running = False

                if event.key == pygame.K_SPACE:
                    START_MENU = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.change_animation()

        # ОТРИСОВКИ
        # старт меню
        if START_MENU:
            blit_menu()
            font_start = pygame.font.SysFont('Comic Sans MS', 35, bold=True)
            text = font_start.render(
                'Нажмите ПРОБЕЛ', False, (243, 139, 79)
            )
            screen.blit(
                text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                       SCREEN_HEIGHT // 2 - text.get_height() // 2 + 50)
            )

        # меню проигрыша
        elif GAME_OVER:
            blit_menu()
            font = pygame.font.SysFont('Comic Sans MS', 35, bold=True)
            for i, t in enumerate(['У тебя закончились силы, ты не смог добраться', 'до деревни и умер']):
                game_over = font.render(t, False, (0, 0, 0))
                screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 50 * (i + 1)))

            font = pygame.font.SysFont('Comic Sans MS', 30)
            text = font.render(
                'Нажмите "R", чтобы начать заново', False, (0, 0, 0)
                )
            screen.blit(
                text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                       SCREEN_HEIGHT // 2 - text.get_height() // 2 + 50)
                )

        # меню победы
        elif GAME_END:
            # изображенеи конца игры
            end_background = pygame.image.load('assets/end_background.jpg').convert()
            screen.blit(end_background, (0, 0))
            font = pygame.font.SysFont('Comic Sans MS', 35, bold=True)
            for i, t in enumerate(['Твой друг - собака помог тебе добраться до деревни.', 'Ты выжил!']):
                game_over = font.render(t, False, (0, 0, 0))
                screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 50 * (i + 1)))
            image = pygame.image.load('assets/end_kitty.png')
            screen.blit(
                pygame.transform.scale(image, (image.get_width()*0.7, image.get_height()*0.7)),
                (10, SCREEN_HEIGHT - image.get_height()*0.7)
            )

        # основная игра
        else:
            # код для движения фона
            i = 0
            while i < tiles:
                screen.blit(background, (background.get_width()*i + scroll, 0))
                i += 1
            if abs(scroll) > background.get_width():
                scroll = 0
            if player.running and player.alive:
                scroll -= 6
                for obj in objects_group:
                    obj.x -= 6
                map_len -= 6

            check_pickup_bone()
            check_touch_bush()
            check_dog()
            check_end()
            player_group.update()
            objects_group.update()
            player_group.draw(screen)
            objects_group.draw(screen)

            bones_count = font.render(f'{now_count}/{need_count}', False, (255, 255, 255))
            hp = font.render(f' {player.health}', False, (255, 255, 255))
            screen.blit(bones_count, (SCREEN_WIDTH - 120, 0))
            screen.blit(hp, (100, 0))
            screen.blit(bone_image, (SCREEN_WIDTH - 220, 5))
            screen.blit(heart_image, (20, 10))

        pygame.display.flip()


main()





