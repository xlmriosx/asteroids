import pygame
from circleshape import CircleShape
import random
from constants import *

class PowerUp(CircleShape):
    def __init__(self, x, y, kind):
        super().__init__(x, y, 10)
        self.kind = kind # "shield", "speed", "bomb"
        self.timer = POWERUP_DURATION
        
    def draw(self, screen):
        color = "white"
        if self.kind == "shield":
            color = "blue"
        elif self.kind == "speed":
            color = "yellow"
        elif self.kind == "bomb":
            color = "red"
            
        pygame.draw.circle(screen, color, self.position, self.radius)
        pygame.draw.circle(screen, "white", self.position, self.radius, 1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_screen()
        self.timer -= dt
        if self.timer < 0:
            self.kill()
