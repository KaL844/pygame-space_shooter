import pygame
import components.scene as scene

pygame.init()

# Define constants
WIN_WIDTH = 600
WIN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Space Shooter"

# Create game window
WINDOW = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

scene_manager = scene.SceneManager.getInstance()

def main():
    running = True
    clock = pygame.time.Clock()

    game_scene = scene.StartScene(scene_manager)
    scene_manager.push(game_scene)

    while not scene_manager.isEmpty() and running:
        clock.tick(FPS)

        # Draw game objects
        scene_manager.draw(WINDOW)
        pygame.display.update()

        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        scene_manager.handle_events(events)

        scene_manager.update()

    pygame.quit()

if __name__ == '__main__':
    main()