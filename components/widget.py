import pygame
import utils.utils as utils
import typing
from utils.constants import Align, EventType, EventParam

pygame.init()

class Widget:
    def __init__(self, x: int, y: int, z: int, visible: bool) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.visible = visible
    def draw(self, _: pygame.surface.Surface) -> None:
        pass
    def set_position(self, x: int = None, y: int = None) -> None:
        if x is not None: self.x = x
        if y is not None: self.y = y
    def set_visible(self, visible: bool) -> None:
        self.visible = visible

class Button(Widget):
    def __init__(self, x=0, y=0, z=0, visible=True, text='', bg_color=(255,255,255), text_color=(0,0,0), anchor=Align.Top_Left, width=0, height=0, font=None, font_size=30, pressed_color:pygame.color.Color=None, disabled_color:pygame.color.Color=None, disabled=False) -> None:
        super().__init__(x, y, z, visible)
        self.is_clicked = False
        self.event_listeners: dict[EventType, typing.Callable[[dict], None]] = {}
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.anchor = anchor
        self.disabled = disabled
        self.pressed_color = pressed_color if pressed_color is not None else bg_color
        self.disabled_color = disabled_color if disabled_color is not None else bg_color

        pos_x, pos_y = utils.align(x, y, width, height, anchor)
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.font = pygame.font.Font(font, font_size)
    def draw(self, screen: pygame.surface.Surface) -> None:
        if not self.visible: return

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.is_clicked:
                self.is_clicked = True
            if pygame.mouse.get_pressed()[0] == 0 and self.is_clicked:
                self.is_clicked = False
                if EventType.Mouse_Touch_End in self.event_listeners:
                    hanlder = self.event_listeners[EventType.Mouse_Touch_End]
                    hanlder({EventParam.x: mouse_pos[0], EventParam.y: mouse_pos[1]})

        pygame.draw.rect(screen, self.disabled_color if self.disabled else self.pressed_color if self.is_clicked else self.bg_color, self.rect)
        pos_x, pos_y = utils.align(self.x, self.y, self.width, self.height, self.anchor)
        text_label = self.font.render(self.text, True, self.text_color)
        screen.blit(text_label, (pos_x + self.width // 2 - text_label.get_size()[0] // 2, pos_y + self.height // 2 - text_label.get_size()[1] // 2))
    def add_event_listener(self, type: EventType, handler: typing.Callable[[dict], None]) -> None:
        self.event_listeners[type] = handler
    def set_position(self, x: int = None, y: int = None) -> None:
        pos_x, pos_y = utils.align(x if x is not None else self.x, y if y is not None else self.y, self.width, self.height, self.anchor)
        self.rect.update(pos_x, pos_y, self.width, self.height, self.anchor)

class Label(Widget):
    def __init__(self, x=0, y=0, z=0, visible=True, text='', text_color=(0,0,0), antialias=True, anchor=Align.Top_Left, font_size=30, font=None) -> None:
        super().__init__(x, y, z, visible)
        self.text = text
        self.text_color = text_color
        self.antialias = antialias
        self.anchor = anchor
        self.font_size = font_size
        self.font = pygame.font.Font(font, font_size)
    def draw(self, screen: pygame.surface.Surface) -> None:
        if not self.visible: return

        text_label = self.font.render(self.text, self.antialias, self.text_color)
        screen.blit(text_label, utils.align(self.x, self.y, text_label.get_size()[0], text_label.get_size()[1], self.anchor))
    def set_text(self, text: str):
        self.text = text

class Animation(Widget):
    def __init__(self, x=0, y=0, z=0, visible=True, sprites: typing.List[str] = [], anchor=Align.Top_Left) -> None:
        super().__init__(x, y, z, visible)
        self.is_running = False
        self.current_sprite = 0
        self.sprites = [pygame.image.load(src) for src in sprites]
        self.speed = 0
        self.anchor = anchor
    def run(self, speed: int) -> None:
        self.is_running = True
        self.speed = speed
    def draw(self, screen: pygame.surface.Surface) -> None:
        if not self.visible: return
        if self.is_running:
            self.current_sprite += self.speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
                self.is_running = False
        image = self.sprites[int(self.current_sprite)]
        screen.blit(image, utils.align(self.x, self.y, image.get_size()[0], image.get_size()[1], self.anchor))
