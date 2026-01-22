import pygame
from constants import *
from circleshape import CircleShape
from shot import *

class Player(CircleShape):
    def __init__(self, x, y):
        # Call the parent class (CircleShape) constructor
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0
        self.shield_active = False
        self.speed_boost = 1.0
        self.bomb_count = 0
        self.bomb_dropped = False
        self.weapon_type = "default"
        self.invulnerable_timer = PLAYER_INVULNERABILITY_TIME

    # The triangle method provided in your assignment
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        if self.invulnerable_timer > 0:
             # Flash effect: only draw if (timer * 10) cast to int is even/odd
             if int(self.invulnerable_timer * 10) % 2 == 0:
                 return

        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)
        if self.shield_active:
             pygame.draw.circle(screen, "blue", self.position, self.radius + 5, 1)
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(dt)
        if keys[pygame.K_d]:
            self.rotate(-dt)

        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_w]:
            self.move(dt)

        if keys[pygame.K_SPACE]:
            self.shoot()
        
        if keys[pygame.K_b] and self.bomb_count > 0:
            self.use_bomb()

        self.timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        # Physics update
        self.velocity *= PLAYER_FRICTION
        self.position += self.velocity * dt
        self.wrap_screen()

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += forward * PLAYER_ACCELERATION * self.speed_boost * dt
    
    def use_bomb(self):
        self.bomb_dropped = True
        self.bomb_count -= 1
    
    def shoot(self):
        if self.timer > 0:
            return
        
        if self.weapon_type == "spread":
            for angle in [-15, 0, 15]:
                shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
                forward = pygame.Vector2(0, 1).rotate(self.rotation + angle)
                shot.velocity = forward * PLAYER_SHOOT_SPEED + self.velocity
        else:
            shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            shot.velocity = forward * PLAYER_SHOOT_SPEED + self.velocity
            
        self.timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        if self.weapon_type == "rapid":
            self.timer /= 2

    def collides_with(self, other):
        # Triangle vs Circle collision
        points = self.triangle()
        
        # Check if any vertex is inside the circle
        for point in points:
            if point.distance_to(other.position) <= other.radius:
                return True
        
        # Check if the circle overlaps any edge
        for i in range(3):
            p1 = points[i]
            p2 = points[(i + 1) % 3]
            
            # Vector from p1 to p2
            edge_vec = p2 - p1
            # Vector from p1 to circle center
            center_vec = other.position - p1
            
            # Project center_vec onto edge_vec, constrained to [0, 1]
            t = center_vec.dot(edge_vec) / edge_vec.length_squared()
            t = max(0, min(1, t))
            
            # Closest point on the segment
            closest_point = p1 + edge_vec * t
            
            if closest_point.distance_to(other.position) <= other.radius:
                return True
                
        return False

        
