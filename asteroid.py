from circleshape import *
from constants import *
from logger import *
import random

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.points = []
        for i in range(8):
            angle = i * (360 / 8)
            dist = self.radius + random.uniform(-self.radius / 4, self.radius / 4)
            point = pygame.Vector2(0, 1).rotate(angle) * dist
            self.points.append(point)
        
    def draw(self, screen):
        # Transform points to world coordinates
        world_points = [self.position + p for p in self.points]
        pygame.draw.polygon(screen, "white", world_points, LINE_WIDTH)

    def update(self, dt):
        self.position += (self.velocity * dt) 
        self.wrap_screen()
    
    def split(self):
        self.kill()

        if (self.radius <= ASTEROID_MIN_RADIUS):
            return
        
        log_event("asteroid_split")
        random_angle = random.uniform(20, 50)
        vector1 = self.velocity.rotate(random_angle)
        vector2 = self.velocity.rotate(-random_angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = vector1 * 1.2
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2.velocity = vector2 * 1.2
    
