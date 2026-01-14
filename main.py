import pygame
from constants import *
from logger import *
from player import *
from asteroid import *
from asteroidfield import *
from shot import *
import sys

def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0

    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2


    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    
    asteroids = pygame.sprite.Group()

    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)

    player = Player(x, y)
    asteroidfield = AsteroidField()

    while True:
        # print(f"Value: {dt}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        log_state()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.fill("black")

        for u in updatable:
            u.update(dt)
        
        for d in drawable:
            d.draw(screen)
        
        for a in asteroids:
            collide = a.collides_with(player)
            if (collide):
                log_event("player_hit")
                print("Game over!")
                sys.exit()
            
            for s in shots:
                collide_shot = a.collides_with(s)
                if (collide_shot):
                    log_event("asteroid_shot")
                    a.split()
                    s.kill()

        pygame.display.flip()
        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()
