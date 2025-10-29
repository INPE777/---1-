import pygame
import math
import sys
from collections import deque

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
FPS = 60

BPM = 90
BEAT_LENGTH = 60.0 / BPM
NOTE_TRAVEL_TIME = 1.4

HIT_WINDOW_PERFECT = 0.10
HIT_WINDOW_GOOD = 0.20
arrow_angle = 0
defeat_music_played = False

# ------------------------------------------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project Rhombus - Python Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 60)

WHITE = (255,255,255)
BG = (15,15,20)

# ------------------------------------------------------------
# "이부분 고쳐야 한다" (이미지 커스터마이즈 구간)
# ------------------------------------------------------------

def load_scaled(name, size=None):
    try:
        img = pygame.image.load(name).convert_alpha() #알파 채널 유지- 투명도
        if size:
            img = pygame.transform.scale(img, size)
        return img

    except:
        return None

# 배경
background_img = load_scaled("bg.png", (WIDTH, HEIGHT))

# 중앙
center_img = load_scaled("center.png", (160,160))

#중앙 화살표
center_arrow_img = load_scaled("img/center_arrow.png", (80,80))

# 노트
note_img = load_scaled("note.png", (40,40))

# 라이프 (단일 교체형)
life_imgs = [
    load_scaled("life3.png", (100,100)),
    load_scaled("life2.png", (100,100)),
    load_scaled("life1.png", (100,100))
]

# 디피트 이미지
defeat_img = load_scaled("defeat.png", (400,200))

# ---------------------- SFX ----------------------

defeat_sfx =pygame.mixer.music.load("sfx/defeat.wav")

# WASD 매핑
KEYS = [pygame.K_a, pygame.K_s, pygame.K_w, pygame.K_d]
KEY_NAMES = ["A", "S", "W", "D"]

TARGET_RADIUS = 80
SPAWN_RADIUS = 330
NOTE_RADIUS = 18

# ------------------------------------------------------------
# 노트 클래스
# ------------------------------------------------------------
class Note:
    def __init__(self, direction:int, time:float):
        self.direction = direction
        self.time = time
        self.hit = False
        self.missed = False

# ------------------------------------------------------------
# 노트 패턴 (1~2개/s 수준)
# ------------------------------------------------------------
sample_pattern = [
    (0,0),(1,2),
    (2,1),(3,3),
    (4,0),(5,2),
    (6,3),(7,1),
    (8,0),(9,2),
    (10,3),(11,1),
    (12,0),(13,2),
    (14,1),(15,3)
]

def build_note_list(pattern):
    q = deque()
    for beat, dir_idx in pattern:
        q.append(Note(dir_idx, beat * BEAT_LENGTH))
    return q

def direction_angle(d):
    mapping = {0: math.pi, 1: math.pi/2, 2: -math.pi/2, 3: 0}
    return mapping[d]

def polar_to_xy(angle, r):
    return int(CENTER[0] + math.cos(angle)*r), int(CENTER[1] + math.sin(angle)*r)

# ------------------------------------------------------------
# 게임 상태 초기화 함수
# ------------------------------------------------------------
def reset_game():
    global notes, active_notes, score, combo, max_combo, last_judge
    global last_judge_timer, start_ticks, pulse_timer, life, defeat
    global defeat_music_played

    notes = build_note_list(sample_pattern)
    active_notes = []

    score = 0
    combo = 0
    max_combo = 0
    last_judge = ""
    last_judge_timer = 0
    start_ticks = None
    pulse_timer = 0.0
    life = 3
    defeat = False
    arrow_angle = 0
    defeat_music_played = False
    # 나중에 음악 넣을 때 여기서 재생
    # pygame.mixer.music.load("song.mp3")
    # pygame.mixer.music.play(0)

reset_game()

# ------------------------------------------------------------
def get_time():
    if start_ticks is None:
        return 0
    return (pygame.time.get_ticks() - start_ticks) / 1000

def spawn_note(note):
    active_notes.append(note)

# ------------------------------------------------------------
# 판정 처리
# ------------------------------------------------------------
def judge(n, t):
    global score, combo, max_combo, last_judge, last_judge_timer, pulse_timer
    dt = abs(n.time - t)
    if dt <= HIT_WINDOW_PERFECT:
        score += 300
        combo += 1
        last_judge = "PERFECT"
        last_judge_timer = 0.6
        pulse_timer = 0.25  # 중앙 이미지 효과
    elif dt <= HIT_WINDOW_GOOD:
        score += 150
        combo += 1
        last_judge = "GOOD"
        last_judge_timer = 0.6
    else:
        return False
    max_combo = max(max_combo, combo)
    n.hit = True
    return True

