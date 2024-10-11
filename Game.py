import pygame, sys
import json
from pygame.locals import *

BLACK = (0, 0, 0)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

pygame.init()

key_file = 'key_data.json'

default_key_mapping = {
    "Left": pygame.K_LEFT,
    "Right": pygame.K_RIGHT,
    "Jump": pygame.K_UP,
    "Down": pygame.K_DOWN,
    "Gliding": pygame.K_a
}

# 키 이름을 pygame 키 코드로 변환하는 함수
def get_key_code(key_name):
    key_mapping = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "a": pygame.K_a,  # "Gliding"을 위한 매핑 추가
        # 추가적인 키 매핑이 필요하면 여기 추가
    }
    return key_mapping.get(key_name.lower(), None)  # 기본적으로 None 반환


# 키 매핑을 JSON 파일에 저장하는 함수
def save_key_mapping(key_mapping):
    with open(key_file, 'w') as f:
        # 각 키를 이름으로 변환하여 저장
        json.dump({"Keys": {k: pygame.key.name(v) for k, v in key_mapping.items()}}, f, indent=4)

def load_key_mapping():
    try:
        with open(key_file, 'r') as f:
            data = json.load(f)
            # 각 키의 값을 get_key_code를 사용하여 pygame 키 코드로 변환
            loaded_keys = {k: get_key_code(v) for k, v in data["Keys"].items()}

            # 모든 키가 존재하는지 확인하고 없으면 기본 매핑으로 설정
            for key in default_key_mapping.keys():
                if key not in loaded_keys or loaded_keys[key] is None:
                    loaded_keys[key] = default_key_mapping[key]  # 기본값으로 대체

            return loaded_keys
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading key mapping: {e}. Using default mapping.")
        return default_key_mapping  # 기본 키 매핑 반환



screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
Icon = pygame.image.load('img/Icon.png')
pygame.display.set_caption('Lucidian Dreamer')
pygame.display.set_icon(Icon)

Logo = pygame.image.load('img/Logo.png')
moon_image = pygame.image.load('img/BG/moon.png').convert_alpha()

scroll = [0] * 5
speeds = [1, 1.5, 2, 2.5, 3]

bg_images = []
bg_widths = []

for i in range(1, 6):
    bg_image = pygame.image.load(f"img/BG/{i}.png").convert_alpha()
    bg_images.append(bg_image)
    bg_widths.append(bg_image.get_width())

Selete = pygame.image.load('img/Slot/SlotSelete.png')  # 선택 오브젝트 이미지

def draw_bg(screen):
    for i in range(len(bg_images)):
        scroll[i] %= bg_widths[i]  # 각 배경의 스크롤 값을 조정함
        screen.blit(bg_images[i], (-scroll[i], 0))  # 배경 이미지 화면에 출력
        screen.blit(bg_images[i], (bg_widths[i] - scroll[i], 0))  # 두번째 배경 이미지를 화면에 출력
        if i == 0:
            screen.blit(moon_image, (0, 0))

def fade_in_bg_and_menu(screen, bg_images, moon_image, images, rects, duration, selected_index):
    clock = pygame.time.Clock()

    fade_bg_surfaces = [bg.copy().convert_alpha() for bg in bg_images]
    fade_menu_surfaces = [image.copy().convert_alpha() for image in images]
    moon_fade = moon_image.copy().convert_alpha()
    selete_fade = Selete.copy().convert_alpha()  # Selete 이미지 복사

    for alpha in range(0, 256, 5):
        screen.fill(BLACK)

        for i in range(len(fade_bg_surfaces)):
            fade_bg_surfaces[i].set_alpha(alpha)

            scroll[i] += speeds[i]
            scroll[i] %= bg_widths[i]

            screen.blit(fade_bg_surfaces[i], (-scroll[i], 0))
            screen.blit(fade_bg_surfaces[i], (bg_widths[i] - scroll[i], 0))
            if i == 0:
                moon_fade.set_alpha(alpha)
                screen.blit(moon_fade, (0, 0))

        for fade_menu_surface, rect in zip(fade_menu_surfaces, rects):
            fade_menu_surface.set_alpha(alpha)
            screen.blit(fade_menu_surface, rect)

        # Selete 이미지를 선택된 메뉴의 옆에 페이드 인
        selete_fade.set_alpha(alpha)
        selected_rect = rects[selected_index]
        selete_x = selected_rect.left - selete_fade.get_width() - 5
        selete_y = selected_rect.centery - selete_fade.get_height() // 2
        screen.blit(selete_fade, (selete_x, selete_y))

        pygame.display.update()
        clock.tick(duration)

