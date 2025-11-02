"""flappy_bird.py
===================
Tento soubor obsahuje kompletní, výukovou implementaci hry Flappy Bird
v knihovně Pygame. Kód je bohatě komentovaný, aby se v něm zorientoval i
úplný začátečník. Program je rozdělený do logických bloků:

1. Inicializace knihoven a nastavení okna.
2. Definice jednoduchých tříd `Bird` a `PipePair`.
3. Funkce pro kreslení menu, hry a obrazovky konce.
4. Hlavní herní smyčka, která přepíná mezi stavy MENU → PLAYING → GAME_OVER.

Každý blok má krátký popis, co přesně dělá a proč to děláme.
"""

import random
from dataclasses import dataclass

import pygame

# ---------------------------------------------------------------------------
# 1) START PYGAME A NASTAVENÍ OKNA
# ---------------------------------------------------------------------------
# Pygame musíme inicializovat dřív, než budeme vytvářet okno, fonty apod.
pygame.init()

# Šířka a výška okna. Velikost klidně uprav, pokud chceš menší/lepší plátno.
WIDTH, HEIGHT = 600, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird – výuková verze")

# Vytvoříme objekt pro řízení FPS (frames per second). 60 znamená, že se
# snažíme vykreslit 60 snímků za vteřinu, což je příjemně plynulé.
FPS = 60
CLOCK = pygame.time.Clock()

# ---------------------------------------------------------------------------
# 2) ZÁKLADNÍ BARVY A FONTY
# ---------------------------------------------------------------------------
# Barvy zapisujeme jako trojici (R, G, B). Hodnota 0–255.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (0, 170, 70)
GOLD = (255, 215, 0)

# Písmo použijeme na zobrazování textu. None znamená "výchozí systémové písmo".
MAIN_FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 32)

# ---------------------------------------------------------------------------
# 3) KONSTANTY PRO PTÁKA A TRUBKY
# ---------------------------------------------------------------------------
BIRD_START_X = 120  # Startovní X pozice ptáka, trochu od levého okraje.
BIRD_START_Y = HEIGHT // 2  # Startovní výška ptáka (uprostřed okna).
GRAVITY = 0.35  # Jak rychle pták padá dolů každý snímek.
FLAP_STRENGTH = -8.5  # Síla odrazu, když zmáčkneš skok (mezerník).
BIRD_WIDTH = 48
BIRD_HEIGHT = 34

PIPE_WIDTH = 100
PIPE_GAP = 220  # Velikost mezery mezi horní a spodní trubkou.
PIPE_DISTANCE = 280  # Vzdálenost nových trubek od sebe.
PIPE_SPEED = 3.2

# ---------------------------------------------------------------------------
# 4) TŘÍDY BIRD A PIPEPAIR
# ---------------------------------------------------------------------------
# Používáme dataclass – jednoduchý způsob, jak definovat třídu s atributy.


@dataclass
class Bird:
    """Logika hráče – žlutý pták, kterého ovládáme."""

    x: float
    y: float
    velocity: float = 0

    def flap(self) -> None:
        """Když hráč zmáčkne mezerník, nastavíme rychlost nahoru."""
        self.velocity = FLAP_STRENGTH

    def update(self) -> None:
        """Každý snímek pták padá vlivem gravitace a mění svoji pozici."""
        self.velocity += GRAVITY
        self.y += self.velocity

    def get_rect(self) -> pygame.Rect:
        """Vrátí obdélník ptáka pro snadnější kolize a kreslení."""
        return pygame.Rect(int(self.x), int(self.y), BIRD_WIDTH, BIRD_HEIGHT)

    def draw(self, surface: pygame.Surface) -> None:
        """Nakreslíme ptáka jako zlatý obdélník (můžeš nahradit obrázkem)."""
        pygame.draw.rect(surface, GOLD, self.get_rect())


@dataclass
class PipePair:
    """Dvojice trubek – horní a spodní, mezi nimi je mezera."""

    x: float
    gap_center_y: float
    passed: bool = False  # Pomůže se započítáváním skóre (jen jednou).

    def top_rect(self) -> pygame.Rect:
        """Horní trubka – sahá od shora po střed mezery."""
        top_height = int(self.gap_center_y - PIPE_GAP / 2)
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, top_height)

    def bottom_rect(self) -> pygame.Rect:
        """Spodní trubka – začíná pod mezerou až dolů."""
        bottom_y = int(self.gap_center_y + PIPE_GAP / 2)
        height = HEIGHT - bottom_y
        return pygame.Rect(int(self.x), bottom_y, PIPE_WIDTH, height)

    def update(self) -> None:
        """Každý snímek trubky cestují doleva – pták k nim letí."""
        self.x -= PIPE_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        """Nakreslíme obě trubky najednou."""
        pygame.draw.rect(surface, GRASS_GREEN, self.top_rect())
        pygame.draw.rect(surface, GRASS_GREEN, self.bottom_rect())

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """Zjistíme, jestli pták narazil do horní nebo spodní části."""
        return bird_rect.colliderect(self.top_rect()) or bird_rect.colliderect(
            self.bottom_rect()
        )


# ---------------------------------------------------------------------------
# 5) HERNÍ STAVY – MENU, HRA, GAME OVER
# ---------------------------------------------------------------------------
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"


def draw_background(surface: pygame.Surface) -> None:
    """Jednoduché pozadí – modré nebe a zelený pás dole."""
    surface.fill(SKY_BLUE)
    pygame.draw.rect(surface, GRASS_GREEN, (0, HEIGHT - 60, WIDTH, 60))


