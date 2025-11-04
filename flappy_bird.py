"""
flappy_bird.py – výuková objektová verze Flappy Bird v Pygame
Stavy: MENU → PLAYING → GAME_OVER
"""

from __future__ import annotations
import os
import sys
import random
from dataclasses import dataclass

import pygame

# ---------------------------------------------------------------------------
# 1) START PYGAME A NASTAVENÍ OKNA
# ---------------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 600, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird – výuková verze")

FPS = 60
CLOCK = pygame.time.Clock()

# ---------------------------------------------------------------------------
# 2) BARVY A FONTY
# ---------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (0, 170, 70)
GOLD = (255, 215, 0)

MAIN_FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 32)

# ---------------------------------------------------------------------------
# 3) KONSTANTY PRO PTÁKA A TRUBKY
# ---------------------------------------------------------------------------
BIRD_START_X = 120
BIRD_START_Y = HEIGHT // 2
GRAVITY = 0.35
FLAP_STRENGTH = -8.5
BIRD_WIDTH = 48
BIRD_HEIGHT = 34

PIPE_WIDTH = 100
PIPE_GAP = 220
PIPE_DISTANCE = 280
PIPE_SPEED = 3.2

# ---------------------------------------------------------------------------
# 4) ASSETY – načtení sprite snímků ptáka
# ---------------------------------------------------------------------------