def fade_in(screen, images, rects, duration, delay=0):
    clock = pygame.time.Clock()
    fade_surfaces = [image.copy().convert_alpha() for image in images]

    pygame.time.delay(delay)

    for alpha in range(0, 256, 5):
        screen.fill(BLACK)

        for fade_surface, rect in zip(fade_surfaces, rects):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, rect)

        pygame.display.update()
        clock.tick(duration)

def fade_out(screen, image, x, y, duration):
    clock = pygame.time.Clock()
    fade_surface = image.copy().convert_alpha()

    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))  # 화면을 검은색으로 채우기
        screen.blit(fade_surface, (x, y))
        pygame.display.update()
        clock.tick(duration)

def main_menu(screen):
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

    return images, Rects

def main():
    global scroll
    #메인 화면 및 반복 관련 bool
    running = True
    isMain = False
    Intro = False
    fade_done = False

    changing_key = False

    #게임 시스템 관련 bool
    SkipCutScene = False
    CutScene = False
    GameStart = False

    # 키 설정 변수들(이 값은 저장됨)
    key_mapping = load_key_mapping()
    LeftKey = key_mapping["Left"]
    RightKey = key_mapping["Right"]
    Jump = key_mapping["Jump"]
    DownKey = key_mapping["Down"]
    Gliding = key_mapping["Gliding"]
    #이 변수는 시간에 따라 사용될 수도 있고 지워질 수도 있음
    MagicKey = pygame.K_s

    images, rects = main_menu(screen)

    selected_index = 1  # Start 메뉴가 기본 선택
                        # 1 = Start
                        # 2 = Option
                        # 3 = Exit

    logo_width, logo_height = 320, 320
    logo_x = (SCREEN_WIDTH - logo_width) // 2
    logo_y = (SCREEN_HEIGHT - logo_height) // 2

    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if changing_key:  # 키 변경 모드 활성화 중
                    if selected_index == 2:  # 예를 들어, Option 메뉴에서 변경
                        DownKey = event.key
                        print(f"DownKey changed to: {pygame.key.name(DownKey)}")
                        # 업데이트된 키 매핑 저장
                        key_mapping["Down"] = DownKey
                        save_key_mapping(key_mapping)  # 변경된 키를 저장
                    changing_key = False  # 키 변경 완료 후 모드 해제
                else:
                    if not changing_key:
                        if event.key == DownKey:
                            selected_index += 1
                            if selected_index > 3:  # 마지막 메뉴에서 더 내려가면 Start로 돌아감
                                selected_index = 1
                        elif event.key == Jump:
                            selected_index -= 1
                            if selected_index < 1:  # 첫 메뉴에서 더 올라가면 Exit로 돌아감
                                selected_index = 3
                        elif event.key == pygame.K_z:
                            if selected_index == 1:
                                print("game Start")
                            elif selected_index == 2:
                                print("option")
                                isOption = True
                                changing_key = True
                            elif selected_index == 3:
                                running = False
                                pygame.quit()
                                sys.exit()

        if not Intro:
            fade_in(screen, [Logo], [(logo_x, logo_y)], 60)
            pygame.time.delay(2000)
            fade_out(screen, Logo, logo_x, logo_y, 60)
            Intro = True
            isMain = True
        elif isMain:
            if not fade_done:
                fade_in_bg_and_menu(screen, bg_images, moon_image, images, rects, 60, selected_index)
                fade_done = True
            else:
                draw_bg(screen)

            for i in range(len(scroll)):
                scroll[i] += speeds[i]
                if scroll[i] >= bg_widths[i]:
                    scroll[i] = 0

            for image, rect in zip(images, rects):
                screen.blit(image, rect)

            # Selete 오브젝트를 선택된 메뉴의 옆에 표시
            selected_rect = rects[selected_index]
            selete_x = selected_rect.left - Selete.get_width() - 5
            selete_y = selected_rect.centery - Selete.get_height() // 2
            screen.blit(Selete, (selete_x, selete_y))

        pygame.display.update()

    pygame.quit()
    sys.exit()


main()
