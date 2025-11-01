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
# Trubky budeme ukládat jako slovníky, aby šlo poznat, které už mají započítané skóre
pipes = []

clock = pygame.time.Clock()
running = True

def create_pipe():
    """Vytvoří novou dvojici trubek s náhodnou mezerou."""
    gap_y = random.randint(120, HEIGHT - 120)
    top_rect = pygame.Rect(WIDTH, 0, pipe_width, gap_y - pipe_gap // 2)
    bottom_rect = pygame.Rect(WIDTH, gap_y + pipe_gap // 2, pipe_width, HEIGHT)
    # Každá dvojice trubek dostane příznak 'passed', aby se skóre nepřičítalo opakovaně
    pipes.append({
        "top": top_rect,
        "bottom": bottom_rect,
        "passed": False,
    })

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
    if pipes[-1]["top"].x < WIDTH - 400:
        create_pipe()

    # Pohyb trubek a sčítání skóre
    for pipe_pair in pipes:
        pipe_pair["top"].x -= pipe_speed
        pipe_pair["bottom"].x -= pipe_speed

        # Jakmile pták proletí za trubkou, zvýšíme skóre právě jednou
        pipe_right_edge = pipe_pair["top"].x + pipe_width
        if not pipe_pair["passed"] and pipe_right_edge < bird_x:
            pipe_pair["passed"] = True
            score += 1  # hráč úspěšně proletěl trubkou

    # Detekce kolizí
    bird_rect = pygame.Rect(bird_x, bird_y, 34, 24)
    for pipe_pair in pipes:
        if bird_rect.colliderect(pipe_pair["top"]) or bird_rect.colliderect(pipe_pair["bottom"]):
            running = False  # jednoduchý konec hry

    if bird_y > HEIGHT or bird_y < 0:
        running = False

    # Vykreslení
    window.fill(WHITE)
    pygame.draw.rect(window, (255, 200, 0), bird_rect)
    for pipe_pair in pipes:
        pygame.draw.rect(window, GREEN, pipe_pair["top"])
        pygame.draw.rect(window, GREEN, pipe_pair["bottom"])

    score_surface = font.render(f"Skóre: {score}", True, (0, 0, 0))
    window.blit(score_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
