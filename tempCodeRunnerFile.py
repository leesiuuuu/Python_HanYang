import pygame
from dataclasses import dataclass

BLACK = (0, 0, 0)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRAVITY = 0.5
GLIDE_GRAVITY = 0.05  # 글라이딩 할 때의 중력
JUMP_HEIGHT = 10

player_x, player_y = 500, 500
ground_y = player_y
player_speed = 3
moving_left = False
moving_right = False
facing_right = True

pygame.init()

@dataclass
class Animation:
    frame_width: int = 48
    frame_height: int = 48
    frame_count: list = None
    current_frame: int = 0
    animation_speed: int = 100
    state: int = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
Icon = pygame.image.load('img/Icon.png')
pygame.display.set_caption('Lucidian Dreamer')
pygame.display.set_icon(Icon)

player_sheet = pygame.image.load('Sprite/Mei-Sheet.png').convert_alpha()
player_animation = Animation()
player_animation.frame_count = [6, 10, 3, 3, 3, 3, 4]
last_update = pygame.time.get_ticks()
clock = pygame.time.Clock()

y_velocity = 0
jumping = False
gliding = False
jumptofall_timer = 0
glide_enable_timer = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # 글라이딩 가능 시간 체크
            if jumping and event.key == pygame.K_a and pygame.time.get_ticks() - glide_enable_timer > 200 and not gliding:
                gliding = True

            if event.key == pygame.K_UP and not jumping:
                jumping = True
                glide_enable_timer = pygame.time.get_ticks()  # 점프 시작 시간 기록
                y_velocity = -JUMP_HEIGHT
                player_animation.state = 2
                player_animation.current_frame = 0

            if event.key == pygame.K_RIGHT:
                moving_left = False
                moving_right = True
                if not jumping:
                    player_animation.state = 1
                    player_animation.current_frame = 0
                facing_right = True

            if event.key == pygame.K_LEFT:
                moving_right = False
                moving_left = True
                if not jumping and not moving_right:  # 오른쪽으로 이동 중일 때 왼쪽 애니메이션 상태 유지 안 함
                    player_animation.state = 1
                    player_animation.current_frame = 0
                if not moving_right:
                    facing_right = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                glide_enable_timer = 0
            if event.key == pygame.K_LEFT:
                moving_left = False
                if not moving_right and not jumping:
                    player_animation.state = 0

            if event.key == pygame.K_RIGHT:
                moving_right = False
                if not moving_left and not jumping:
                    player_animation.state = 0

            if event.key == pygame.K_a:
                gliding = False  # A 키를 떼면 글라이딩을 중지

    # 오른쪽 이동을 우선적으로 처리
    if moving_right:
        player_x += player_speed
    elif moving_left:
        player_x -= player_speed

    if jumping:
        player_y += y_velocity
        if gliding:
            y_velocity += GLIDE_GRAVITY  # 글라이딩 중일 때 중력을 줄임
        else:
            y_velocity += GRAVITY  # 일반 중력

        if y_velocity > 0 and player_animation.state == 2:
            player_animation.state = 3
            player_animation.current_frame = 0
            jumptofall_timer = pygame.time.get_ticks()

        if player_animation.state == 3:
            if pygame.time.get_ticks() - jumptofall_timer > 200:
                player_animation.state = 4
                player_animation.current_frame = 0
                
        if player_y >= ground_y:
            player_y = ground_y
            jumping = False
            y_velocity = 0
            glide_enable_timer = 0
            gliding = False
            
            if moving_left or moving_right:
                player_animation.state = 1
                player_animation.current_frame = 0
            else:
                player_animation.state = 0
                player_animation.current_frame = 0

            last_update = pygame.time.get_ticks()

    now = pygame.time.get_ticks()
    if now - last_update > player_animation.animation_speed:
        player_animation.current_frame = (player_animation.current_frame + 1) % player_animation.frame_count[player_animation.state]
        last_update = now

    player_rect = pygame.Rect(
        player_animation.current_frame * player_animation.frame_width,
        player_animation.state * player_animation.frame_height,
        player_animation.frame_width,
        player_animation.frame_height
    )

    current_frame_surface = player_sheet.subsurface(player_rect)

    if facing_right:
        final_player_image = current_frame_surface
    else:
        final_player_image = pygame.transform.flip(current_frame_surface, True, False)

    screen.fill(BLACK)
    screen.blit(final_player_image, (player_x, player_y))
    pygame.display.update()

    clock.tick(60)

pygame.quit()
