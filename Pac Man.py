import pygame
import sys
import random
import math
from collections import deque




pygame.init()
FPS = 30
clock = pygame.time.Clock()
block_size = 20
MAP_ROWS = 23
MAP_COLS = 21
RIGHT = 4
UP = 3
LEFT = 2
DOWN = 1
BLACK = (0, 0, 0)
WALL_COLOR = (52, 45, 202)
WALL_INNER_COLOR = (0, 0, 0)
FOOD_COLOR = (254, 184, 151)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
WIDTH = block_size * MAP_COLS
HEIGHT = block_size * MAP_ROWS + 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario's Pacman")



game_map_layout = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,2,2,2,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,1,2,1,1,2,1,2,1,1,1,1,1],
    [2,2,2,2,2,2,2,2,1,2,2,2,1,2,2,2,2,2,2,2,2],
    [1,1,1,1,1,2,1,2,1,2,2,2,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,1,1,1,1,1,2,1,2,1,0,0,0,0],
    [0,0,0,0,1,2,1,2,2,2,2,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,2,2,1,1,1,1,1,2,2,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,1,2,2,2,2,2,1,2,2,2,2,2,1,2,2,2,1],
    [1,1,2,2,1,2,1,2,1,1,1,1,1,2,1,2,1,2,2,1,1],
    [1,2,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]




random_targets = [



    (block_size, block_size),
    (block_size, (MAP_ROWS - 2) * block_size),
    ((MAP_COLS - 2) * block_size, block_size),
    ((MAP_COLS - 2) * block_size, (MAP_ROWS - 2) * block_size)
]



score = 0
lives = 3
ghost_count = 4
def copy_map(m):
    return [row[:] for row in m]