def draw_menu(surface: pygame.Surface) -> None:
    """Úvodní obrazovka se stručným návodem."""
    draw_background(surface)

    title = MAIN_FONT.render("Flappy Bird", True, GOLD)
    subtitle = SMALL_FONT.render("Stiskni SPACE pro start", True, BLACK)
    controls = SMALL_FONT.render(
        "Ovládání: SPACE = skoč, ESC = ukončit",
        True,
        BLACK,
    )

    surface.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT * 0.25)))
    surface.blit(subtitle, subtitle.get_rect(center=(WIDTH / 2, HEIGHT * 0.45)))
    surface.blit(controls, controls.get_rect(center=(WIDTH / 2, HEIGHT * 0.60)))


def draw_game_over(surface: pygame.Surface, score: int) -> None:
    """Obrazovka po prohře – nabídneme restart."""
    draw_background(surface)

    title = MAIN_FONT.render("Game Over", True, BLACK)
    score_text = SMALL_FONT.render(f"Skóre: {score}", True, BLACK)
    retry = SMALL_FONT.render("ENTER = hrát znovu, ESC = konec", True, BLACK)

    surface.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT * 0.30)))
    surface.blit(score_text, score_text.get_rect(center=(WIDTH / 2, HEIGHT * 0.50)))
    surface.blit(retry, retry.get_rect(center=(WIDTH / 2, HEIGHT * 0.65)))


def draw_score(surface: pygame.Surface, score: int) -> None:
    """Během hry zobrazujeme skóre v levém horním rohu."""
    text = SMALL_FONT.render(f"Skóre: {score}", True, BLACK)
    surface.blit(text, (20, 20))


# ---------------------------------------------------------------------------
# 6) FUNKCE PRO SPUŠTĚNÍ NEBO RESET HRY
# ---------------------------------------------------------------------------

def create_initial_game_state() -> tuple[Bird, list[PipePair], int]:
    """Vrátí čerstvého ptáka, první trubky a skóre = 0."""
    bird = Bird(BIRD_START_X, BIRD_START_Y)
    pipes = []

    # Aby hra nečekala na první trubky, vytvoříme hned tři s odstupem.
    for i in range(3):
        gap_center = random.randint(180, HEIGHT - 180)
        pipe_x = WIDTH + i * PIPE_DISTANCE
        pipes.append(PipePair(pipe_x, gap_center))

    return bird, pipes, 0


# ---------------------------------------------------------------------------
# 7) HLAVNÍ FUNKCE – HERNÍ SMYČKA
# ---------------------------------------------------------------------------

def main() -> None:
    """Spustí hru a stará se o přepínání stavů a vykreslení."""

    state = MENU
    bird, pipes, score = create_initial_game_state()
    running = True

    while running:
        # CLOCK.tick(FPS) zajistí, že hra pojede stabilně rychlostí FPS.
        CLOCK.tick(FPS)

        # ------------------------------------------------------------------
        # ZPRACOVÁNÍ UŽIVATELSKÝCH UDÁLOSTÍ (klávesnice, zavření okna…)
        # ------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state == MENU and event.key == pygame.K_SPACE:
                    # Start hry
                    state = PLAYING
                    bird, pipes, score = create_initial_game_state()
                elif state == PLAYING and event.key == pygame.K_SPACE:
                    # Pták mávne křídly.
                    bird.flap()
                elif state == GAME_OVER and event.key == pygame.K_RETURN:
                    # Restart po prohře.
                    state = PLAYING
                    bird, pipes, score = create_initial_game_state()

        # ------------------------------------------------------------------
        # STAV MENU – jen kreslíme menu a čekáme na stisk SPACE.
        # ------------------------------------------------------------------
        if state == MENU:
            draw_menu(WINDOW)
            pygame.display.flip()
            continue

        # ------------------------------------------------------------------
        # BĚŽÍCÍ HRA – aktualizujeme ptáka, trubky, kontrolujeme kolize.
        # ------------------------------------------------------------------
        if state == PLAYING:
            bird.update()

            # Přidej novou trubku, jakmile poslední odletí dostatečně vlevo.
            if pipes[-1].x < WIDTH - PIPE_DISTANCE:
                gap_center = random.randint(180, HEIGHT - 180)
                pipes.append(PipePair(WIDTH, gap_center))

            # Aktualizuj trubky a kontroluj skóre.
            for pipe in pipes:
                pipe.update()

                # Pokud pták proletěl za trubku (pravý okraj je vlevo od ptáka)
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1

            # Zbavíme se trubek, které už jsou úplně mimo obrazovku.
            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]

            bird_rect = bird.get_rect()

            # Kolize s trubkami?
            if any(pipe.collides_with(bird_rect) for pipe in pipes):
                state = GAME_OVER

            # Nebo kolize se zemí / nebem (mimo obraz)?
            if bird.y <= -BIRD_HEIGHT or bird.y >= HEIGHT - 60:
                state = GAME_OVER

            # Vykreslíme scénu – pozadí, trubky, ptáka, skóre.
            draw_background(WINDOW)
            for pipe in pipes:
                pipe.draw(WINDOW)
            bird.draw(WINDOW)
            draw_score(WINDOW, score)
            pygame.display.flip()
            continue

        # ------------------------------------------------------------------
        # STAV GAME OVER – zobrazíme skóre a čekáme na ENTER nebo ESC.
        # ------------------------------------------------------------------
        if state == GAME_OVER:
            draw_game_over(WINDOW, score)
            pygame.display.flip()

    # Když `running` = False, skončíme a zavřeme Pygame.
    pygame.quit()


if __name__ == "__main__":
    main()
