import pygame
import typing
import random
import os
import utils.utils as utils
from components.widget import Button, Label, Animation
from components.effect import EffectManager, FireworkEffect, SmokeUpEffect, SmokeCircleEffect, SparkleEffect
from utils.constants import Align, EventType

class Scene:
    def __init__(self) -> None:
        pass
    def handle_events(self, _: pygame.event.Event) -> None:
        pass
    def update(self) -> None:
        pass
    def draw(self, _: pygame.surface.Surface) -> None:
        pass
    def onEnter(self) -> None:
        pass
    def onExit(self) -> None:
        pass

class SceneManager:
    _instance = None

    def __init__(self) -> None:
        SceneManager._instance = self

        self.scenes: typing.List[Scene] = []

    def isEmpty(self) -> bool:
        return len(self.scenes) == 0
    
    def handle_events(self, events: typing.List[pygame.event.Event]) -> None:
        if self.isEmpty(): return
        self.scenes[0].handle_events(events)

    def update(self) -> None:
        if self.isEmpty(): return
        self.scenes[0].update()

    def draw(self, screen: pygame.surface.Surface) -> None:
        if self.isEmpty(): return
        self.scenes[0].draw(screen)

    def push(self, scene: Scene) -> None:
        self.scenes.append(scene)
        scene.onEnter()

    def peek(self) -> None:
        if self.isEmpty(): return
        self.scenes[0].onExit()
        self.scenes.pop(0)

    @staticmethod
    def getInstance() -> 'SceneManager':
        if SceneManager._instance is None:
            SceneManager()
        return SceneManager._instance