def _assets_dir() -> str:
    """
    Vrátí cestu k assets/ tak, aby fungovala jak při běhu ze zdrojáku,
    tak i v případě PyInstaller (--onefile) – používá _MEIPASS fallback.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets")

def load_image(name: str, scale_to: tuple[int, int] | None = (BIRD_WIDTH, BIRD_HEIGHT)) -> pygame.Surface:
    path = os.path.join(_assets_dir(), name)
    img = pygame.image.load(path).convert_alpha()
    if scale_to:
        img = pygame.transform.smoothscale(img, scale_to)
    return img

# Očekává se, že v assets/ jsou: bird1.png, bird2.png, bird3.png
BIRD_FRAMES: list[pygame.Surface] = [
    load_image("bird1.png"),
    load_image("bird2.png"),
    load_image("bird3.png"),
]

# ---------------------------------------------------------------------------
# 5) TŘÍDY
# ---------------------------------------------------------------------------

@dataclass
class Bird:
    x: float
    y: float
    velocity: float = 0.0
    frame_index: float = 0.0   # plynulá animace
    frame_speed: float = 0.2   # rychlost přepínání snímků

    def flap(self) -> None:
        self.velocity = FLAP_STRENGTH

    def update(self) -> None:
        self.velocity += GRAVITY
        self.y += self.velocity
        self.frame_index = (self.frame_index + self.frame_speed) % len(BIRD_FRAMES)

    def current_image(self) -> pygame.Surface:
        base = BIRD_FRAMES[int(self.frame_index)]
        # natočení podle rychlosti pro „živější“ dojem
        angle = max(min(-self.velocity * 3, 25), -25)  # omezíme rozsah natočení
        return pygame.transform.rotozoom(base, angle, 1.0)

    def get_rect(self) -> pygame.Rect:
        img = self.current_image()
        r = img.get_rect()
        r.topleft = (int(self.x), int(self.y))
        return r

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.current_image(), (int(self.x), int(self.y)))


@dataclass
class PipePair:
    x: float
    gap_center_y: float
    passed: bool = False

    def top_rect(self) -> pygame.Rect:
        top_height = int(self.gap_center_y - PIPE_GAP / 2)
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, top_height)

    def bottom_rect(self) -> pygame.Rect:
        bottom_y = int(self.gap_center_y + PIPE_GAP / 2)
        height = HEIGHT - bottom_y
        return pygame.Rect(int(self.x), bottom_y, PIPE_WIDTH, height)

    def update(self) -> None:
        self.x -= PIPE_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, GRASS_GREEN, self.top_rect())
        pygame.draw.rect(surface, GRASS_GREEN, self.bottom_rect())

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        return bird_rect.colliderect(self.top_rect()) or bird_rect.colliderect(self.bottom_rect())


# ---------------------------------------------------------------------------
# 6) HERNÍ STAVY A RENDERY
# ---------------------------------------------------------------------------
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"


def draw_background(surface: pygame.Surface) -> None:
    surface.fill(SKY_BLUE)
    pygame.draw.rect(surface, GRASS_GREEN, (0, HEIGHT - 60, WIDTH, 60))


def draw_menu(surface: pygame.Surface) -> None:
    draw_background(surface)
    title = MAIN_FONT.render("Flappy Bird", True, GOLD)
    subtitle = SMALL_FONT.render("Stiskni SPACE pro start", True, BLACK)
    controls = SMALL_FONT.render("Ovládání: SPACE = skoč, ESC = ukončit", True, BLACK)
    surface.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT * 0.25)))
    surface.blit(subtitle, subtitle.get_rect(center=(WIDTH / 2, HEIGHT * 0.45)))
    surface.blit(controls, controls.get_rect(center=(WIDTH / 2, HEIGHT * 0.60)))


def draw_game_over(surface: pygame.Surface, score: int) -> None:
    draw_background(surface)
    title = MAIN_FONT.render("Game Over", True, BLACK)
    score_text = SMALL_FONT.render(f"Skóre: {score}", True, BLACK)
    retry = SMALL_FONT.render("ENTER = hrát znovu, ESC = konec", True, BLACK)
    surface.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT * 0.30)))
    surface.blit(score_text, score_text.get_rect(center=(WIDTH / 2, HEIGHT * 0.50)))
    surface.blit(retry, retry.get_rect(center=(WIDTH / 2, HEIGHT * 0.65)))


def draw_score(surface: pygame.Surface, score: int) -> None:
    text = SMALL_FONT.render(f"Skóre: {score}", True, BLACK)
    surface.blit(text, (20, 20))


# ---------------------------------------------------------------------------
# 7) STARTOVNÍ STAV HRY
# ---------------------------------------------------------------------------
def create_initial_game_state() -> tuple[Bird, list[PipePair], int]:
    bird = Bird(BIRD_START_X, BIRD_START_Y)
    pipes: list[PipePair] = []
    for i in range(3):
        gap_center = random.randint(180, HEIGHT - 180)
        pipe_x = WIDTH + i * PIPE_DISTANCE
        pipes.append(PipePair(pipe_x, gap_center))
    return bird, pipes, 0


# ---------------------------------------------------------------------------
# 8) HLAVNÍ SMYČKA
# ---------------------------------------------------------------------------
def main() -> None:
    state = MENU
    bird, pipes, score = create_initial_game_state()
    running = True

    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state == MENU and event.key == pygame.K_SPACE:
                    state = PLAYING
                    bird, pipes, score = create_initial_game_state()
                elif state == PLAYING and event.key == pygame.K_SPACE:
                    bird.flap()
                elif state == GAME_OVER and event.key == pygame.K_RETURN:
                    state = PLAYING
                    bird, pipes, score = create_initial_game_state()

        if state == MENU:
            draw_menu(WINDOW)
            pygame.display.flip()
            continue

        if state == PLAYING:
            bird.update()

            if pipes[-1].x < WIDTH - PIPE_DISTANCE:
                gap_center = random.randint(180, HEIGHT - 180)
                pipes.append(PipePair(WIDTH, gap_center))

            for pipe in pipes:
                pipe.update()
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1

            pipes = [p for p in pipes if p.x + PIPE_WIDTH > 0]

            bird_rect = bird.get_rect()

            if any(p.collides_with(bird_rect) for p in pipes):
                state = GAME_OVER

            if bird.y <= -BIRD_HEIGHT or bird.y >= HEIGHT - 60:
                state = GAME_OVER

            draw_background(WINDOW)
            for p in pipes:
                p.draw(WINDOW)
            bird.draw(WINDOW)
            draw_score(WINDOW, score)
            pygame.display.flip()
            continue

        if state == GAME_OVER:
            draw_game_over(WINDOW, score)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
