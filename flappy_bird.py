import pygame
import random

pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 1200  , 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird – demo")

# Základní barvy
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)

# Vlastnosti ptáka
bird_x = 80
bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.5
jump_strength = -8

# Trubky
pipe_width = 60
pipe_gap = 300
pipe_speed = 3
pipes = []

clock = pygame.time.Clock()
running = True

def create_pipe():
    """Vytvoří novou dvojici trubek s náhodnou mezerou."""
    gap_y = random.randint(120, HEIGHT - 120)
    top_rect = pygame.Rect(WIDTH, 0, pipe_width, gap_y - pipe_gap // 2)
    bottom_rect = pygame.Rect(WIDTH, gap_y + pipe_gap // 2, pipe_width, HEIGHT)
    pipes.append((top_rect, bottom_rect))

create_pipe()

score = 0
font = pygame.font.SysFont(None, 32)

while running:
    clock.tick(60)  # 60 snímků za vteřinu

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird_velocity = jump_strength  # pták vyskočí nahoru

    # Fyzika ptáka
    bird_velocity += gravity
    bird_y += bird_velocity

    # Přidávání trubek
    if pipes[-1][0].x < WIDTH - 400:
        create_pipe()

    # Pohyb trubek a sčítání skóre
    for pipe_pair in pipes:
        pipe_pair[0].x -= pipe_speed
        pipe_pair[1].x -= pipe_speed

        if pipe_pair[0].x + pipe_width == bird_x:
            score += 1  # hráč prošel trubkou

    # Detekce kolizí
    bird_rect = pygame.Rect(bird_x, bird_y, 34, 24)
    for pipe_pair in pipes:
        if bird_rect.colliderect(pipe_pair[0]) or bird_rect.colliderect(pipe_pair[1]):
            running = False  # jednoduchý konec hry

    if bird_y > HEIGHT or bird_y < 0:
        running = False

    # Vykreslení
    window.fill(WHITE)
    pygame.draw.rect(window, (255, 200, 0), bird_rect)
    for pipe_pair in pipes:
        pygame.draw.rect(window, GREEN, pipe_pair[0])
        pygame.draw.rect(window, GREEN, pipe_pair[1])

    score_surface = font.render(f"Skóre: {score}", True, (0, 0, 0))
    window.blit(score_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
