import pygame
import random
import time

# ====================================================================
# 1. CONSTANTS (ค่าคงที่)
# ====================================================================

# การตั้งค่ากระดานและวัตถุ
SHAPES = ['Triangle', 'Square', 'Circle', 'Pentagon', 'Star', 'Diamond']
COLORS = {'Triangle': 'RED', 'Square': 'BLUE', 'Circle': 'PINK', 'Pentagon': 'YELLOW', 'Star': 'PURPLE', 'Diamond': 'WHITE'}

GRID_WIDTH = 12
GRID_HEIGHT = 22 # 2 แถวบนสุดใช้สำหรับ Spawn

# การตั้งค่า Pygame และการแสดงผล
BLOCK_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + 300 
SCREEN_HEIGHT = (GRID_HEIGHT - 2) * BLOCK_SIZE + 150 

# สี RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
DARK_RED = (150, 0, 0)
PINK = (255, 105, 180)

COLOR_MAP = {
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'PINK': (255, 105, 180),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'WHITE': (255, 255, 255),
}

# 🎶 ไฟล์เพลงประกอบ
MUSIC_FILE = 'Sis Puella Magica!.mp3'

# 🖼️ Global Variables สำหรับภาพพื้นหลัง
MENU_BG_IMAGE = None
GAME_BG_IMAGE = None

# ====================================================================
# 2. CLASS ShapeBlock
# ====================================================================

class ShapeBlock:
    """แทนวัตถุ 1 ชิ้น (1x1) บนกระดาน"""
    
    def __init__(self, x, y, shape_type, color):
        self.x = x
        self.y = y
        self.shape_type = shape_type
        self.color = color
        self.is_special = (shape_type == 'Diamond')
        
    def get_match_key(self):
        return (self.shape_type, self.color)
    
    def __repr__(self):
        return f"({self.shape_type[:3]}/{self.color[:3]} @ {self.x},{self.y})"

# ====================================================================
# 3. CLASS Grid
# ====================================================================

