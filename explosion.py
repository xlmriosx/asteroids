import pygame
from circleshape import CircleShape
import random

class Explosion(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, 1)
        self.particles = []
        for _ in range(20):
            velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(50, 200)
            self.particles.append([pygame.Vector2(x, y), velocity, random.uniform(0.2, 0.5)]) # pos, vel, life

    def update(self, dt):
        alive_particles = []
        for p in self.particles:
            p[0] += p[1] * dt
            p[2] -= dt
            if p[2] > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        
        if len(self.particles) == 0:
            self.kill()

    def draw(self, screen):
        for p in self.particles:
            pygame.draw.circle(screen, "orange", p[0], 2)
