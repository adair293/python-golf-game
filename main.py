import pygame
import pymunk
import pymunk.pygame_util
 
pygame.init()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
 
pygame.display.set_caption("Golf")
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

#pymunk space
space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)

#clock
clock = pygame.time.Clock()
FPS = 120

dragging = False
drag_start = (0, 0)
IMPULSE_SCALING_FACTOR = 50

#load images
green_image = pygame.image.load("assets/Golf_green.png").convert_alpha()

#Hole params
HOLE_RADIUS = 28
HOLE_POS = (SCREEN_WIDTH - 150, SCREEN_HEIGHT / 2)

x = screen.get_width() / 2
y = screen.get_height() / 2

# define a variable to control the main loop
pygame.display.flip()

def draw_dotted_line(screen, start_pos, end_pos, color, width=1, dash_length=10):
    x_diff = end_pos[0] - start_pos[0]
    y_diff = end_pos[1] - start_pos[1]
    length = max(1, (x_diff**2 + y_diff**2)**0.5)
    x_dir, y_dir = x_diff / length, y_diff / length

    num_dashes = int(length / dash_length)
    
    for i in range(num_dashes):
        start_dash = (int(start_pos[0] + x_dir * i * dash_length),
                      int(start_pos[1] + y_dir * i * dash_length))
        
        end_dash = (int(start_dash[0] + x_dir * dash_length),
                    int(start_dash[1] + y_dir * dash_length))
        
        pygame.draw.line(screen, color, start_dash, end_dash, width)

def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8
    #use pivot joint to add friction
    pivot = pymunk.PivotJoint(static_body, body,(0,0), (0,0))
    pivot.max_bias = 0
    pivot.max_force = 1000

    space.add(body, shape, pivot)
    return shape

def create_wall(start, end, thickness):
    body = space.static_body  # Use the space's static body for walls
    shape = pymunk.Segment(body, start, end, thickness)
    shape.friction = 1.0  # This will add friction to the wall
    shape.elasticity = 0.8
    space.add(shape)
    return shape

def is_ball_in_hole(ball_pos, hole_pos, hole_radius):
    #check if ball is within the hole radius
    dx = ball_pos[0] - hole_pos[0]
    dy = ball_pos[1] - hole_pos[1]

    distance = (dx**2 + dy**2) ** 0.5
    return distance < hole_radius

golf_ball = create_ball(25, (500,500))

bottom_wall = create_wall((0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), 1)
left_wall = create_wall((0, 0), (0, SCREEN_HEIGHT), 1)
right_wall = create_wall((SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), 1)
top_wall = create_wall((0, 0), (SCREEN_WIDTH, 0), 1)

# game loop
running = True
while running:

    clock.tick(FPS)
    space.step(1 / FPS)

    #draw golf green
    screen.blit(green_image, (0,0))

    # Draw Hole
    pygame.draw.circle(screen, (0, 0, 0), HOLE_POS, HOLE_RADIUS)
    pygame.draw.circle(screen, (150, 150, 150), HOLE_POS, HOLE_RADIUS - 5)

    # Draw golf ball
    pygame.draw.circle(screen, (255, 255, 255), (int(golf_ball.body.position.x), int(golf_ball.body.position.y)), 25)

    #check if ball is in hole
    if is_ball_in_hole(golf_ball.body.position, HOLE_POS, HOLE_RADIUS):
        golf_ball.body.position = (500, 500)
        golf_ball.body.velocity = (0, 0)

    #event handler
    for event in pygame.event.get():
        if dragging:
            draw_dotted_line(screen, golf_ball.body.position, pygame.mouse.get_pos(), (0, 0, 0), width=2)
        if event.type == pygame.MOUSEBUTTONDOWN:
            drag_start = pygame.mouse.get_pos()
            dragging = True
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            drag_end = pygame.mouse.get_pos()
            x_impulse = (drag_start[0] - drag_end[0]) * IMPULSE_SCALING_FACTOR
            y_impulse = (drag_start[1] - drag_end[1]) * IMPULSE_SCALING_FACTOR
            golf_ball.body.apply_impulse_at_local_point((x_impulse, y_impulse), (0,0))
            dragging = False
        if event.type == pygame.QUIT:
            running = False

    #space.debug_draw(draw_options)
    pygame.display.update()