class Grid:
    """จัดการกระดานเกมและกลไกหลัก"""
    
    def __init__(self):
        self.grid_matrix = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)] 
        self.active_shape_blocks = []
        
    def is_valid_position(self, x, y):
        # ใช้สำหรับการตรวจสอบการ Spawn และการ Lock
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        return self.grid_matrix[x][y] is None

    def spawn_new_shape(self):
        num_blocks = random.randint(1, 3)
        start_x = GRID_WIDTH // 2
        
        weights = [10] * (len(SHAPES) - 1) + [3] 
        selected_type = random.choices(SHAPES, weights=weights, k=1)[0]
        selected_color = COLORS[selected_type]

        new_blocks = []
        for i in range(num_blocks):
            block = ShapeBlock(start_x, 0 + i, selected_type, selected_color) 
            new_blocks.append(block)
        
        self.active_shape_blocks = new_blocks
        
        if not all(self.is_valid_position(b.x, b.y) for b in self.active_shape_blocks):
            return "GAME_OVER"

    def move_active_shape(self, dx, dy):
        can_move = True
        for block in self.active_shape_blocks:
            new_x = block.x + dx
            new_y = block.y + dy
            
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                can_move = False
                break
            
            # ตรวจสอบการชนกับบล็อกที่วางอยู่แล้ว โดยต้องไม่ใช่บล็อกใน Active Shape ตัวเอง
            target_block = self.grid_matrix[new_x][new_y]
            if target_block is not None and target_block not in self.active_shape_blocks:
                can_move = False
                break
                
        if can_move:
            for block in self.active_shape_blocks:
                block.x += dx
                block.y += dy
            return True
        
        return False

    def rotate_active_shape(self):
        # ⚠️ แก้ไขเมธอดนี้เพื่อให้การหมุนทำงานได้ถูกต้อง
        if not self.active_shape_blocks or len(self.active_shape_blocks) == 1:
            return
        
        pivot_block = self.active_shape_blocks[0]
        new_positions = []
        
        for block in self.active_shape_blocks:
            rel_x = block.x - pivot_block.x
            rel_y = block.y - pivot_block.y
            
            # Rotate 90 degrees counter-clockwise: (rel_x, rel_y) -> (-rel_y, rel_x)
            new_rel_x = -rel_y
            new_rel_y = rel_x
            
            new_x = pivot_block.x + new_rel_x
            new_y = pivot_block.y + new_rel_y
            
            # 1. ตรวจสอบขอบเขต (รวมถึงแถวบนที่มองไม่เห็น)
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                return 
            
            # 2. ตรวจสอบการชนกับบล็อกที่วางอยู่แล้ว (ไม่ชนกับตัวเอง)
            target_block = self.grid_matrix[new_x][new_y]
            if target_block is not None and target_block not in self.active_shape_blocks:
                return 
                
            new_positions.append((new_x, new_y))

        # อัปเดตตำแหน่งจริง
        for i, block in enumerate(self.active_shape_blocks):
            block.x, block.y = new_positions[i]

    def drop_active_shape(self):
        return self.move_active_shape(0, 1)

    def lock_shape(self):
        """วาง Active Shape และตรวจสอบ Game Over"""
        for block in self.active_shape_blocks:
            self.grid_matrix[block.x][block.y] = block
            
            if block.y < 2:
                self.active_shape_blocks = []
                return "GAME_OVER" 
                
        self.active_shape_blocks = []
        
        total_cleared_score = self.check_and_clear_matches()
        return total_cleared_score

    def check_and_clear_matches(self):
        score = 0
        combo_count = 0
        
        while True:
            cleared_blocks = self._find_all_matches()
            if not cleared_blocks:
                break

            points = self._clear_blocks(cleared_blocks)
            score += self._calculate_combo_score(points, combo_count)
            
            self.apply_gravity()
            combo_count += 1
            
        return score

    def _find_all_matches(self):
        cleared_blocks = set()
        
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                block = self.grid_matrix[x][y]
                if block and block not in cleared_blocks:
                    match_group = self._dfs_match_check(block)
                    if len(match_group) >= 4:
                        for matched_block in match_group:
                            if matched_block.is_special:
                                self._add_horizontal_row_to_clear(matched_block.y, cleared_blocks)
                        
                        cleared_blocks.update(match_group)
                        
        return cleared_blocks

    def _dfs_match_check(self, start_block):
        stack = [start_block]
        visited = {start_block}
        group = []
        match_key = start_block.get_match_key()
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

        while stack:
            current = stack.pop()
            group.append(current)

            for dx, dy in directions:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    neighbor = self.grid_matrix[nx][ny]
                    if neighbor and neighbor.get_match_key() == match_key and neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
        
        return group
    
    def _add_horizontal_row_to_clear(self, y_row, cleared_set):
        for x in range(GRID_WIDTH):
            block = self.grid_matrix[x][y_row]
            if block:
                cleared_set.add(block)

    def _clear_blocks(self, blocks_to_clear):
        cleared_count = len(blocks_to_clear)
        for block in blocks_to_clear:
            self.grid_matrix[block.x][block.y] = None
        return cleared_count

    def _calculate_combo_score(self, cleared_count, combo_count):
        if cleared_count >= 8: base_score = 500
        elif cleared_count >= 6: base_score = 250
        else: base_score = 100
        
        if combo_count == 1: multiplier = 1.5 
        elif combo_count >= 2: multiplier = 2.0
        else: multiplier = 1.0

        return int(base_score * multiplier)

    def apply_gravity(self):
        for x in range(GRID_WIDTH):
            blocks_in_col = [self.grid_matrix[x][y] for y in range(GRID_HEIGHT) if self.grid_matrix[x][y] is not None]
            
            for y in range(GRID_HEIGHT):
                self.grid_matrix[x][y] = None
                
            for i, block in enumerate(blocks_in_col):
                new_y = GRID_HEIGHT - len(blocks_in_col) + i
                block.y = new_y
                self.grid_matrix[x][new_y] = block

