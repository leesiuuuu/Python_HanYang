import pygame, sys
from pygame.locals import *

BLACK = (0, 0, 0)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

#페이드 인 애니메이션 재생
def fade_in(screen, images, rects, duration, delay=0):
    clock = pygame.time.Clock()

    # 이미지별 페이드 서페이스 준비
    fade_surfaces = [image.copy().convert_alpha() for image in images]

    pygame.time.delay(delay)

    for alpha in range(0, 256, 5):
        screen.fill(BLACK)

        for fade_surface, rect in zip(fade_surfaces, rects):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, rect)

        pygame.display.update()
        clock.tick(duration)

# 페이드 아웃 애니메이션 재생
def fade_out(screen, image, x, y, duration):
    clock = pygame.time.Clock()
    fade_surface = image.copy()
    fade_surface = fade_surface.convert_alpha()

    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))  # 화면을 검은색으로 채우기
        screen.blit(fade_surface, (x, y))
        pygame.display.update()
        clock.tick(duration)

def main_menu(screen, fade_done):
    screen.fill(BLACK)

    Title = pygame.image.load('img/Title1.png')
    Start = pygame.image.load('img/Slot/Slot1.png')
    Option = pygame.image.load('img/Slot/Slot2.png')
    Exit = pygame.image.load('img/Slot/Slot3.png')

    screen_width, screen_height = screen.get_size()

    Title_rect = Title.get_rect(center=(screen_width // 2, screen_height // 5))
    button_gap = 20  # 텍스트 간격 설정

    Start_rect = Start.get_rect(center=(screen_width // 2, screen_height // 2))
    Option_rect = Option.get_rect(center=(screen_width // 2, Start_rect.bottom + button_gap))
    Exit_rect = Exit.get_rect(center=(screen_width // 2, Option_rect.bottom + button_gap + 10))

    images = [Title, Start, Option, Exit]
    Rects = [Title_rect, Start_rect, Option_rect, Exit_rect]

    if not fade_done:
        fade_in(screen, images, Rects, 60, delay=0)
    else:
        for images, Rects in zip(images, Rects):
            screen.blit(images, Rects)

    pygame.display.update()

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    Icon = pygame.image.load('img/Icon.png')
    pygame.display.set_caption('Lucidian Dreamer')
    pygame.display.set_icon(Icon)

    Logo = pygame.image.load('img/Logo.png')

    running = True
    isMain = False
    Intro = False
    fade_done = False

    logo_width, logo_height = 320, 320
    logo_x = (SCREEN_WIDTH - logo_width) // 2
    logo_y = (SCREEN_HEIGHT - logo_height) // 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC를 누르면 종료
                    running = False
                    pygame.quit()
                    sys.exit()
        if Intro == False:
            fade_in(screen, [Logo], [(logo_x, logo_y)], 60)
            pygame.time.delay(2000)
            fade_out(screen, Logo, logo_x, logo_y, 60)
            Intro = True
            isMain = True
        elif isMain == True:
            main_menu(screen, fade_done)
            fade_done = True

        pygame.display.update()

    pygame.quit()
    sys.exit()

main()