class ExampleScene(Scene):
    def __init__(self, scene_manager: SceneManager, color: pygame.color.Color) -> None:
        super().__init__()

        self.scene_manager = scene_manager
        self.effect_manager = EffectManager()
        self.background_color = color
        self.start_btn = Button(x=300, y=300, width=100, height=50, anchor=Align.Mid_Center, text="START", pressed_color=(150, 150, 150))
        self.start_btn.add_event_listener(EventType.Mouse_Touch_End, self.on_start_click)
        self.label = Label(x=300, y=200, text='Hello World!', anchor=Align.Mid_Center)
        sprites = [f'assets/attack_{i}.png' for i in range(1, 11)]
        self.animation = Animation(x=300, y=400, sprites=sprites, anchor=Align.Mid_Center)

    def draw(self, screen: pygame.surface.Surface) -> None:
        screen.fill(self.background_color)
        self.label.draw(screen)
        self.start_btn.draw(screen)
        self.animation.draw(screen)
        self.effect_manager.draw(screen)
        
    def handle_events(self, events: typing.List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.effect_manager.add_effect(SparkleEffect(2, 0.1, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self.scene_manager.pop()
            self.scene_manager.push(ExampleScene(self.scene_manager, (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))))
        elif keys[pygame.K_e]:
            # self.effect_manager.add_effect(FireworkEffect(10, 0.1, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
            # self.effect_manager.add_effect(SmokeEffect(5, 0.1, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
            # self.effect_manager.add_effect(SmokeCircleEffect(4))
            self.effect_manager.add_effect(SparkleEffect(2, 0.1))
            pass
            

    def on_start_click(self, _: dict) -> None:
        self.animation.run(0.2)

class GameScene(Scene):
    START_POSITION = (280, 500)
    PLAYER_DAMAGE = 10
    ENEMY_DAMAGE = 100
    ENEMY_NUMBER = 5
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    class GameObject:
        def __init__(self, x: int, y: int, image: pygame.surface.Surface) -> None:
            self.x = x
            self.y = y
            self.image = image
            self.mask = pygame.mask.from_surface(image)

        def move(self, x, y):
            self.x += x
            self.y += y

        def draw(self, surface: pygame.surface.Surface):
            surface.blit(self.image, (self.x, self.y))

        def update(self):
            pass

        def is_off_screen(self, height: int):
            return self.y < 0 or self.y > height

        def get_mask(self):
            return self.mask
        
        def get_size(self):
            return self.image.get_size()
        
        def is_collide_with(self, obj2: 'GameScene.GameObject'):
            return self.get_mask().overlap(obj2.get_mask(), (obj2.x - self.x, obj2.y - self.y)) != None
    
    class Bullet(GameObject):
        def __init__(self, x: int, y: int, image: pygame.surface.Surface, vel_y: int) -> None:
            super().__init__(x, y, image)
            self.vel_y = vel_y

    class Ship(GameObject):
        COOL_DOWN = 20
        def __init__(self, x: int, y: int, image: pygame.surface.Surface, bullet_vel: int, bullet_img: pygame.surface.Surface, health: int) -> None:
            super().__init__(x, y, image)
            self.bullets: typing.List[GameScene.Bullet] = []
            self.bullet_vel = bullet_vel
            self.cool_down = 0
            self.health = health
            self.bullet_img = bullet_img

        def shoot(self):
            if (self.cool_down < GameScene.Ship.COOL_DOWN): return
            self.cool_down = 0
            self.bullets.append(GameScene.Bullet(self.x, self.y, self.bullet_img, self.bullet_vel))

        def draw(self, surface: pygame.surface.Surface):
            for bullet in self.bullets:
                bullet.draw(surface)

            super().draw(surface)
        
        def update(self, window_height: int):
            self.cool_down += 1
            for bullet in self.bullets:
                bullet.move(0, bullet.vel_y)
                if bullet.is_off_screen(window_height):
                    self.bullets.remove(bullet) 

        def receive_damage(self, damage):
            self.health -= damage

        def is_dead(self) -> bool:
            return self.health <= 0

        def get_health(self) -> int:
            return self.health

    class Player(Ship):
        MAX_HEALTH = 10
        PLAYER_SIZE = (50, 50)
        PLAYER_VEL = 5
        PLAYER_BULLET_VEL = -5
        PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png')), PLAYER_SIZE)
        BULLET_YELLOW = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png')), PLAYER_SIZE)
        def __init__(self, x: int, y: int) -> None:
            super().__init__(x, y, GameScene.Player.PLAYER_SHIP, GameScene.Player.PLAYER_BULLET_VEL, GameScene.Player.BULLET_YELLOW, GameScene.Player.MAX_HEALTH)
            self.lives = 3
            self.score = 0

        def update(self, enemies: typing.List['GameScene.Enemy'], window_height:int, effect_manager: EffectManager):
            super().update(window_height)

            for enemy in enemies:
                if self.is_collide_with(enemy):
                    enemies.remove(enemy)
                    self.receive_damage(GameScene.PLAYER_DAMAGE)
                    effect_manager.add_effect(SmokeCircleEffect(3, self.x, self.y, 15))
                    continue
                
                for bullet in self.bullets:
                    if bullet.is_collide_with(enemy):
                        self.bullets.remove(bullet)
                        enemy.receive_damage(GameScene.ENEMY_DAMAGE)
                        self.score += 10
                        effect_manager.add_effect(SparkleEffect(6, enemy.x + enemy.get_size()[0] // 2, enemy.y + enemy.get_size()[1] // 2))
                        break

            if self.is_dead():
                self.lives -= 1
                if not self.is_end(): self.health = GameScene.Player.MAX_HEALTH
        
        def get_lives(self) -> int:
            return self.lives

        def is_end(self) -> bool:
            return self.lives < 1
        
        def move(self, x, y, window_width, window_height):
            if self.x + x < window_width - self.image.get_size()[0] and self.x + x > 0:
                self.x += x
            if self.y + y < window_height - self.image.get_size()[1] and self.y + y > 0:
                self.y += y

    class Enemy(Ship):
        MAX_HEALTH = 100
        ENEMY_SIZE = (40, 40)
        ENEMY_BULLET_VEL = 5
        ENEMY_VEL = 1
        BULLET_BLUE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png')), ENEMY_SIZE)
        BULLET_GREEN = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_laser_green.png')), ENEMY_SIZE)
        BULLET_RED = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_laser_red.png')), ENEMY_SIZE)
        ENEMY_GREEN = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png')), ENEMY_SIZE)
        ENEMY_BLUE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png')), ENEMY_SIZE)
        ENEMY_RED = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png')), ENEMY_SIZE)
        COLOR_MAP = {
            'red': (ENEMY_RED, BULLET_RED),
            'green': (ENEMY_GREEN, BULLET_GREEN),
            'blue': (ENEMY_BLUE, BULLET_BLUE)
        }
        def __init__(self, x: int, y: int, color: str) -> None:
            super().__init__(x, y, GameScene.Enemy.COLOR_MAP[color][0], GameScene.Enemy.ENEMY_BULLET_VEL, GameScene.Enemy.COLOR_MAP[color][1], GameScene.Enemy.MAX_HEALTH)

        def update(self, player: 'GameScene.Player', window_height:int):
            super().update(window_height)

            self.move(0, GameScene.Enemy.ENEMY_VEL)
            
            if random.randrange(0, 2 * 60) == 1:
                self.shoot()

            for bullet in self.bullets:
                if bullet.is_collide_with(player):
                    self.bullets.remove(bullet)
                    player.receive_damage(GameScene.PLAYER_DAMAGE)

        def is_reach_goal(self, HEIGHT):
            return self.y > HEIGHT
            
    def __init__(self, scene_manager: SceneManager) -> None:
        self.player = GameScene.Player(GameScene.START_POSITION[0], GameScene.START_POSITION[1])
        self.window_width = GameScene.WINDOW_WIDTH
        self.window_height = GameScene.WINDOW_HEIGHT
        self.enemies: typing.List[GameScene.Enemy] = list()
        self.img_bg = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (GameScene.WINDOW_WIDTH, GameScene.WINDOW_HEIGHT))
        self.live_label = Label(x=10, y=10, text='', text_color=(255,255,255))
        self.health_label = Label(x=10, y=30, text='', text_color=(255,255,255))
        self.end_game_label = Label(x=250, y=250, text='You Lose!', text_color=(255,255,255))
        self.end_game_label.set_visible(False)
        self.score_label = Label(x=550,y=10, text_color=(255,255,255), anchor=Align.Top_Right)
        self.level = 0
        self.enemies_number = 0
        self.effect_manager = EffectManager()
        self.lost_count = 0
        self.is_running = True
        self.scene_manager = scene_manager
        self.btn_back = Button(x=300, y=300, width=150, height=40, pressed_color=(50,50,50), text='Back', anchor=Align.Mid_Center)
        self.btn_back.set_visible(False)
        self.btn_back.add_event_listener(EventType.Mouse_Touch_End, self.on_back)

    def handle_events(self, _: typing.List[pygame.event.Event]) -> None:
        if not self.is_running: return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.move(-GameScene.Player.PLAYER_VEL, 0, self.window_width, self.window_height)
        elif keys[pygame.K_RIGHT]:
            self.player.move(GameScene.Player.PLAYER_VEL, 0, self.window_width, self.window_height)
        elif keys[pygame.K_UP]:
            self.player.move(0, -GameScene.Player.PLAYER_VEL, self.window_width, self.window_height)
        elif keys[pygame.K_DOWN]:
            self.player.move(0, GameScene.Player.PLAYER_VEL, self.window_width, self.window_height)

        if keys[pygame.K_SPACE]:
            self.player.shoot()

    def update(self) -> None:
        self.live_label.set_text(f'Live: {self.player.lives}')
        self.health_label.set_text(f'Health: {self.player.health}')
        self.score_label.set_text(f'Score: {self.player.score}')

        if self.player.is_end():
            self.is_running = False
            self.end_game_label.set_visible(True)
            self.btn_back.set_visible(True)
    
        if not self.is_running: return

        if len(self.enemies) == 0:
            self.level += 1
            self.enemies_number += GameScene.ENEMY_NUMBER
            for _ in range(self.enemies_number):
                enemy = GameScene.Enemy(random.randrange(50, self.window_width - 100), random.randrange(-500, -50), random.choice(['red', 'green', 'blue']))
                self.enemies.append(enemy)

        self.player.update(self.enemies, self.window_height, self.effect_manager)
        for enemy in self.enemies:
            if enemy.is_reach_goal(self.window_height) or enemy.is_dead():
                self.enemies.remove(enemy)
                if enemy.is_reach_goal(self.window_height): self.player.receive_damage(GameScene.PLAYER_DAMAGE)
            else:
                enemy.update(self.player, self.window_height)

    def draw(self, screen: pygame.surface.Surface) -> None:
        screen.blit(self.img_bg, (0, 0))
        self.live_label.draw(screen)
        self.health_label.draw(screen)
        self.score_label.draw(screen)
        self.player.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.effect_manager.draw(screen)
        self.end_game_label.draw(screen)
        self.btn_back.draw(screen)
        
    def onEnter(self) -> None:
        pass
    def onExit(self) -> None:
        pass

    def on_back(self, _) -> None:
        self.scene_manager.push(StartScene(self.scene_manager))
        self.scene_manager.peek()

class StartScene(Scene):
    def __init__(self, scene_manager: SceneManager) -> None:
        self.scene_manager = scene_manager
        self.btn_start = Button(x=300, y=300, width=100, height=50, text='Start', pressed_color=(50,50,50), anchor=Align.Mid_Center)
        self.btn_start.add_event_listener(EventType.Mouse_Touch_End, self.on_start_game)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0,0,0))
        self.btn_start.draw(screen)

    def on_start_game(self, _) -> None:
        self.scene_manager.push(GameScene(self.scene_manager))
        self.scene_manager.peek()