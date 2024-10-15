import pygame
from dataclasses import dataclass

BLACK = (0, 0, 0)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRAVITY = 0.5
GLIDE_GRAVITY = 0.05  # 글라이딩 할 때의 중력
JUMP_HEIGHT = 10

player_x, player_y = 500, 350
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

# 배경 레이어 로드
background_layers = [
    pygame.image.load('img/BG/1.png').convert_alpha(),  # 먼 배경
    pygame.image.load('img/BG/2.png').convert_alpha(),  # 중간 배경
    pygame.image.load('img/BG/4.png').convert_alpha()   # 가까운 배경
]

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

# 카메라 초기화
camera_x, camera_y = 0, 0

def update_camera(player_x, player_y):
    global camera_x, camera_y
    # 카메라를 플레이어 중앙에 맞추기
    camera_x = player_x - SCREEN_WIDTH // 2
    camera_y = player_y - SCREEN_HEIGHT // 2
    
    # 카메라가 맵의 범위를 넘어가지 않도록 제한 (여기서는 맵 크기를 2560x1440으로 가정)
    camera_x = max(0, min(camera_x, 2560 - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, 1440 - SCREEN_HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if jumping and event.key == pygame.K_a and pygame.time.get_ticks() - glide_enable_timer > 200 and not gliding:
                gliding = True

            if event.key == pygame.K_UP and not jumping:
                jumping = True
                glide_enable_timer = pygame.time.get_ticks()
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
                if not jumping and not moving_right:
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
                gliding = False

    # 오른쪽 이동을 우선적으로 처리
    if moving_right:
        player_x += player_speed
    elif moving_left:
        player_x -= player_speed

    if jumping:
        player_y += y_velocity
        if gliding:
            y_velocity += GLIDE_GRAVITY
        else:
            y_velocity += GRAVITY

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

    # 카메라 업데이트
    update_camera(player_x, player_y)

    # 화면을 지우고 배경 그리기
    screen.fill(BLACK)  # 화면을 지우기

    # 배경 레이어 그리기 (각 레이어마다 속도 조정)
    for i, layer in enumerate(background_layers):
        layer_scroll_speed = 1 + (i * 0.5)  # 레이어 속도 조정 (멀리 갈수록 느리게)
        screen.blit(layer, (-camera_x * layer_scroll_speed, -camera_y * layer_scroll_speed))

    # 플레이어를 카메라 위치에 맞춰 그리기
    screen.blit(final_player_image, (player_x - camera_x, player_y - camera_y))
    pygame.display.update()

    clock.tick(60)

pygame.quit()