# ------------------------------------------------------------
# 메인 루프
# ------------------------------------------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN and defeat:
                reset_game()
                continue

            if start_ticks is None and e.key == pygame.K_SPACE:
                start_ticks = pygame.time.get_ticks()
            if not defeat and start_ticks is not None and e.key in KEYS:
                press_time = get_time()
                dir_idx = KEYS.index(e.key)

                # 화살표 회적 각도
                if e.key == pygame.K_w:
                    arrow_angle = 0
                elif e.key == pygame.K_s:
                    arrow_angle = 180
                elif e.key == pygame.K_a:
                    arrow_angle = -90
                elif e.key == pygame.K_d:
                    arrow_angle = 90

                candidate = None
                best = 999
                for n in active_notes:
                    if n.direction == dir_idx and not n.hit and not n.missed:
                        d = abs(n.time - press_time)
                        if d < best:
                            best = d; candidate = n
                if candidate:
                    ok = judge(candidate, press_time)
                    if not ok:
                        combo = 0
                        last_judge = "MISS"
                        last_judge_timer = 0.5
                        life -= 1
                        if life <= 0:
                            defeat = True

    # --- 배경 ---
    if background_img:
        screen.blit(background_img, (0,0))
    else:
        screen.fill(BG)

    if defeat:
        # DEFEAT 화면
        if not defeat_music_played:
            pygame.mixer.music.load("sfx/defeat.wav")
            pygame.mixer.music.play()
            defeat_music_played = True

        if defeat_img:
            rect = defeat_img.get_rect(center=CENTER)
            screen.blit(defeat_img, rect)
        else:
            txt = big_font.render("DEFEAT", True, (255,60,60))
            screen.blit(txt, txt.get_rect(center=CENTER))
        sub = font.render("Press ENTER to Restart", True, WHITE)
        screen.blit(sub, sub.get_rect(center=(CENTER[0], CENTER[1]+100)))
        pygame.display.flip()
        continue

    # --- 노트 생성 ---
    t = get_time()
    if start_ticks:
        while notes and notes[0].time - NOTE_TRAVEL_TIME <= t:
            spawn_note(notes.popleft())

    # -- 중앙 화살표 그리기 --
    if center_arrow_img:
        scale = 1.0
        img_w = int(80 * scale)
        img_h = int(80 * scale)
        scaled = pygame.transform.scale(center_arrow_img, (img_w, img_h))

        rotated_arrow = pygame.transform.rotate(scaled, -arrow_angle)
        rect = rotated_arrow.get_rect(center=CENTER)
        screen.blit(rotated_arrow, rect)

    # --- 중앙 그리기 (PERFECT 효과 포함) ---
    if center_img:
        scale = 1.0
        if pulse_timer > 0:
            scale = 1.0 + pulse_timer * 1.5
            pulse_timer -= dt

        img_w = int(160 * scale)
        img_h = int(160 * scale)
        scaled = pygame.transform.scale(center_img, (img_w, img_h))
        rect = scaled.get_rect(center=CENTER)
        screen.blit(scaled, rect)
    else:
        pygame.draw.circle(screen, WHITE, CENTER, TARGET_RADIUS, 5)




    # --- 노트 이동 + 회전 그리기 ---
    for n in list(active_notes):
        if n.hit:
            active_notes.remove(n)
            continue
        if t > n.time + HIT_WINDOW_GOOD:
            n.missed = True
            combo = 0
            last_judge = "MISS"
            last_judge_timer = 0.5
            life -= 1
            if life <= 0:
                defeat = True
            active_notes.remove(n)
            continue

        prog = max(0, min(1, (n.time - t) / NOTE_TRAVEL_TIME))
        r = TARGET_RADIUS + (SPAWN_RADIUS - TARGET_RADIUS)*prog
        angle = direction_angle(n.direction)
        x,y = polar_to_xy(angle, r)

        if note_img:
            dx = CENTER[0] - x
            dy = CENTER[1] - y
            angle_deg = math.degrees(math.atan2(dy, dx))
            rotated = pygame.transform.rotate(note_img, -angle_deg)
            rect = rotated.get_rect(center=(x,y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (200,200,80), (x,y), NOTE_RADIUS)

    # --- HUD ---
    hud = font.render(f"SCORE:{score}  COMBO:{combo}", True, WHITE)
    screen.blit(hud,(20,20))

    # --- 라이프 표시 (단일 교체형) ---
    if life > 0 and life <= 3:
        life_img = life_imgs[life-1]
        if life_img:
            rect = life_img.get_rect(topright=(WIDTH-20, 20))
            screen.blit(life_img, rect)
        else:
            # 이미지 없으면 텍스트로 표시
            txt = font.render(f"LIFE:{life}", True, WHITE)
            screen.blit(txt, (WIDTH-120, 20))

    # --- 판정 텍스트 ---
    if last_judge_timer>0:
        txt = big_font.render(last_judge, True, WHITE)
        screen.blit(txt, txt.get_rect(center=(CENTER[0],CENTER[1]-160)))
        last_judge_timer -= dt

    pygame.display.flip()

pygame.quit()
sys.exit()
