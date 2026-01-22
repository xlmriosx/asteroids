import pygame
from constants import *
from logger import *
from player import *
from asteroid import *
from asteroidfield import *
from shot import *
from explosion import Explosion
from powerup import PowerUp
import random
import sys
import score_manager

# Initialize Pygame and Font globally once
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")

# Load Assets
try:
    background = pygame.image.load("background.png")
except:
    background = None # Fallback

# Fonts
font_title = pygame.font.SysFont("arial", 80)
font_menu = pygame.font.SysFont("arial", 50)
font_ui = pygame.font.SysFont("arial", 36)
font_small = pygame.font.SysFont("arial", 24)

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_HOVER = (200, 200, 255)
COLOR_ACCENT = (100, 255, 100)
COLOR_DANGER = (255, 100, 100)

class Game:
    def __init__(self):
        self.state = "MENU" # MENU, GAME, GAME_OVER, LEADERBOARD, NAME_ENTRY
        self.clock = pygame.time.Clock()
        self.dt = 0
        
        # Game Objects
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Containers configuration
        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable)
        Shot.containers = (self.shots, self.updatable, self.drawable)
        Explosion.containers = (self.updatable, self.drawable)
        PowerUp.containers = (self.powerups, self.updatable, self.drawable)
        
        # Game State Variables
        self.player = None
        self.asteroidfield = None
        self.score = 0
        self.lives = PLAYER_LIVES
        self.respawn_timer = 0
        
        # Name Entry
        self.input_name = ""
        
        # Setup Initial Menu
        self.buttons = {
            "START": pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 50),
            "LEADERBOARD": pygame.Rect(SCREEN_WIDTH//2 - 125, 380, 250, 50),
            "EXIT": pygame.Rect(SCREEN_WIDTH//2 - 100, 460, 200, 50),
            "BACK": pygame.Rect(SCREEN_WIDTH//2 - 100, 600, 200, 50)
        }

    def reset_game(self):
        self.updatable.empty()
        self.drawable.empty()
        self.asteroids.empty()
        self.shots.empty()
        self.powerups.empty()
        
        self.score = 0
        self.lives = PLAYER_LIVES
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroidfield = AsteroidField()
        self.respawn_timer = 0

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if self.state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.buttons["START"].collidepoint(mouse_pos):
                        self.reset_game()
                        self.state = "GAME"
                    elif self.buttons["LEADERBOARD"].collidepoint(mouse_pos):
                        self.state = "LEADERBOARD"
                    elif self.buttons["EXIT"].collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
            
            elif self.state == "LEADERBOARD":
                if event.type == pygame.MOUSEBUTTONDOWN:
                     if self.buttons["BACK"].collidepoint(event.pos):
                         self.state = "MENU"

            elif self.state == "NAME_ENTRY":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.input_name:
                            score_manager.add_score(self.input_name, self.score)
                            self.state = "LEADERBOARD"
                        else:
                            self.state = "MENU" # Skip if empty?
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    else:
                        if len(self.input_name) < 10 and event.unicode.isprintable():
                           self.input_name += event.unicode
            
            elif self.state == "GAME_OVER":
                 if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_SPACE:
                         self.state = "MENU"

    def update(self):
        if self.state == "GAME":
            self.updatable.update(self.dt)
            self.check_collisions()
            self.check_respawn()
            
    def check_collisions(self):
        if self.player.alive():
             if self.player.bomb_dropped:
                self.player.bomb_dropped = False
                for a in self.asteroids:
                    Explosion(a.position.x, a.position.y)
                    a.kill()
                    self.score += 10
             
             for p in self.powerups:
                 if self.player.collides_with(p):
                     if p.kind == "shield":
                         self.player.shield_active = True
                     elif p.kind == "speed":
                         self.player.speed_boost = 1.5
                     elif p.kind == "bomb":
                         self.player.bomb_count += 1
                     elif p.kind == "spread":
                         self.player.weapon_type = "spread"
                     elif p.kind == "rapid":
                         self.player.weapon_type = "rapid"
                     p.kill()

        for a in self.asteroids:
            if self.player.alive() and a.collides_with(self.player):
                if self.player.invulnerable_timer > 0:
                    pass # Ignore collision
                elif self.player.shield_active:
                    self.player.shield_active = False
                    Explosion(a.position.x, a.position.y)
                    a.split()
                else:
                    log_event("player_hit")
                    self.player.kill()
                    Explosion(self.player.position.x, self.player.position.y)
                    self.lives -= 1
                    self.respawn_timer = 1 

            for s in self.shots:
                if a.collides_with(s):
                    log_event("asteroid_shot")
                    a.split()
                    s.kill()
                    Explosion(a.position.x, a.position.y)
                    
                    if a.radius == ASTEROID_MIN_RADIUS:
                        self.score += SCORE_ASTEROID_SMALL
                    elif a.radius == ASTEROID_MIN_RADIUS * 2:
                        self.score += SCORE_ASTEROID_MEDIUM
                    else:
                        self.score += SCORE_ASTEROID_LARGE
                    
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        kind = random.choice(["shield", "speed", "bomb", "spread", "rapid"])
                        PowerUp(a.position.x, a.position.y, kind)
    
    def check_respawn(self):
        if not self.player.alive() and self.lives > 0:
            self.respawn_timer -= self.dt
            if self.respawn_timer <= 0:
                self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        elif not self.player.alive() and self.lives <= 0:
             # Check high score
             if score_manager.is_mid_high_score(self.score):
                 self.input_name = ""
                 self.state = "NAME_ENTRY"
             else:
                 self.state = "GAME_OVER"

    def draw(self):
        if background:
            screen.blit(background, (0,0))
        else:
            screen.fill(COLOR_BLACK)

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "GAME_OVER":
            self.draw_game() # Draw game in background
            self.draw_game_over()
        elif self.state == "NAME_ENTRY":
            self.draw_game() # Draw game in background
            self.draw_name_entry()
        elif self.state == "LEADERBOARD":
            self.draw_leaderboard()

        pygame.display.flip()

    def draw_text_centered(self, text, font, color, y_offset=0):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
        screen.blit(surface, rect)

    def draw_button(self, text, rect, hover_color=COLOR_HOVER, default_color=COLOR_WHITE):
        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if rect.collidepoint(mouse_pos) else default_color
        
        # Create a surface for the button with alpha for glass morphism effect
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (50, 50, 50, 180), button_surface.get_rect(), border_radius=10)
        pygame.draw.rect(button_surface, color, button_surface.get_rect(), 2, border_radius=10)
        
        screen.blit(button_surface, rect)
        
        text_surf = font_menu.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_menu(self):
        self.draw_text_centered("ASTEROIDS", font_title, COLOR_WHITE, -200)
        
        self.draw_button("START", self.buttons["START"])
        self.draw_button("TOP 10", self.buttons["LEADERBOARD"])
        self.draw_button("EXIT", self.buttons["EXIT"])

    def draw_game(self):
        for d in self.drawable:
            d.draw(screen)
            
        # UI
        score_text = font_ui.render(f"Score: {self.score}", True, COLOR_WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font_ui.render(f"Lives: {self.lives}", True, COLOR_WHITE)
        screen.blit(lives_text, (10, 50))
        
        if self.player and self.player.alive():
             bomb_text = font_ui.render(f"Bombs: {self.player.bomb_count}", True, COLOR_WHITE)
             screen.blit(bomb_text, (10, 90))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0,0))
        
        self.draw_text_centered("GAME OVER", font_title, COLOR_DANGER, -50)
        self.draw_text_centered(f"Final Score: {self.score}", font_menu, COLOR_WHITE, 50)
        self.draw_text_centered("Press SPACE to return to Menu", font_small, COLOR_ACCENT, 100)

    def draw_name_entry(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0,0))

        self.draw_text_centered("NEW HIGH SCORE!", font_title, COLOR_ACCENT, -100)
        self.draw_text_centered(f"Score: {self.score}", font_menu, COLOR_WHITE, -20)
        self.draw_text_centered("Enter Name:", font_ui, COLOR_WHITE, 50)
        
        name_surf = font_menu.render(self.input_name + "_", True, COLOR_ACCENT)
        name_rect = name_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(name_surf, name_rect)

    def draw_leaderboard(self):
        self.draw_text_centered("TOP 10 SCORES", font_title, COLOR_WHITE, -250)
        
        scores = score_manager.get_top_scores()
        
        start_y = 200
        for i, entry in enumerate(scores):
            color = COLOR_ACCENT if i == 0 else COLOR_WHITE
            text = f"{i+1}. {entry['name']}   -   {entry['score']}"
            line_surf = font_ui.render(text, True, color)
            rect = line_surf.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 40))
            screen.blit(line_surf, rect)
            
        self.draw_button("BACK", self.buttons["BACK"])

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
