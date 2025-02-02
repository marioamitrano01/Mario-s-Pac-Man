import sys
import random
import pygame
from pygame.math import Vector2
from functools import wraps
from typing import List, Tuple, Set, Optional

# Global constants
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
TILE_SIZE = 32
FPS = 60

# Maze layout: '#' represents a wall, '.' represents a pellet.
maze_layout: List[str] = [
    "####################",
    "#........##........#",
    "#.####...##...####.#",
    "#..................#",
    "#.####.#.##.#.####.#",
    "#......#....#......#",
    "######.#.##.#.######",
    "     #.#.##.#.#     ",
    "######.#.##.#.######",
    "#........##........#",
    "#.####...##...####.#",
    "#......#....#......#",
    "####################"
]

# Debug decorator for logging function calls (optional)
def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Uncomment next line to enable debugging output:
        # print(f"[DEBUG] Calling {func.__name__} with args: {args[1:]}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        # print(f"[DEBUG] {func.__name__} returned {result}")
        return result
    return wrapper

# Maze class
class Maze:
    def __init__(self, layout: List[str], tile_size: int, offset: Tuple[int, int]) -> None:
        """
        :param layout: List of strings representing the maze layout.
        :param tile_size: Size of each tile in pixels.
        :param offset: (x, y) offset to center the maze on the screen.
        """
        self.layout = layout
        self.tile_size = tile_size
        self.offset = offset
        self.pellets: Set[Tuple[int, int]] = set()  # (column, row) positions for pellets
        self.walls: List[pygame.Rect] = []           # List of wall rectangles
        self._parse_layout()

    def _parse_layout(self) -> None:
        for row_index, row in enumerate(self.layout):
            for col_index, char in enumerate(row):
                pos_x = col_index * self.tile_size + self.offset[0]
                pos_y = row_index * self.tile_size + self.offset[1]
                if char == '#':
                    self.walls.append(pygame.Rect(pos_x, pos_y, self.tile_size, self.tile_size))
                elif char == '.':
                    self.pellets.add((col_index, row_index))

    def draw(self, screen: pygame.Surface) -> None:
        # Draw walls in blue
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 255), wall)
        # Draw pellets in yellow
        for pellet in self.pellets:
            pellet_x = int(pellet[0] * self.tile_size + self.tile_size // 2 + self.offset[0])
            pellet_y = int(pellet[1] * self.tile_size + self.tile_size // 2 + self.offset[1])
            pygame.draw.circle(screen, (255, 255, 0), (pellet_x, pellet_y), 4)

    def eat_pellet(self, tile_pos: Tuple[int, int]) -> bool:
        if tile_pos in self.pellets:
            self.pellets.remove(tile_pos)
            return True
        return False

# Player class (Pac-Man)
class Player:
    def __init__(self, position: Tuple[int, int], speed: float, maze: Maze) -> None:
        """
        :param position: Starting position (in pixels).
        :param speed: Movement speed in pixels per second.
        :param maze: Reference to the Maze for collision detection.
        """
        self.position: Vector2 = Vector2(position)
        self.speed: float = speed
        self.maze: Maze = maze
        self.radius: int = TILE_SIZE // 2 - 2  # So Pac-Man fits inside a tile
        self.direction: Vector2 = Vector2(1, 0)  # Initial direction: right
        self.next_direction: Optional[Vector2] = None  # Buffered direction
        self.mouth_open: bool = True
        self.mouth_timer: float = 0.0
        self.mouth_interval: float = 200.0  # Milliseconds for mouth toggle

    def try_change_direction(self) -> None:
        """
        If there is a buffered direction, apply it when Pac-Man is close enough to the center of a tile and
        the new direction is not blocked.
        """
        if self.next_direction is None:
            return

        # Compute Pac-Man's center (self.position is top-left)
        player_center = self.position + Vector2(TILE_SIZE / 2, TILE_SIZE / 2)

        # Determine the tile in which the player is
        tile_x = int((player_center.x - self.maze.offset[0]) // TILE_SIZE)
        tile_y = int((player_center.y - self.maze.offset[1]) // TILE_SIZE)

        # Calculate the exact center of the tile
        tile_center = Vector2(
            self.maze.offset[0] + tile_x * TILE_SIZE + TILE_SIZE / 2,
            self.maze.offset[1] + tile_y * TILE_SIZE + TILE_SIZE / 2
        )

        # If the distance between the centers is less than 4 pixels, try to apply the buffered direction
        if (player_center - tile_center).length() < 4:
            test_position = self.position + self.next_direction * self.speed * (1 / FPS)
            test_rect = pygame.Rect(test_position.x, test_position.y, TILE_SIZE, TILE_SIZE)
            if not any(test_rect.colliderect(wall) for wall in self.maze.walls):
                self.direction = self.next_direction
                self.next_direction = None

    @debug
    def update(self, dt: float) -> None:
        # Attempt to change direction if a buffered input exists
        self.try_change_direction()

        # Move in the current direction
        move_amount = self.direction * self.speed * dt
        new_position = self.position + move_amount

        pacman_rect = pygame.Rect(new_position.x, new_position.y, TILE_SIZE, TILE_SIZE)
        if not any(pacman_rect.colliderect(wall) for wall in self.maze.walls):
            self.position = new_position

        # Update mouth animation
        self.mouth_timer += dt * 1000  # Convert dt to milliseconds
        if self.mouth_timer >= self.mouth_interval:
            self.mouth_open = not self.mouth_open
            self.mouth_timer = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        center = (int(self.position.x + TILE_SIZE / 2), int(self.position.y + TILE_SIZE / 2))
        color = (255, 255, 0)  # Yellow
        if self.mouth_open:
            pygame.draw.circle(screen, color, center, self.radius)
            # Draw an open mouth as a black triangle
            mouth_points = [
                center,
                (center[0] + self.radius, center[1] - self.radius // 2),
                (center[0] + self.radius, center[1] + self.radius // 2)
            ]
            pygame.draw.polygon(screen, (0, 0, 0), mouth_points)
        else:
            pygame.draw.circle(screen, color, center, self.radius)

# Ghost class
class Ghost:
    def __init__(self, position: Tuple[int, int], speed: float, color: Tuple[int, int, int], maze: Maze) -> None:
        """
        :param position: Initial position of the ghost.
        :param speed: Movement speed in pixels per second.
        :param color: Ghost color (RGB tuple).
        :param maze: Reference to the Maze for collision detection.
        """
        self.position: Vector2 = Vector2(position)
        self.speed: float = speed
        self.color: Tuple[int, int, int] = color
        self.maze: Maze = maze
        self.radius: int = TILE_SIZE // 2 - 2
        self.direction: Vector2 = self.random_direction()
        self.change_dir_timer: float = 0.0
        self.change_interval: float = 1000.0  # Milliseconds

    def random_direction(self) -> Vector2:
        directions = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]
        return random.choice(directions)

    def update(self, dt: float) -> None:
        self.change_dir_timer += dt * 1000
        if self.change_dir_timer >= self.change_interval:
            self.direction = self.random_direction()
            self.change_dir_timer = 0.0

        move_amount = self.direction * self.speed * dt
        new_position = self.position + move_amount
        ghost_rect = pygame.Rect(new_position.x, new_position.y, TILE_SIZE, TILE_SIZE)
        if any(ghost_rect.colliderect(wall) for wall in self.maze.walls):
            self.direction = self.random_direction()
        else:
            self.position = new_position

    def draw(self, screen: pygame.Surface) -> None:
        center = (int(self.position.x + TILE_SIZE / 2), int(self.position.y + TILE_SIZE / 2))
        pygame.draw.circle(screen, self.color, center, self.radius)

# Game class with improved interface and creative end screens
class Game:
    def __init__(self) -> None:
        pygame.init()
        # We no longer use the mixer since there is no sound.
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario's Pac-Man")

        # Fonts for UI messages
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 36)

        self.state: str = "start"  # Game states: "start", "playing", "game_over", "win"
        self.state_timer: float = 0.0  # For animating end screens
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game objects and score."""
        maze_width = len(maze_layout[0]) * TILE_SIZE
        maze_height = len(maze_layout) * TILE_SIZE
        offset_x = (SCREEN_WIDTH - maze_width) // 2
        offset_y = (SCREEN_HEIGHT - maze_height) // 2
        self.maze = Maze(maze_layout, TILE_SIZE, (offset_x, offset_y))
        self.player = Player((offset_x + TILE_SIZE, offset_y + TILE_SIZE), 100, self.maze)
        self.ghosts: List[Ghost] = []
        ghost_colors = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
        ghost_positions = [
            (offset_x + TILE_SIZE * 10, offset_y + TILE_SIZE * 5),
            (offset_x + TILE_SIZE * 9,  offset_y + TILE_SIZE * 5),
            (offset_x + TILE_SIZE * 10, offset_y + TILE_SIZE * 6),
            (offset_x + TILE_SIZE * 9,  offset_y + TILE_SIZE * 6)
        ]
        for pos, color in zip(ghost_positions, ghost_colors):
            self.ghosts.append(Ghost(pos, 80, color, self.maze))
        self.score: int = 0

    def process_events(self) -> None:
        """Handle events and state transitions."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "exit"
            elif event.type == pygame.KEYDOWN:
                if self.state == "start":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.reset_game()
                elif self.state == "playing":
                    # Buffer directional inputs
                    if event.key == pygame.K_LEFT:
                        self.player.next_direction = Vector2(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player.next_direction = Vector2(1, 0)
                    elif event.key == pygame.K_UP:
                        self.player.next_direction = Vector2(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player.next_direction = Vector2(0, 1)
                elif self.state in ("game_over", "win"):
                    # In either end state, press R to restart.
                    if event.key == pygame.K_r:
                        self.state = "playing"
                        self.reset_game()
                        self.state_timer = 0.0

    def update(self, dt: float) -> None:
        """Update game objects if playing."""
        if self.state == "playing":
            self.player.update(dt)
            for ghost in self.ghosts:
                ghost.update(dt)

            # Pellet consumption using player's center
            player_center = self.player.position + Vector2(TILE_SIZE / 2, TILE_SIZE / 2)
            tile_x = int((player_center.x - self.maze.offset[0]) // TILE_SIZE)
            tile_y = int((player_center.y - self.maze.offset[1]) // TILE_SIZE)
            if self.maze.eat_pellet((tile_x, tile_y)):
                self.score += 10

            # Check win condition: no more pellets
            if not self.maze.pellets:
                self.state = "win"
                self.state_timer = 0.0

            # Check collision between player and ghosts
            player_rect = pygame.Rect(self.player.position.x, self.player.position.y, TILE_SIZE, TILE_SIZE)
            for ghost in self.ghosts:
                ghost_rect = pygame.Rect(ghost.position.x, ghost.position.y, TILE_SIZE, TILE_SIZE)
                if player_rect.colliderect(ghost_rect):
                    self.state = "game_over"
                    self.state_timer = 0.0
                    break

        # In the end states, update the timer (for dynamic animations)
        if self.state in ("game_over", "win"):
            self.state_timer += dt

    def draw(self) -> None:
        """Draw the game or UI screens depending on state."""
        self.screen.fill((0, 0, 0))
        if self.state == "start":
            # Draw the start menu
            title_text = self.big_font.render("Mario's Pac-Man", True, (255, 255, 0))
            instruction_text = self.font.render("Press SPACE to start", True, (255, 255, 255))
            self.screen.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(instruction_text, ((SCREEN_WIDTH - instruction_text.get_width()) // 2, SCREEN_HEIGHT // 2))
        elif self.state == "playing":
            # Draw the game objects
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            # Draw the score
            score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surface, (10, 10))
        elif self.state == "game_over":
            # Create a flashing color effect for the "Game Over" message
            flash_color = (255, 0, 0) if int(self.state_timer * 3) % 2 == 0 else (255, 255, 0)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            game_over_text = self.big_font.render("Game Over!", True, flash_color)
            restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
            self.screen.blit(game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2, SCREEN_HEIGHT // 2))
            score_surface = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surface, ((SCREEN_WIDTH - score_surface.get_width()) // 2, SCREEN_HEIGHT // 2 + 30))
        elif self.state == "win":
            # Create a dynamic "You Win!" screen
            flash_color = (0, 255, 0) if int(self.state_timer * 3) % 2 == 0 else (0, 200, 200)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            win_text = self.big_font.render("Congratulations, You Win!", True, flash_color)
            restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
            self.screen.blit(win_text, ((SCREEN_WIDTH - win_text.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2, SCREEN_HEIGHT // 2))
            score_surface = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surface, ((SCREEN_WIDTH - score_surface.get_width()) // 2, SCREEN_HEIGHT // 2 + 30))
        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while self.state != "exit":
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            self.process_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