# ====================================================================
# 4. CLASS GameManager
# ====================================================================

class GameManager:
    """ควบคุม Game State, Score, Time, และ Input"""
    
    def __init__(self):
        self.grid = Grid()
        self.score = 0
        self.time_left = 180.0
        self.target_score = 2000
        # สถานะที่เป็นไปได้: "MENU", "RUNNING", "PAUSED", "LOSE", "WIN"
        self.game_state = "MENU" 
        self.fall_timer = 0
        self.fall_speed = 0.5

    def reset_game(self):
        """รีเซ็ตทุกอย่างเพื่อเริ่มเกมใหม่"""
        self.grid = Grid()
        self.score = 0
        self.time_left = 180.0
        self.game_state = "RUNNING"
        self.fall_timer = 0
        self.fall_speed = 0.5
        self.grid.spawn_new_shape() 

        # Music Logic
        if pygame.mixer.music.get_volume() > 0:
            if not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    pass

    def handle_input(self, action):
        if self.game_state != "RUNNING":
            return
            
        if action == 'LEFT':
            self.grid.move_active_shape(-1, 0)
        elif action == 'RIGHT':
            self.grid.move_active_shape(1, 0)
        elif action == 'DOWN':
            self.grid.move_active_shape(0, 1)
        elif action == 'ROTATE':
            # ปุ่มลูกศรขึ้น (UP) สำหรับการหมุน
            self.grid.rotate_active_shape()

    def update(self, delta_time):
        # ไม่ต้องอัปเดตเกมถ้าอยู่ในสถานะอื่นที่ไม่ใช่ RUNNING
        if self.game_state != "RUNNING":
            return
            
        self.time_left -= delta_time
        
        self.fall_timer += delta_time
        if self.fall_timer >= self.fall_speed:
            if not self.grid.drop_active_shape():
                
                lock_result = self.grid.lock_shape()
                
                if lock_result == "GAME_OVER":
                    self.game_state = "LOSE" 
                    pygame.mixer.music.stop() 
                    self.fall_timer = 0
                    return 
                    
                self.score += lock_result
                
                if self.grid.spawn_new_shape() == "GAME_OVER":
                    self.game_state = "LOSE"
                    pygame.mixer.music.stop()
                    
            self.fall_timer = 0
        
        self.check_win_or_lose()

    def check_win_or_lose(self):
        if self.score >= self.target_score:
            self.game_state = "WIN"
            pygame.mixer.music.stop()
        elif self.time_left <= 0:
            self.game_state = "LOSE"
            pygame.mixer.music.stop()

# ====================================================================
# 5. RENDERING & UI FUNCTIONS
# ====================================================================

def draw_button(screen, rect, text, font, color, text_color):
    """ฟังก์ชันวาดปุ่มมาตรฐาน"""
    pygame.draw.rect(screen, color, rect, 0, 5)
    pygame.draw.rect(screen, WHITE, rect, 2, 5)
    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))
    return rect