class Pacman:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.frame_count = 7
        self.current_frame = 1
        self.animation_timer = 0

        
    def get_map_x(self):
        return int(self.x // block_size)
    

    def get_map_y(self):
        return int(self.y // block_size)
    

    def get_map_x_right_side(self):
        return int((self.x + self.size - 1) // block_size)
    

    def get_map_y_bottom_side(self):
        return int((self.y + self.size - 1) // block_size)
    

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 100:
            self.current_frame = self.current_frame + 1 if self.current_frame < self.frame_count else 1
            self.animation_timer = 0


    def move_forwards(self):
        if self.direction == RIGHT:
            self.x += self.speed
        elif self.direction == UP:
            self.y -= self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed


    def move_backwards(self):
        if self.direction == RIGHT:
            self.x -= self.speed
        elif self.direction == UP:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x += self.speed
        elif self.direction == DOWN:
            self.y -= self.speed


    def check_collisions(self, game_map):
        corners = [
            (self.x, self.y),
            (self.x + self.size - 1, self.y),
            (self.x, self.y + self.size - 1),
            (self.x + self.size - 1, self.y + self.size - 1)
        ]


        for cx, cy in corners:
            map_x = int(cx // block_size)
            map_y = int(cy // block_size)
            if map_y < 0 or map_y >= len(game_map) or map_x < 0 or map_x >= len(game_map[0]):
                continue
            if game_map[map_y][map_x] == 1:
                return True
        return False
    


    def change_direction_if_possible(self, game_map):
        if self.direction == self.next_direction:
            return
        original_direction = self.direction
        self.direction = self.next_direction
        self.move_forwards()
        if self.check_collisions(game_map):
            self.move_backwards()
            self.direction = original_direction
        else:
            self.move_backwards()



    def move_process(self, game_map):
        self.change_direction_if_possible(game_map)
        self.move_forwards()
        if self.check_collisions(game_map):
            self.move_backwards()



    def eat(self, game_map):
        global score
        map_x = self.get_map_x()
        map_y = self.get_map_y()
        if map_y < 0 or map_y >= len(game_map) or map_x < 0 or map_x >= len(game_map[0]):
            return
        if game_map[map_y][map_x] == 2:
            game_map[map_y][map_x] = 3
            score += 1




    def draw(self, surface):
        center = (int(self.x + self.size / 2), int(self.y + self.size / 2))
        radius = self.size // 2
        open_angle = (self.current_frame / self.frame_count) * 45
        pygame.draw.circle(surface, PACMAN_COLOR, center, radius)




class Ghost:
    def __init__(self, x, y, size, speed, range_radius, target_index=0):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.direction = RIGHT
        self.range_radius = range_radius
        self.random_target_index = target_index
        self.target = random_targets[self.random_target_index]
        self.last_random_change = pygame.time.get_ticks()



    def get_map_x(self):
        return int(self.x // block_size)
    

    def get_map_y(self):
        return int(self.y // block_size)
    

    def get_map_x_right_side(self):
        return int((self.x + self.size - 1) // block_size)
    

    def get_map_y_bottom_side(self):
        return int((self.y + self.size - 1) // block_size)
    

    def check_collisions(self, game_map):
        corners = [
            (self.x, self.y),
            (self.x + self.size - 1, self.y),
            (self.x, self.y + self.size - 1),
            (self.x + self.size - 1, self.y + self.size - 1)
        ]
        for cx, cy in corners:
            map_x = int(cx // block_size)
            map_y = int(cy // block_size)
            if map_y < 0 or map_y >= len(game_map) or map_x < 0 or map_x >= len(game_map[0]):
                continue
            if game_map[map_y][map_x] == 1:
                return True
        return False
    


    def move_forwards(self):
        if self.direction == RIGHT:
            self.x += self.speed
        elif self.direction == UP:
            self.y -= self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed


    def move_backwards(self):
        if self.direction == RIGHT:
            self.x -= self.speed
        elif self.direction == UP:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x += self.speed
        elif self.direction == DOWN:
            self.y -= self.speed


    def is_in_range(self, pacman):
        dx = self.get_map_x() - pacman.get_map_x()
        dy = self.get_map_y() - pacman.get_map_y()
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.range_radius
    

    def change_random_direction(self):
        self.random_target_index = (self.random_target_index + 1) % len(random_targets)
        self.target = random_targets[self.random_target_index]


    def calculate_new_direction(self, game_map, dest_x, dest_y):
        start = (self.get_map_x(), self.get_map_y())
        queue = deque()
        queue.append((start, []))
        visited = set()
        visited.add(start)
        while queue:
            current, moves = queue.popleft()
            if current == (dest_x, dest_y):
                return moves[0] if moves else self.direction
            for d, (dx, dy) in zip([LEFT, RIGHT, UP, DOWN], [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= ny < len(game_map) and 0 <= nx < len(game_map[0]):
                    if game_map[ny][nx] != 1 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), moves + [d]))
        return self.direction
    

    def change_direction_if_possible(self, game_map, pacman):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_random_change > 10000:
            self.change_random_direction()
            self.last_random_change = current_time
        if self.is_in_range(pacman):
            dest = (pacman.get_map_x(), pacman.get_map_y())
        else:
            dest = (int(self.target[0] // block_size), int(self.target[1] // block_size))
        new_dir = self.calculate_new_direction(game_map, dest[0], dest[1])
        old_dir = self.direction
        self.direction = new_dir
        self.move_forwards()
        if self.check_collisions(game_map):
            self.move_backwards()
            self.direction = old_dir
        else:
            self.move_backwards()


    def move_process(self, game_map, pacman):
        self.change_direction_if_possible(game_map, pacman)
        self.move_forwards()
        if self.check_collisions(game_map):
            self.move_backwards()



    def draw(self, surface):
        center = (int(self.x + self.size / 2), int(self.y + self.size / 2))
        radius = self.size // 2
        pygame.draw.circle(surface, GHOST_COLOR, center, radius)
        pygame.draw.circle(surface, (255, 100, 100), center, int(self.range_radius * block_size), 1)



def draw_walls(surface, game_map):


    
    wall_space_width = block_size / 1.6
    wall_offset = (block_size - wall_space_width) / 2
    for row in range(len(game_map)):
        for col in range(len(game_map[0])):
            if game_map[row][col] == 1:
                rect = pygame.Rect(col * block_size, row * block_size, block_size, block_size)
                pygame.draw.rect(surface, WALL_COLOR, rect)
                if col > 0 and game_map[row][col - 1] == 1:
                    inner_rect = pygame.Rect(col * block_size, row * block_size + wall_offset, wall_space_width + wall_offset, wall_space_width)
                    pygame.draw.rect(surface, WALL_INNER_COLOR, inner_rect)
                if col < len(game_map[0]) - 1 and game_map[row][col + 1] == 1:
                    inner_rect = pygame.Rect(col * block_size + wall_offset, row * block_size + wall_offset, wall_space_width + wall_offset, wall_space_width)
                    pygame.draw.rect(surface, WALL_INNER_COLOR, inner_rect)
                if row < len(game_map) - 1 and game_map[row + 1][col] == 1:
                    inner_rect = pygame.Rect(col * block_size + wall_offset, row * block_size + wall_offset, wall_space_width, wall_space_width + wall_offset)
                    pygame.draw.rect(surface, WALL_INNER_COLOR, inner_rect)
                if row > 0 and game_map[row - 1][col] == 1:
                    inner_rect = pygame.Rect(col * block_size + wall_offset, row * block_size, wall_space_width, wall_space_width + wall_offset)
                    pygame.draw.rect(surface, WALL_INNER_COLOR, inner_rect)


def draw_foods(surface, game_map):
    for row in range(len(game_map)):
        for col in range(len(game_map[0])):
            if game_map[row][col] == 2:
                food_rect = pygame.Rect(col * block_size + block_size / 3, row * block_size + block_size / 3, block_size / 3, block_size / 3)
                pygame.draw.rect(surface, FOOD_COLOR, food_rect)



def draw_score_and_lives(surface):
    font = pygame.font.SysFont("Arial", 20)
    score_text = font.render("Score: " + str(score), True, TEXT_COLOR)
    surface.blit(score_text, (10, block_size * MAP_ROWS + 10))
    lives_text = font.render("Lives: ", True, TEXT_COLOR)
    surface.blit(lives_text, (WIDTH - 150, block_size * MAP_ROWS + 10))
    for i in range(lives):
        pygame.draw.circle(surface, PACMAN_COLOR, (WIDTH - 80 + i * (block_size + 5), block_size * MAP_ROWS + 20), block_size // 2)



def create_new_pacman():
    return Pacman(block_size, block_size, block_size, block_size / 5)


def create_ghosts():
    ghosts = []
    for i in range(ghost_count * 2):
        init_x = 9 * block_size + (0 if i % 2 == 0 else 1) * block_size
        init_y = 10 * block_size + (0 if i % 2 == 0 else 1) * block_size
        ghost_speed = (block_size / 5) / 2
        range_radius = 6 + i
        ghosts.append(Ghost(init_x, init_y, block_size, ghost_speed, range_radius, target_index=i % len(random_targets)))
    return ghosts



def update_game(pacman, ghosts, game_map):
    pacman.move_process(game_map)
    pacman.eat(game_map)
    for ghost in ghosts:
        ghost.move_process(game_map, pacman)
    for ghost in ghosts:
        if ghost.get_map_x() == pacman.get_map_x() and ghost.get_map_y() == pacman.get_map_y():
            handle_ghost_collision()
            break



def draw_game(pacman, ghosts, game_map):
    screen.fill(BLACK)
    draw_walls(screen, game_map)
    draw_foods(screen, game_map)
    for ghost in ghosts:
        ghost.draw(screen)
    pacman.draw(screen)
    draw_score_and_lives(screen)
    pygame.display.flip()




def handle_ghost_collision():
    global lives, pacman_obj, ghosts_obj, game_map
    lives -= 1
    pacman_obj = create_new_pacman()
    ghosts_obj = create_ghosts()
    if lives <= 0:
        print("Game Over! Final Score:", score)
        pygame.quit()
        sys.exit()
game_map = copy_map(game_map_layout)
pacman_obj = create_new_pacman()
ghosts_obj = create_ghosts()
running = True




while running:





    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                pacman_obj.next_direction = LEFT
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                pacman_obj.next_direction = RIGHT
            elif event.key in [pygame.K_UP, pygame.K_w]:
                pacman_obj.next_direction = UP
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                pacman_obj.next_direction = DOWN



    pacman_obj.update_animation(dt)
    update_game(pacman_obj, ghosts_obj, game_map)
    draw_game(pacman_obj, ghosts_obj, game_map)




pygame.quit()
