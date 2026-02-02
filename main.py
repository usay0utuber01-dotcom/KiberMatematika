import pygame
import random
import os

# --- SOZLAMALAR ---
WIDTH, HEIGHT = 550, 750
FPS = 60

# --- RANG LAR (FAQAT QORA VA YASHIL) ---
BLACK = (0, 0, 0)           # To'liq qora fon
GREEN = (0, 255, 0)         # Yorqin neon yashil yozuvlar
DARK_GREEN = (0, 50, 0)     # Bloklar uchun to'q yashil
CARD_COLOR = (0, 20, 0)     # Panel rangi (juda to'q yashil)
WHITE = (255, 255, 255)     # Tugma ichidagi matnlar uchun oq
GRAY = (40, 40, 40)         # Menu tugmasi uchun

class GameApp:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Kiber Matematika: Green Edition")
        self.clock = pygame.time.Clock()
        
        # Shriftlar (Qalin va yashil uslubda)
        self.font_main = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_res = pygame.font.SysFont("Arial", 38, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
        
        # OVOZLAR
        self.sounds = {}
        sound_map = {
            "click": "tugma.wav",
            "correct": "bosqichgalaba.wav",
            "win": "asosiygalaba.wav",
            "lose": "yutqazish.wav"
        }
        
        for key, fileName in sound_map.items():
            if os.path.exists(fileName):
                try:
                    self.sounds[key] = pygame.mixer.Sound(fileName)
                    self.sounds[key].set_volume(0.9)
                except: self.sounds[key] = None
            else: self.sounds[key] = None

        self.state = "MENU"
        self.last_state_change = 0
        self.reset_math()

    def play_sound(self, key):
        if self.sounds.get(key):
            self.sounds[key].stop()
            self.sounds[key].play()

    def draw_glass_rect(self, rect, color, alpha=180, radius=20):
        # Shaffof yashil bloklar
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=radius)
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(self.screen, GREEN, rect, 3, border_radius=radius) # Yashil ramka

    def reset_math(self):
        self.level = 1
        self.total_questions = 0
        self.correct_answers = 0
        self.m_game_over = False
        self.level_complete = False
        self.new_math_question()

    def new_math_question(self):
        self.total_questions += 1
        cfg = {1:(1,12,['+']), 2:(10,50,['+','-']), 3:(2,12,['*']), 4:(20,150,['+','-','*']), 5:(100,500,['+','-','*'])}
        l, h, ops = cfg[self.level]
        a, b, op = random.randint(l,h), random.randint(l,h), random.choice(ops)
        self.ans = a+b if op=='+' else (a-b if op=='-' else a*b)
        self.q_text = f"{a} {op} {b} = ?"
        
        answers = [self.ans]
        while len(answers) < 5:
            w = self.ans + random.randint(-20, 20)
            if w != self.ans and w not in answers: answers.append(w)
        random.shuffle(answers)
        
        self.options = [{'rect': pygame.Rect(WIDTH//2-140, 240+(i*78), 280, 65), 'val': v} for i, v in enumerate(answers)]
        self.m_start_time = pygame.time.get_ticks()
        self.m_timer = max(2000, 7000 - (self.level * 800))

    def play_math(self, events):
        self.screen.fill(BLACK) # Qora fon
        
        # YUQORI PANEL
        pygame.draw.rect(self.screen, CARD_COLOR, (0, 0, WIDTH, 120))
        
        q_count_txt = f"SAVOL: {self.total_questions} / 15"
        q_surf = self.font_main.render(q_count_txt, True, GREEN) # Yashil yozuv
        self.screen.blit(q_surf, q_surf.get_rect(center=(WIDTH//2, 45)))
        
        l_surf = self.font_small.render(f"BOSQICH: {self.level}", True, GREEN)
        self.screen.blit(l_surf, l_surf.get_rect(center=(WIDTH//2, 90)))

        ex_btn = pygame.Rect(20, 35, 100, 50)
        self.draw_glass_rect(ex_btn, DARK_GREEN, 150, 12)
        m_txt = self.font_small.render("MENU", True, WHITE)
        self.screen.blit(m_txt, m_txt.get_rect(center=ex_btn.center))

        if not self.m_game_over and not self.level_complete:
            elapsed = pygame.time.get_ticks() - self.m_start_time
            rem_pct = max(0, (self.m_timer - elapsed) / self.m_timer)
            
            # SAVOL MATNI
            q_s = self.font_big.render(self.q_text, True, GREEN)
            self.screen.blit(q_s, q_s.get_rect(center=(WIDTH//2, 185)))
            
            # VARIANTLAR
            for opt in self.options:
                self.draw_glass_rect(opt['rect'], DARK_GREEN, 180)
                txt = self.font_main.render(str(opt['val']), True, WHITE)
                self.screen.blit(txt, txt.get_rect(center=opt['rect'].center))
            
            # TAYMER
            pygame.draw.rect(self.screen, DARK_GREEN, (60, HEIGHT-60, WIDTH-120, 16), border_radius=8)
            pygame.draw.rect(self.screen, GREEN, (60, HEIGHT-60, (WIDTH-120)*rem_pct, 16), border_radius=8)
            
            if elapsed >= self.m_timer: 
                self.m_game_over = True; self.play_sound("lose")
            
            if pygame.time.get_ticks() - self.last_state_change > 300:
                for e in events:
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self.play_sound("click")
                        if ex_btn.collidepoint(e.pos):
                            self.state = "MENU"; self.last_state_change = pygame.time.get_ticks()
                        for opt in self.options:
                            if opt['rect'].collidepoint(e.pos):
                                if opt['val'] == self.ans:
                                    self.correct_answers += 1
                                    if self.total_questions >= 15:
                                        if self.correct_answers >= 10: self.level_complete = True; self.play_sound("correct")
                                        else: self.m_game_over = True; self.play_sound("lose")
                                    else: self.new_math_question()
                                else: self.m_game_over = True; self.play_sound("lose")
        else: self.show_math_result(events)

    def show_math_result(self, events):
        res_rect = pygame.Rect(WIDTH//2-250, HEIGHT//2-150, 500, 300)
        self.draw_glass_rect(res_rect, CARD_COLOR, 245)
        
        txt = "G'ALABA!" if self.level_complete else "YUTQAZDINGIZ!"
        msg_s = self.font_res.render(txt, True, GREEN)
        self.screen.blit(msg_s, msg_s.get_rect(center=(WIDTH//2, HEIGHT//2-65)))
        
        stat_s = self.font_main.render(f"Natija: {self.correct_answers}/15", True, GREEN)
        self.screen.blit(stat_s, stat_s.get_rect(center=(WIDTH//2, HEIGHT//2)))

        btn = pygame.Rect(WIDTH//2-170, HEIGHT//2+65, 340, 75)
        self.draw_glass_rect(btn, DARK_GREEN)
        btn_txt = "DAVOM ETISH" if self.level_complete else "QAYTA BOSHLASH"
        txt_surf = self.font_main.render(btn_txt, True, WHITE)
        self.screen.blit(txt_surf, txt_surf.get_rect(center=btn.center))
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(e.pos):
                self.play_sound("click")
                if self.level_complete:
                    if self.level < 5: 
                        self.level += 1; self.total_questions = 0; self.correct_answers = 0
                        self.level_complete = False; self.new_math_question()
                        self.last_state_change = pygame.time.get_ticks()
                    else: self.play_sound("win"); self.state = "MENU"; self.reset_math()
                else: 
                    self.reset_math()
                    self.last_state_change = pygame.time.get_ticks()

    def run(self):
        while True:
            evs = pygame.event.get()
            for e in evs:
                if e.type == pygame.QUIT: return
                if self.state == "MENU" and e.type == pygame.MOUSEBUTTONDOWN:
                    play_btn = pygame.Rect(WIDTH//2-170, 400, 340, 95)
                    if play_btn.collidepoint(e.pos):
                        self.play_sound("click")
                        self.state = "MATH"; self.last_state_change = pygame.time.get_ticks()

            if self.state == "MENU":
                self.screen.fill(BLACK)
                # Matrix-uslubidagi sarlavha
                t_s = self.font_big.render("KIBER MATEMATIKA", True, GREEN)
                self.screen.blit(t_s, t_s.get_rect(center=(WIDTH//2, 250)))
                
                play_btn = pygame.Rect(WIDTH//2-170, 400, 340, 95)
                self.draw_glass_rect(play_btn, DARK_GREEN, alpha=230)
                b_txt = self.font_main.render("O'YINNI BOSHLASH", True, WHITE)
                self.screen.blit(b_txt, b_txt.get_rect(center=play_btn.center))
            
            elif self.state == "MATH":
                self.play_math(evs)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    GameApp().run()