def draw_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, current_volume, is_muted):
    """วาดหน้าจอเมนูหลัก พร้อมปุ่มควบคุมเสียงและชื่อเพลง"""
    
    # กำหนดสีขอบ
    OUTLINE_COLOR = BLACK 
    OUTLINE_THICKNESS = 2 # ความหนาของขอบ (พิกเซล)

    # --- วาด Title และ Subtitle พร้อมขอบ ---
    
    # 1. Title (GEOMADOKA)
    title_text = "GEOMADOKA"
    title_color = WHITE

    # วาดขอบ
    for dx in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
        for dy in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
            if dx != 0 or dy != 0: # หลีกเลี่ยงการวาดทับตัวเองตรงกลาง
                outline_surf = font.render(title_text, True, OUTLINE_COLOR)
                screen.blit(outline_surf, (SCREEN_WIDTH // 2 - outline_surf.get_width() // 2 + dx, SCREEN_HEIGHT // 4 + dy))
    # วาดข้อความหลัก
    title_surf = font.render(title_text, True, title_color)
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, SCREEN_HEIGHT // 4))


    # 2. Subtitle (Falling Geo-Block Puzzle)
    subtitle_text = "Falling Geo-Block Puzzle"
    
    # ⭐️ เปลี่ยนสีตรงนี้: ใช้ PURPLE (RGB: 128, 0, 128)
    # เราต้องสร้างตัวแปรสีม่วงขึ้นมาใหม่
    PURPLE = (128, 0, 128) 
    subtitle_color = PURPLE

    # วาดขอบ
    for dx in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
        for dy in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(subtitle_text, True, OUTLINE_COLOR)
                screen.blit(outline_surf, (SCREEN_WIDTH // 2 - outline_surf.get_width() // 2 + dx, SCREEN_HEIGHT // 4 + 50 + dy))
    # วาดข้อความหลัก
    subtitle_surf = font.render(subtitle_text, True, subtitle_color)
    screen.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, SCREEN_HEIGHT // 4 + 50))

    # ตำแหน่งปุ่ม START
    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2, 250, 60)
    draw_button(screen, start_button_rect, "START GAME", font, DARK_GREEN, WHITE)
    
    # --- 🔊 ปุ่มควบคุมเสียง ---
    button_size = 40
    spacing = 10
    start_x = 30
    start_y = 30
    
    # 1. ปุ่ม Mute/Unmute
    mute_rect = pygame.Rect(start_x, start_y, button_size, button_size)
    mute_text = "M" if not is_muted else "🔇" 
    mute_color = DARK_RED if is_muted else GRAY
    draw_button(screen, mute_rect, mute_text, font, mute_color, WHITE)

    # 2. ปุ่ม ลดเสียง (-)
    vol_down_rect = pygame.Rect(start_x + button_size + spacing, start_y, button_size, button_size)
    draw_button(screen, vol_down_rect, "-", font, GRAY, WHITE)
    
    # 3. ปุ่ม เพิ่มเสียง (+)
    vol_up_rect = pygame.Rect(start_x + 2*button_size + 2*spacing, start_y, button_size, button_size)
    draw_button(screen, vol_up_rect, "+", font, GRAY, WHITE)
    
    # 4. แสดงระดับเสียง (พร้อมขอบ)
    vol_text = f"Vol: {int(current_volume * 100)}%"
    vol_color = WHITE # กำหนดสีข้อความหลัก

    # วาดขอบ
    for dx in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
        for dy in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(vol_text, True, OUTLINE_COLOR)
                screen.blit(outline_surf, (start_x + dx, start_y + button_size + 10 + dy))
    # วาดข้อความหลัก
    vol_surf = font.render(vol_text, True, vol_color)
    screen.blit(vol_surf, (start_x, start_y + button_size + 10))
    
    # 5. แสดงชื่อเพลง (พร้อมขอบ)
    song_name_text = "Song name: Sis Puella Magica!"
    song_color = YELLOW # กำหนดสีข้อความหลัก
    small_font = pygame.font.Font(None, 24) 
    
    song_y = start_y + button_size + 10 + vol_surf.get_height() + 5

    # วาดขอบ
    for dx in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
        for dy in range(-OUTLINE_THICKNESS, OUTLINE_THICKNESS + 1):
            if dx != 0 or dy != 0:
                outline_surf = small_font.render(song_name_text, True, OUTLINE_COLOR)
                screen.blit(outline_surf, (start_x + dx, song_y + dy))
    # วาดข้อความหลัก
    song_surf = small_font.render(song_name_text, True, song_color)
    screen.blit(song_surf, (start_x, song_y))
    
    # ตำแหน่ง: ใต้ Vol text
    song_y = start_y + button_size + 10 + vol_surf.get_height() + 5
    screen.blit(song_surf, (start_x, song_y))
    
    return start_button_rect, mute_rect, vol_down_rect, vol_up_rect

def draw_pause_popup(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT):
    """วาด Pop-up เมื่อเกมหยุดชั่วคราว (PAUSED)"""
    
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))

    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 170, 400, 340)
    pygame.draw.rect(screen, GRAY, box_rect, 0, 10)
    pygame.draw.rect(screen, WHITE, box_rect, 3, 10)

    title_surf = font.render("GAME PAUSED", True, YELLOW)
    screen.blit(title_surf, (box_rect.centerx - title_surf.get_width() // 2, box_rect.top + 30))

    # กำหนดขนาดและตำแหน่งปุ่ม
    button_width = 250
    button_height = 50
    button_x = box_rect.centerx - button_width // 2
    
    # 1. Continue Button (เล่นต่อ)
    continue_rect = pygame.Rect(button_x, box_rect.top + 100, button_width, button_height)
    draw_button(screen, continue_rect, "CONTINUE (Q)", font, DARK_GREEN, WHITE)
    
    # 2. Restart Button (เริ่มใหม่)
    restart_rect = pygame.Rect(button_x, box_rect.top + 170, button_width, button_height)
    draw_button(screen, restart_rect, "RESTART", font, DARK_RED, WHITE)
    
    # 3. Main Menu Button (กลับหน้าเมนู)
    menu_rect = pygame.Rect(button_x, box_rect.top + 240, button_width, button_height)
    draw_button(screen, menu_rect, "MAIN MENU", font, DARK_RED, WHITE)

    return continue_rect, restart_rect, menu_rect

def draw_game_over_popup(screen, game_manager, font, SCREEN_WIDTH, SCREEN_HEIGHT):
    """วาด Pop-up เมื่อเกมจบ (LOSE/WIN)"""
    
    final_score = game_manager.score
    
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))

    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
    pygame.draw.rect(screen, GRAY, box_rect, 0, 10)
    pygame.draw.rect(screen, WHITE, box_rect, 3, 10)

    if game_manager.game_state == "WIN":
        title = "CONGRATULATIONS!"
        color = YELLOW
    else:
        title = "GAME OVER"
        color = RED
        
    title_surf = font.render(title, True, color)
    score_surf = font.render(f"Final Score: {final_score}", True, WHITE)
    
    screen.blit(title_surf, (box_rect.centerx - title_surf.get_width() // 2, box_rect.top + 30))
    screen.blit(score_surf, (box_rect.centerx - score_surf.get_width() // 2, box_rect.top + 80))

    play_again_rect = pygame.Rect(box_rect.left + 30, box_rect.bottom - 80, 160, 50)
    menu_rect = pygame.Rect(box_rect.right - 190, box_rect.bottom - 80, 160, 50)
    
    draw_button(screen, play_again_rect, "PLAY AGAIN", font, DARK_GREEN, WHITE)
    draw_button(screen, menu_rect, "MAIN MENU", font, DARK_RED, WHITE)

    return play_again_rect, menu_rect

def draw_block(screen, block, offset_x=0, offset_y=0):
    # ประกาศ global เพื่อช่วยให้ Linter ทำงานได้ถูกต้องกับ Global Constants
    global BLOCK_SIZE, BLACK, WHITE
    
    color = COLOR_MAP.get(block.color, BLACK)
    rect = pygame.Rect(
        offset_x + block.x * BLOCK_SIZE,
        offset_y + (block.y - 2) * BLOCK_SIZE,
        BLOCK_SIZE,
        BLOCK_SIZE
    )
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 1) 
    center_x = rect.centerx
    center_y = rect.centery
    
    if block.shape_type == 'Triangle':
        points = [(center_x, rect.top + 5), (rect.right - 5, rect.bottom - 5), (rect.left + 5, rect.bottom - 5)]
        pygame.draw.polygon(screen, WHITE, points, 0)
        pygame.draw.polygon(screen, BLACK, points, 2)
    elif block.shape_type == 'Circle':
        pygame.draw.circle(screen, BLACK, (center_x, center_y), BLOCK_SIZE // 2 - 2, 0)
        pygame.draw.circle(screen, WHITE, (center_x, center_y), BLOCK_SIZE // 2 - 2, 2)
    elif block.shape_type == 'Square':
        pygame.draw.rect(screen, BLACK, rect.inflate(-8, -8), 0)
        pygame.draw.rect(screen, WHITE, rect.inflate(-8, -8), 2)
    elif block.shape_type == 'Diamond':
        points = [rect.midtop, rect.midright, rect.midbottom, rect.midleft]
        pygame.draw.polygon(screen, WHITE, points, 0)
        pygame.draw.polygon(screen, BLACK, points, 2)
    elif block.shape_type == 'Pentagon':
        pygame.draw.circle(screen, BLACK, (center_x, center_y), BLOCK_SIZE // 2 - 2, 0)
        pygame.draw.circle(screen, WHITE, (center_x, center_y), BLOCK_SIZE // 2 - 2, 2)
        pygame.draw.line(screen, WHITE, (center_x, rect.top + 5), (center_x, rect.bottom - 5), 2)
    elif block.shape_type == 'Star':
        pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomright, 2)
        pygame.draw.line(screen, WHITE, rect.topright, rect.bottomleft, 2)

def draw_grid(screen, grid_instance, offset_x, offset_y):
    global GRID_WIDTH, BLOCK_SIZE, GRID_HEIGHT, WHITE
    
    grid_rect = pygame.Rect(offset_x, offset_y, GRID_WIDTH * BLOCK_SIZE, (GRID_HEIGHT-2) * BLOCK_SIZE)
    # พื้นหลังตารางโปร่งแสงสีดำ
    s = pygame.Surface((grid_rect.width, grid_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 50)) 
    screen.blit(s, (grid_rect.x, grid_rect.y))

    pygame.draw.rect(screen, WHITE, grid_rect, 2) # วาดแค่ขอบ

    for x in range(GRID_WIDTH):
        for y in range(2, GRID_HEIGHT): 
            block = grid_instance.grid_matrix[x][y]
            if block:
                draw_block(screen, block, offset_x, offset_y)
    for block in grid_instance.active_shape_blocks:
        if block.y >= 2:
            draw_block(screen, block, offset_x, offset_y)
            
def draw_running_ui(screen, game_manager, font, ui_x, grid_offset_y):
    """วาด UI สำหรับสถานะ RUNNING (Time, Score, Goal และคำแนะนำ)"""
    status_text = f"Time: {max(0, game_manager.time_left):.1f}s"
    score_text = f"Score: {game_manager.score}"
    goal_text = f"Goal: {game_manager.target_score}"
    
    # พื้นหลังโปร่งแสงสีดำสำหรับข้อความ
    ui_width = 250
    ui_rect = pygame.Rect(ui_x - 10, grid_offset_y - 10, ui_width, 200)
    s = pygame.Surface((ui_rect.width, ui_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 100)) 
    screen.blit(s, (ui_rect.x, ui_rect.y))

    time_surf = font.render(status_text, True, WHITE)
    screen.blit(time_surf, (ui_x, grid_offset_y))

    score_surf = font.render(score_text, True, WHITE)
    screen.blit(score_surf, (ui_x, grid_offset_y + 60))
    
    goal_surf = font.render(goal_text, True, WHITE)
    screen.blit(goal_surf, (ui_x, grid_offset_y + 120))

    # แสดงคำแนะนำการหยุดเกม
    stop_text = "Press Q for stop"
    small_font = pygame.font.Font(None, 28)
    stop_surf = small_font.render(stop_text, True, YELLOW)
    
    # ตำแหน่ง: ใต้ Goal text
    stop_y = grid_offset_y + 120 + goal_surf.get_height() + 30
    screen.blit(stop_surf, (ui_x, stop_y))


# ====================================================================
# 6. MAIN GAME LOOP
# ====================================================================

def run_geomatch():
    
    try:
        pygame.init()
        pygame.mixer.init()
    except Exception as e:
        print(f"FATAL ERROR: Failed to initialize Pygame. Error: {e}")
        return

    font = pygame.font.Font(None, 36)
    grid_offset_x = 50
    grid_offset_y = 50

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"FATAL ERROR: Could not set display mode. Error: {e}")
        pygame.quit()
        return

    pygame.display.set_caption("GeoMatch - Falling Block Game")
    clock = pygame.time.Clock()
    
    # 🖼️ โหลดและปรับภาพพื้นหลัง
    global MENU_BG_IMAGE, GAME_BG_IMAGE
    try:
        MENU_BG_IMAGE = pygame.image.load('menu_bg.jpg').convert()
        MENU_BG_IMAGE = pygame.transform.scale(MENU_BG_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"WARNING: Could not load 'menu_bg.jpg'. Using BLACK background. Error: {e}")
        MENU_BG_IMAGE = None
    
    try:
        GAME_BG_IMAGE = pygame.image.load('game_bg.jpg').convert()
        GAME_BG_IMAGE = pygame.transform.scale(GAME_BG_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"WARNING: Could not load 'game_bg.jpg'. Using BLACK background. Error: {e}")
        GAME_BG_IMAGE = None

    current_volume = 0.5 
    is_muted = False
    
    # Initial Music Setup
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(current_volume)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"WARNING: Could not load music file '{MUSIC_FILE}'. Music will be disabled. Error: {e}")
        
    try:
        game_manager = GameManager() 
    except Exception as e:
        print(f"FATAL ERROR: Failed to create GameManager instance. Error: {e}")
        pygame.quit()
        return

    menu_buttons = (None, None, None, None) 
    popup_buttons = (None, None)
    pause_buttons = (None, None, None) 

    running = True
    while running:
        try:
            delta_time = clock.get_time() / 1000.0 
            
            # --- Event Handling (Input) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 1. Input สำหรับสถานะ RUNNING & PAUSED (ปุ่ม Q) และการควบคุมทิศทาง
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        if game_manager.game_state == "RUNNING":
                            game_manager.game_state = "PAUSED"
                            pygame.mixer.music.pause()
                            
                        elif game_manager.game_state == "PAUSED":
                            game_manager.game_state = "RUNNING"
                            pygame.mixer.music.unpause()
                            
                    # Input ควบคุมทิศทาง (เฉพาะ RUNNING)
                    elif game_manager.game_state == "RUNNING":
                        if event.key == pygame.K_LEFT:
                            game_manager.handle_input('LEFT')
                        elif event.key == pygame.K_RIGHT:
                            game_manager.handle_input('RIGHT')
                        elif event.key == pygame.K_DOWN:
                            game_manager.handle_input('DOWN')
                        elif event.key == pygame.K_UP: 
                            game_manager.handle_input('ROTATE')

                            
                # 2. Input สำหรับสถานะ MENU (คลิกปุ่มต่างๆ)
                elif game_manager.game_state == "MENU" and event.type == pygame.MOUSEBUTTONDOWN:
                    start_button, mute_rect, vol_down_rect, vol_up_rect = menu_buttons
                    
                    if start_button and start_button.collidepoint(event.pos):
                        game_manager.reset_game()
                    
                    elif mute_rect and mute_rect.collidepoint(event.pos):
                        is_muted = not is_muted
                        if is_muted:
                            pygame.mixer.music.set_volume(0.0)
                        else:
                            pygame.mixer.music.set_volume(current_volume)
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.play(-1)
                                
                    elif vol_down_rect and vol_down_rect.collidepoint(event.pos):
                        current_volume = max(0.0, current_volume - 0.1) 
                        if not is_muted:
                            pygame.mixer.music.set_volume(current_volume)

                    elif vol_up_rect and vol_up_rect.collidepoint(event.pos):
                        current_volume = min(1.0, current_volume + 0.1) 
                        if not is_muted:
                            pygame.mixer.music.set_volume(current_volume)
                        
                # 3. Input สำหรับสถานะ LOSE/WIN
                elif (game_manager.game_state == "LOSE" or game_manager.game_state == "WIN") and event.type == pygame.MOUSEBUTTONDOWN and popup_buttons[0]:
                    play_again_rect, menu_rect = popup_buttons
                    if play_again_rect.collidepoint(event.pos):
                        game_manager.reset_game()
                    elif menu_rect.collidepoint(event.pos):
                        game_manager.game_state = "MENU"
                        game_manager.grid = Grid() 

                # 4. Input สำหรับสถานะ PAUSED (คลิกปุ่ม Pop-up)
                elif game_manager.game_state == "PAUSED" and event.type == pygame.MOUSEBUTTONDOWN and pause_buttons[0]:
                    continue_rect, restart_rect, menu_rect = pause_buttons
                    
                    if continue_rect.collidepoint(event.pos):
                        game_manager.game_state = "RUNNING"
                        pygame.mixer.music.unpause()

                    elif restart_rect.collidepoint(event.pos):
                        game_manager.reset_game()
                        pygame.mixer.music.unpause()

                    elif menu_rect.collidepoint(event.pos):
                        game_manager.game_state = "MENU"
                        game_manager.grid = Grid()
                        pygame.mixer.music.unpause()

            # --- Update & Drawing based on State ---
            
            # 🖼️ วาดภาพพื้นหลังตามสถานะก่อนเสมอ
            if game_manager.game_state == "MENU":
                if MENU_BG_IMAGE:
                    screen.blit(MENU_BG_IMAGE, (0, 0))
                else:
                    screen.fill(BLACK)
            elif game_manager.game_state == "RUNNING" or game_manager.game_state == "PAUSED" or game_manager.game_state == "LOSE" or game_manager.game_state == "WIN":
                if GAME_BG_IMAGE:
                    screen.blit(GAME_BG_IMAGE, (0, 0))
                else:
                    screen.fill(BLACK)
            else:
                screen.fill(BLACK)
                
            ui_x = grid_offset_x + GRID_WIDTH * BLOCK_SIZE + 50 

            if game_manager.game_state == "RUNNING" or game_manager.game_state == "PAUSED":
                game_manager.update(delta_time)
                draw_grid(screen, game_manager.grid, grid_offset_x, grid_offset_y)
                draw_running_ui(screen, game_manager, font, ui_x, grid_offset_y)
                
                # Draw Pause Pop-up
                if game_manager.game_state == "PAUSED":
                    pause_buttons = draw_pause_popup(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)
                else:
                    pause_buttons = (None, None, None)

            elif game_manager.game_state == "MENU":
                menu_buttons = draw_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, current_volume, is_muted)
                
            elif game_manager.game_state == "LOSE" or game_manager.game_state == "WIN":
                draw_grid(screen, game_manager.grid, grid_offset_x, grid_offset_y)
                draw_running_ui(screen, game_manager, font, ui_x, grid_offset_y)
                
                popup_buttons = draw_game_over_popup(screen, game_manager, font, SCREEN_WIDTH, SCREEN_HEIGHT)


            pygame.display.flip()
            clock.tick(60) 
            
        except Exception as e:
            print(f"RUNTIME ERROR: An unexpected error occurred in the Game Loop. Error: {e}")
            running = False

    pygame.quit()

# ====================================================================
# RUN EXECUTION
# ====================================================================

if __name__ == '__main__':
    run_geomatch()