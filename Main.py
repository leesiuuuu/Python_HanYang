import pygame
import random
from dataclasses import dataclass

BLACK = (0, 0, 0)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRAVITY = 0.8
GLIDE_GRAVITY = 0.05
JUMP_HEIGHT = 15
MOVE_SPEED = 4
CAMERA_FOLLOW_SPEED = 0.05

pygame.init()

@dataclass
class Animation:
    frame_width: int = 48
    frame_height: int = 48
    frame_count: list = None
    current_frame: int = 0
    animation_speed: int = 100
    state: int = 0

class Player:
    def __init__(self, x, y, ground_y, scale=3):
        self.x = x
        self.y = y
        self.ground_y = ground_y
        self.speed = MOVE_SPEED
        self.scale = scale
        self.facing_right = True
        self.moving_left = False
        self.moving_right = False
        self.jumping = False
        self.gliding = False
        self.y_velocity = 0
        self.jumptofall_timer = 0
        self.glide_enable_timer = 0
        self.animation = Animation(frame_count=[6, 10, 3, 3, 3, 3, 4])
        self.sheet = pygame.image.load('Sprite/Mei-Sheet.png').convert_alpha()
        self.last_update = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event.key)

    def handle_keydown(self, key):
        if key == pygame.K_a:
            self.start_glide()
        elif key == pygame.K_UP:
            self.start_jump()
        elif key == pygame.K_RIGHT:
            self.move_right()
        elif key == pygame.K_LEFT:
            self.move_left()

    def handle_keyup(self, key):
        if key == pygame.K_a:
            self.stop_glide()
        elif key == pygame.K_LEFT:
            self.stop_move_left()
        elif key == pygame.K_RIGHT:
            self.stop_move_right()

    def start_jump(self):
        if not self.jumping:
            self.jumping = True
            self.glide_enable_timer = pygame.time.get_ticks()
            self.y_velocity = -JUMP_HEIGHT
            self.animation.state = 2
            self.animation.current_frame = 0

    def start_glide(self):
        if self.jumping and pygame.time.get_ticks() - self.glide_enable_timer > 200 and not self.gliding:
            self.gliding = True

    def stop_glide(self):
        self.gliding = False

    def move_right(self):
        self.moving_left = False
        self.moving_right = True
        if not self.jumping:
            self.animation.state = 1
            self.animation.current_frame = 0
        self.facing_right = True

    def stop_move_right(self):
        self.moving_right = False
        if not self.moving_left and not self.jumping:
            self.animation.state = 0

    def move_left(self):
        self.moving_right = False
        self.moving_left = True
        if not self.jumping and not self.moving_right:
            self.animation.state = 1
            self.animation.current_frame = 0
        self.facing_right = False

    def stop_move_left(self):
        self.moving_left = False
        if not self.moving_right and not self.jumping:
            self.animation.state = 0
    
    def start_fall(self):
        # 플레이어가 하강할 때의 애니메이션 및 상태 처리
        if self.y_velocity > 0 and self.animation.state == 2:
            self.animation.state = 3  # 점프에서 낙하 상태로 변경
            self.animation.current_frame = 0
            self.jumptofall_timer = pygame.time.get_ticks()

        # 일정 시간 이후에 낙하 상태에서 다른 상태로 변경 (ex: 착지 준비 상태)
        if self.animation.state == 3:
            if pygame.time.get_ticks() - self.jumptofall_timer > 200:
                self.animation.state = 4  # 착지 상태로 변경
                self.animation.current_frame = 0
    
    def stop_fall(self):
        # 플레이어가 착지했을 때 호출되는 메서드
        self.jumping = False
        self.y_velocity = 0
        self.glide_enable_timer = 0
        self.gliding = False

        # 이동 중일 경우 걷는 애니메이션, 그렇지 않으면 대기 애니메이션으로 전환
        if self.moving_left or self.moving_right:
            self.animation.state = 1  # 걷는 상태
            self.animation.current_frame = 0
        else:
            self.animation.state = 0  # 대기 상태
            self.animation.current_frame = 0

    def update(self):
        if self.moving_right:
            self.x += self.speed
        elif self.moving_left:
            self.x -= self.speed

        if self.jumping:
            self.y += self.y_velocity
            if self.gliding:
                self.y_velocity += GLIDE_GRAVITY
            else:
                self.y_velocity += GRAVITY

            # 하강 처리 함수 호출
            self.start_fall()

            # 플레이어가 땅에 닿았을 때 낙하를 멈춤
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.stop_fall()  # stop_fall 메서드 호출

    def draw(self, screen, camera_x, camera_y):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation.animation_speed:
            self.animation.current_frame = (self.animation.current_frame + 1) % self.animation.frame_count[self.animation.state]
            self.last_update = now

        player_rect = pygame.Rect(
            self.animation.current_frame * self.animation.frame_width,
            self.animation.state * self.animation.frame_height,
            self.animation.frame_width,
            self.animation.frame_height
        )

        current_frame_surface = self.sheet.subsurface(player_rect)

        if self.facing_right:
            final_player_image = current_frame_surface
        else:
            final_player_image = pygame.transform.flip(current_frame_surface, True, False)

        final_player_image = pygame.transform.scale(
            final_player_image,
            (int(self.animation.frame_width * self.scale), int(self.animation.frame_height * self.scale))
        )

        screen.blit(final_player_image, (self.x - camera_x, self.y - camera_y))

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.duration = 0
        self.intensity = 0
        self.timer = 0
    # Lerp 를 구현한 함수
    def lerp(self, start, end, factor):
        return start + (end - start) * factor
    # 카메라 흔들림
    def Shake(self, duration, intensity):
        self.duration = duration
        self.intensity = intensity
        self.timer = 0

    def update(self, player_x, player_y):
        target_x = player_x - SCREEN_WIDTH // 2
        target_y = player_y - SCREEN_HEIGHT // 2
        
        #만약 흔들림이 켜졌을 때
        if self.duration > 0:
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)

            self.x = self.lerp(self.x, target_x + offset_x, CAMERA_FOLLOW_SPEED)
            self.y = self.lerp(self.y, target_y + offset_y, CAMERA_FOLLOW_SPEED)

            # 흔들림 타이머
            self.timer += pygame.time.get_ticks()
            if self.timer >= self.duration:
                self.duration = 0
                self.timer = 0
        # 카메라의 움직임을 부드럽게 구현하기 위한 Lerp 사용
        self.x = self.lerp(self.x, target_x, CAMERA_FOLLOW_SPEED)
        self.y = self.lerp(self.y, target_y, CAMERA_FOLLOW_SPEED)

        # X, Y 좌표를 화면 경계 내로 제한
        self.x = max(0, min(self.x, self.width - SCREEN_WIDTH))
        self.y = max(0, min(self.y, self.height - SCREEN_HEIGHT))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Lucidian Dreamer')
        self.icon = pygame.image.load('img/Icon.png')
        pygame.display.set_icon(self.icon)

        # 배경 이미지 생성
        self.background_layers = [
            pygame.image.load('img/BG/1.png').convert_alpha(),
            pygame.image.load('img/BG/2.png').convert_alpha(),
            pygame.image.load('img/BG/4.png').convert_alpha()
        ]

        self.player = Player(700, 700, 700)
        self.camera = Camera(3000, 1740)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.player.handle_event(event)

            self.player.update()
            self.camera.update(self.player.x, self.player.y)

            self.screen.fill(BLACK)
            # 배경 레이어를 화면에 그리는 부분을 수정합니다.
            for i, layer in enumerate(self.background_layers):
                layer_scroll_speed = 1 + (i * 0.5)  # 각 레이어의 스크롤 속도 설정
                # 각 레이어의 위치를 카메라 위치에 따라 계산
                layer_x = -self.camera.x * layer_scroll_speed
                layer_y = -self.camera.y * layer_scroll_speed

                # 레이어의 위치를 화면에 그립니다.
                self.screen.blit(layer, (layer_x, layer_y))

                # 만약 배경 레이어가 반복되어야 한다면 추가적인 조건을 추가할 수 있습니다.
                if layer_x < -layer.get_width():
                    self.screen.blit(layer, (layer_x + layer.get_width(), layer_y))


            self.player.draw(self.screen, self.camera.x, self.camera.y)
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
if __name__ == "__main__":
    game = Game()
    game.run()
