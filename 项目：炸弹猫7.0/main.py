import pygame
from pygame.locals import *
import sys
import random

from monster import *
from prop import *
from you import li_cards
import my_game

print("start")
# 初始化配置 --------------------------------------------------

def init_settings():    # 乱七八糟的一堆还是一起封装起来(都是必须的初始化)
    pygame.init()
    pygame.mixer.init()  # 初始化音频混合器
    WIDTH, HEIGHT = 1792 // 2, 1024 // 2
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("炸弹猫")
    return screen, WIDTH, HEIGHT
# 立即调用初始化函数
screen, WIDTH, HEIGHT = init_settings()
# 全局配置 --------------------------------------------------
COLORS = {
    # 主界面颜色
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'gold': (255, 215, 0),
    'panel': (30, 30, 30, 200),
    'button': (70, 70, 70),   # 按钮的
    'dark_gray': (60, 60, 60),
    'card_bg': (200, 180, 100),   # 卡牌背景色

    # 战斗界面颜色
    "bg": (30, 30, 30),  # 背景色
    "text": (240, 240, 240),  # 默认文本颜色
    "warning": (255, 80, 80),  # 警告色
}

FONTS = {
    'title': pygame.font.Font("font_style2.ttf", 72),
    'button': pygame.font.Font("font_style1.ttf", 36),   # 比起2字体要更破碎些
    'big': pygame.font.Font("font_style2.ttf", 42),
    'normal': pygame.font.Font("font_style2.ttf", 28),
    'medium': pygame.font.Font("SimHei.ttf", 32),
    'small': pygame.font.Font("SimHei.ttf", 20)
}

IMAGES = {
    'starting_ui': pygame.image.load('starting_ui_background.jpg'),
    'avatar': pygame.image.load('avatar.jpg'),
    'coin': pygame.image.load('coin.jpg'),
    'battle_background': pygame.image.load('battle_bg.jpg')
}


# 主菜单模块 --------------------------------------------------
class MainMenu:   # 主菜单
    def __init__(self, screen, WIDTH, HEIGHT):    # 初始化
        self.screen = screen
        self.elements = {      # 主菜单的含文字元素
            'title': self.create_text("炸弹猫", 'title', (WIDTH // 2, HEIGHT // 4)),
            'start_btn': self.create_text("开始游戏", 'button', (WIDTH // 2, HEIGHT // 2)),
            'quit_btn': self.create_text("退出游戏", 'button', (WIDTH // 2, HEIGHT // 2 + HEIGHT//6)),
            'credit': self.create_text("开发者：---", 'small', (WIDTH - 100, HEIGHT - 20))
        }
        self.button_hitboxes = {    # 其中的可点击部分
            'start': self.elements['start_btn'][1].inflate(40, 20),
            'quit': self.elements['quit_btn'][1].inflate(40, 20),
            'music': pygame.Rect(20, HEIGHT - 40, 80, 30)  # 音乐按钮点击区域
        }
        self.music_on = True  # 音乐默认开启

    def create_text(self, text, font_type, center_pos):   # 创建文本(循环外创建)
        text_surf = FONTS[font_type].render(text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center = center_pos)
        return text_surf, text_rect

    def draw_element(self, element, bg_color = None, mouse_pos = None):   # 保持渲染(循环内保持)
        text_surf, text_rect = element
        if bg_color:
            btn_rect = text_rect.inflate(40, 20)
            hover = btn_rect.collidepoint(mouse_pos) if mouse_pos else False
            rect_color = COLORS['black'] if hover else bg_color
            pygame.draw.rect(self.screen, rect_color, btn_rect)
        self.screen.blit(text_surf, text_rect)

    def run(self):    # 主菜单运行
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(IMAGES['starting_ui'], (0, 0))

            # 更新音乐按钮文本
            self.elements['music_btn'] = self.create_text(
                f"音乐: {'开' if self.music_on else '关'}",
                'small',
                (50, HEIGHT - 20)
            )
            # 绘制元素
            self.draw_element(self.elements['title'])
            self.draw_element(self.elements['start_btn'], COLORS['gray'], mouse_pos)
            self.draw_element(self.elements['quit_btn'], COLORS['gray'], mouse_pos)
            self.draw_element(self.elements['credit'])
            self.draw_element(self.elements['music_btn'])  # 绘制音乐按钮
            # 事件处理
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if self.button_hitboxes['start'].collidepoint(event.pos):
                        return True  # 进入游戏主界面
                    elif self.button_hitboxes['quit'].collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif self.button_hitboxes['music'].collidepoint(event.pos):  # 音乐按钮点击
                        self.music_on = not self.music_on
                        game_interface.toggle_music()  # 切换音乐状态

            pygame.display.flip()

# 过渡模块  ----------------------------------------------------
#故事情节函数
def plot():

    # 创建一个半透明背景面板
    story_panel = pygame.Surface((WIDTH-100, HEIGHT-100), pygame.SRCALPHA)
    story_panel.fill((0, 0, 0, 200))
    
    # 故事情节
    story_lines = [
        "在一个被诅咒的猫王国里，",
        "邪恶的猫巫师释放了可怕的炸弹猫瘟疫，",
        "所有怒气值超过100的猫都会变成行走的炸弹。",
        "",
        "作为王国的最后希望，",
        "你必须用用现有卡牌来对抗这场灾难，",
        "准备好开始你的冒险了吗？"
    ]
    
    # 显示文本
    y_offset = 30
    for line in story_lines:
        if line:  # 非空行
            text = FONTS['normal'].render(line, True, COLORS['white'])
            story_panel.blit(text, (50, y_offset))
        y_offset += 40
    
    # 确定按钮
    continue_btn = pygame.Rect(
        story_panel.get_width()//2 - 100,
        story_panel.get_height() - 80,
        200, 50
    )
    pygame.draw.rect(story_panel, COLORS['gold'], continue_btn, border_radius=10)
    btn_text = FONTS['normal'].render("继续", True, COLORS['black'])
    story_panel.blit(btn_text, (continue_btn.centerx - btn_text.get_width()//2, 
                               continue_btn.centery - btn_text.get_height()//2))
    
    # 显示故事面板
    screen.blit(story_panel, (50, 50))
    pygame.display.flip()
    
    # 等待玩家点击继续
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                adjusted_pos = (mouse_pos[0]-50, mouse_pos[1]-50)  # 调整到面板坐标系
                if continue_btn.collidepoint(adjusted_pos):
                    waiting = False

# 输入昵称 缺点是只能输数字＋英文呢称，输入长度限制12
def input_nickname():
    nickname = ""
    input_active = True
    
    # 创建输入框
    input_box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 50)
    color_inactive = COLORS['gray']
    color_active = COLORS['gold']
    color = color_inactive
    
    # 提示文本
    prompt_text = FONTS['normal'].render("请输入你的昵称(限制为英文输入法）:", True, COLORS['white'])
    prompt_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    
    # 确认按钮
    confirm_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 70, 160, 50)
    
    while input_active:    #主输入循环
        for event in pygame.event.get():
            if event.type == QUIT:  #退出事件
                pygame.quit()
                sys.exit()
                
            if event.type == MOUSEBUTTONDOWN:     #鼠标点击事件
                # 检查是否点击输入框
                if input_box.collidepoint(event.pos):
                    color = color_active
                else:
                    color = color_inactive
                
                # 检查确认按钮
                if confirm_btn.collidepoint(event.pos) and nickname:    
                    input_active = False

            if event.type == KEYDOWN:
                if color == color_active:
                    if event.key == K_RETURN and nickname:
                        input_active = False
                    elif event.key == K_BACKSPACE:  # 输错了删除最后一个字符
                        nickname = nickname[:-1]
                    else:
                        # 限制昵称长度，允许大小写字母和数字
                        if len(nickname) < 12 and (event.unicode.isalnum() or event.unicode.isupper()):
                            nickname += event.unicode
        
        # 绘制界面
        screen.fill(COLORS['black'])
        
        # 绘制提示
        screen.blit(prompt_text, prompt_rect)
        
        # 绘制输入框
        pygame.draw.rect(screen, color, input_box, 2, border_radius=5)
        txt_surface = FONTS['normal'].render(nickname, True, COLORS['white'])
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        input_box.w = max(300, txt_surface.get_width() + 20)
        
        # 绘制确认按钮
        btn_color = COLORS['gold'] if nickname else COLORS['gray']
        pygame.draw.rect(screen, btn_color, confirm_btn, border_radius=10)
        btn_text = FONTS['normal'].render("确认", True, COLORS['black'])
        screen.blit(btn_text, (confirm_btn.centerx - btn_text.get_width()//2, 
                              confirm_btn.centery - btn_text.get_height()//2))
        
        pygame.display.flip()
    
    return nickname if nickname else "Player"  # 默认昵称

#显示通关结尾画面
def ending_screen():

    # 创建半透明背景面板
    end_panel = pygame.Surface((WIDTH-100, HEIGHT-100), pygame.SRCALPHA)
    end_panel.fill((0, 0, 0, 200))
    
    # 显示通关标题
    title_font = pygame.font.Font("font_style2.ttf", 48)
    title_text = title_font.render("恭喜通关！", True, COLORS['gold'])
    end_panel.blit(title_text, (end_panel.get_width()//2 - title_text.get_width()//2, 50))
    
    # 显示玩家信息
    info_font = FONTS['normal']
    lines = [
        f"玩家: {player_nickname}",
        "你成功拯救了猫王国！",
        "所有的炸弹猫都被净化了",
        "恭喜您通关成功"
    ]
    
    # 渲染文本
    y_offset = 120
    for line in lines:
        if line:
            text = info_font.render(line, True, COLORS['white'])
            end_panel.blit(text, (end_panel.get_width()//2 - text.get_width()//2, y_offset))
        y_offset += 50
    
    #添加两个水平排列的按钮）
    button_area_y = end_panel.get_height() - 80  # 按钮区域垂直位置

    #左侧是返回菜单按钮
    return_btn_rect = pygame.Rect(
        end_panel.get_width()//2 - 220,  
        button_area_y,
        200, 50
    )
    pygame.draw.rect(end_panel, COLORS['gold'], return_btn_rect, border_radius=10)
    return_text = FONTS['normal'].render("返回菜单", True, COLORS['black'])
    end_panel.blit(return_text, (
        return_btn_rect.centerx - return_text.get_width()//2,
        return_btn_rect.centery - return_text.get_height()//2
    ))

    # 右侧是退出游戏按钮
    exit_btn_rect = pygame.Rect(
        end_panel.get_width()//2 + 20,  
        button_area_y,
        200, 50
    )
    pygame.draw.rect(end_panel, COLORS['gold'], exit_btn_rect, border_radius=10)  
    exit_text = FONTS['normal'].render("退出游戏", True, COLORS['black'])
    end_panel.blit(exit_text, (
        exit_btn_rect.centerx - exit_text.get_width()//2,
        exit_btn_rect.centery - exit_text.get_height()//2
    ))
    
    # 显示面板
    screen.blit(end_panel, (50, 50))
    pygame.display.flip()
    
    # 等待玩家点击
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                adjusted_pos = (mouse_pos[0]-50, mouse_pos[1]-50)  # 转换为面板坐标系

                # 检测返回菜单按钮
                if return_btn_rect.collidepoint(adjusted_pos):
                    waiting = False
                    return True  # 返回主菜单

                # 检测退出游戏按钮
                if exit_btn_rect.collidepoint(adjusted_pos):
                    pygame.quit()
                    sys.exit()  # 直接退出游戏

# 游戏主界面模块 --------------------------------------------------
class GameInterface:   # 游戏主界面
    def __init__(self, screen, WIDTH, HEIGHT):  # 初始化
        self.screen = screen
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        # 添加音乐相关属性
        self.background_music = None
        self.music_playing = False
        self.load_music()  # 加载音乐

        self.coins = 1000    # 这俩参量必须是全局的
        self.handbook_mode = "cards"

        self.scroll_y = 0    # 代码从这开始，所有与"scroll"相关的都是用来处理适应“滚动”交互
        self.scroll_x = 0    # x和y分别是水平和垂直方向上的滚动
        self.max_scroll_y = 0

        self.battle_started = False  # 新增：标记战斗是否开始

        self.single_btn = None   # 初始化
        self.multi_btn = None
        self.single_btn_screen = None
        self.multi_btn_screen = None    
        
        self.gacha_pool = []  # 独立的抽卡池
        self.showing_gacha = False
        self.gacha_results = []  
        self.init_gacha_pool()

        self.current_round = 1  # 当前挑战的关卡
        self.round_btn = None   # 动态更新的关卡按钮

        self.max_rounds = 4  # 总轮次上限
        self.current_round = 1
        self.has_won_game = False  # 是否已通关


    def update_round_button(self):  # 动态更新关卡按钮
        btn_width, btn_height = 200, 60
        # 按钮始终居中
        self.round_btn = (
            f"Round {self.current_round}",
            pygame.Rect(
                self.WIDTH//2 - btn_width//2,
                self.HEIGHT//2 - btn_height//2,
                btn_width,
                btn_height
            )
        )

    def init_gacha_pool(self):      # 从全局卡牌复制初始池
        self.gacha_pool = list(s.name for s in dict_props_palyer.values())

    def draw_top_bar(self):   # 顶部状态栏
        # 初始化
        top_panel = pygame.Surface((WIDTH, 60), SRCALPHA)
        top_panel.fill(COLORS['panel'])
        
        # 头像区域
        avatar_rect = pygame.Rect(10, 5, 50, 50)
        pygame.draw.rect(top_panel, COLORS['white'], avatar_rect, 2)
        IMAGES['avatar'] = pygame.transform.scale(IMAGES['avatar'], (50, 50))
        top_panel.blit(IMAGES['avatar'], (avatar_rect.x, avatar_rect.y))
        
        nickname_text = FONTS['normal'].render(player_nickname, True, COLORS['white'])
        top_panel.blit(nickname_text, (70, 15))
        
        # 金币区域
        IMAGES['coin'] = pygame.transform.scale(IMAGES['coin'], (20, 20))
        top_panel.blit(IMAGES['coin'], (WIDTH - 100, 20))
        coin_text = FONTS['small'].render(f"x{self.coins}", True, COLORS['white'])
        top_panel.blit(coin_text, (WIDTH - 80, 20))
        
        screen.blit(top_panel, (0, 0))

    def draw_bottom_menu(self, current_tab):   # 底部菜单栏
        # 初始化
        bottom_panel = pygame.Surface((WIDTH, 80), SRCALPHA)
        bottom_panel.fill(COLORS['panel'])
        
        # 按钮分布
        tabs = ['战斗', '卡牌', '图鉴']
        button_width = WIDTH // 3 - 12
        for i, tab in enumerate(tabs):
            x = 10 + i * (button_width + 10)
            color = COLORS['white'] if tab == current_tab else COLORS['button']
            
            # 绘制按钮
            btn_rect = pygame.Rect(x, 10, button_width, 60)
            pygame.draw.rect(bottom_panel, color, btn_rect, border_radius=5)
            
            # 文字
            text = FONTS['button'].render(tab, True, COLORS['black'])
            text_rect = text.get_rect(center=btn_rect.center)
            bottom_panel.blit(text, text_rect)
        
        screen.blit(bottom_panel, (0, HEIGHT - 80))

    def draw_button(self, surface, pos, text, active = False, enabled=True):   # “按钮绘制”函数，用来统一处理后续的按钮绘制

        btn_rect = pygame.Rect(pos[0], pos[1], 180, 60)
        mouse_pos = pygame.mouse.get_pos()

        # 转换坐标到surface本地坐标系
        local_x = mouse_pos[0] - surface.get_abs_offset()[0]
        local_y = mouse_pos[1] - surface.get_abs_offset()[1]
        hover = btn_rect.collidepoint(local_x, local_y - 77)   # 减去77是为了合适
        
        color = COLORS['gold'] if (active or hover) else COLORS['button']
        if not enabled: color = COLORS['gray']
        
        pygame.draw.rect(surface, color, btn_rect, border_radius=10)
        text_color = COLORS['black'] if enabled else COLORS['dark_gray']
        text_surf = FONTS['normal'].render(text, True, text_color)
        surface.blit(text_surf, (pos[0] + 20, pos[1] + 15))
        return btn_rect
    
    def draw_battle_interface(self):   # 战斗界面
        text, rect = self.round_btn
        # 根据鼠标悬停状态动态高亮
        mouse_pos = pygame.mouse.get_pos()
        color = COLORS['gold'] if rect.collidepoint(mouse_pos) else COLORS['gray']
        # 绘制按钮
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        text_surf = FONTS['button'].render(text, True, COLORS['black'])
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

        pygame.display.flip()

    def draw_gacha_interface(self):  # 抽卡界面
        # 抽卡面板
        panel = pygame.Surface((self.WIDTH - 40, 300), pygame.SRCALPHA)
        panel.fill(COLORS['panel'])

        single_btn_rect = pygame.Rect(70, 120, 180, 60)  # (x, y, width, height)
        multi_btn_rect = pygame.Rect(270, 120, 180, 60)

        # 绘制按钮（仍然在panel上绘制，但检测用屏幕坐标）
        self.draw_button(panel, (50, 20), f"单抽(100)", enabled=self.coins >= 100)
        self.draw_button(panel, (250, 20), f"十连(950)", enabled=self.coins >= 950)

        # 保存按钮rect用于点击检测（直接使用屏幕坐标）
        self.single_btn_screen = single_btn_rect
        self.multi_btn_screen = multi_btn_rect

        # 卡牌滚动逻辑
        total_width = len(li_cards) * 100 - (self.WIDTH - 200) - 140  # 减去140是试出来的
        self.scroll_x = max(0, min(self.scroll_x, total_width))

        # 绘制卡牌
        card_x = 20 - self.scroll_x
        for card in li_cards:
            if card_x > self.WIDTH - 40: continue
            card_rect = pygame.Rect(card_x, 100, 80, 120)
            pygame.draw.rect(panel, COLORS['card_bg'], card_rect, border_radius=5)

            # 卡牌文字
            if isinstance(card, int):
                text = FONTS['big'].render(str(card), True, COLORS['black'])
            else:
                text = FONTS['normal'].render(card, True, COLORS['black'])
            text_rect = text.get_rect(center=card_rect.center)
            panel.blit(text, text_rect)

            card_x += 100

        self.screen.blit(panel, (20, 100))

        if self.showing_gacha:
            self.draw_gacha_results()

    def draw_handbook_interface(self):   # 图鉴界面
        # 图鉴面板
        panel = pygame.Surface((self.WIDTH - 40, 300), pygame.SRCALPHA)
        panel.fill(COLORS['panel'])
        
        # 模式切换按钮区域（高度80）
        button_area_height = 80    # 这个参数找了好久！
        self.draw_button(panel, (20, 20), "卡牌图鉴", active = self.handbook_mode=="cards")
        self.draw_button(panel, (160, 20), "怪物图鉴", active = self.handbook_mode=="monsters")
        
        # 内容区域参数
        content_start_y = 90  # 从按钮下方开始
        visible_height = self.HEIGHT - 180 - button_area_height - 20  # 可视区域高度
        
        # 获取条目数据
        entries = li_props if self.handbook_mode == "cards" else li_monsters
        
        # 计算总内容高度
        entry_heights = [100 if self.handbook_mode == "monsters" else 80 for _ in entries]   # 单块区域
        content_height = sum(entry_heights) - 10
        
        # 滚动边界控制
        self.max_scroll_y = max(0, content_height - visible_height)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll_y))
        
        # 绘制内容（带裁剪区域）
        clip_rect = pygame.Rect(0, button_area_height, panel.get_width(), visible_height)
        panel.set_clip(clip_rect)
        
        current_y = content_start_y - self.scroll_y
        for i, item in enumerate(entries):
            entry_height = entry_heights[i]
            # 只绘制可见条目
            if current_y + entry_height < button_area_height:
                current_y += entry_height
                continue
            if current_y > visible_height + button_area_height:
                break
                
            # 绘制条目背景
            entry_rect = pygame.Rect(20, current_y, self.WIDTH - 80, entry_height-10)
            pygame.draw.rect(panel, COLORS['button'], entry_rect, border_radius=5)
            
            # 绘制条目内容
            if self.handbook_mode == "cards":
                text_line1 = FONTS['small'].render(f"{item.name}", True, COLORS['gold'])
                text_line2 = FONTS['small'].render(f"功能：{item.function}", True, COLORS['white'])
                panel.blit(text_line1, (entry_rect.x + 10, entry_rect.y + 5))
                panel.blit(text_line2, (entry_rect.x + 10, entry_rect.y + 25))
            else:
                text_line1 = FONTS['small'].render(f"{item.number}. {item.name}", True, COLORS['gold'])
                text_line2 = FONTS['small'].render(f"{item.strategy}", True, COLORS['white'])
                cards_text = "初始卡牌：" + ", ".join(str(card) for card in item.cards)  

                text_line3 = FONTS['small'].render(cards_text, True, COLORS['white'])
                panel.blit(text_line1, (entry_rect.x + 10, entry_rect.y + 5))
                panel.blit(text_line2, (entry_rect.x + 10, entry_rect.y + 25))
                panel.blit(text_line3, (entry_rect.x + 10, entry_rect.y + 45))

            current_y += entry_height
        
        # 重置裁剪区域
        panel.set_clip(None)

        self.screen.blit(panel, (20, 80))
    def draw_gacha_results(self):   # 绘制 抽卡结果
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # 半透明黑色背景
        
        card_width, card_height = 150, 200  # 缩小卡牌尺寸
        card_color = (255, 240, 200)
        none_color = (200, 200, 200)
        
        if len(self.gacha_results) == 1:  # 单抽布局
            card = self.gacha_results[0]
            # 居中显示
            card_rect = pygame.Rect(
                WIDTH//2 - card_width//2,
                HEIGHT//2 - card_height//2,
                card_width,
                card_height
            )
            # 卡牌主体
            color = none_color if card is None else card_color
            pygame.draw.rect(overlay, color, card_rect, border_radius=8)
            # 文字样式
            text = FONTS['medium'].render(str(card) if card else "None", True, (40, 40, 40))
            text_rect = text.get_rect(center = card_rect.center)
            overlay.blit(text, text_rect)
        else:  # 2x5布局
            cols = 5
            start_x = (WIDTH - (cols * card_width + (cols-1)*20)) // 2
            start_y = (HEIGHT - (2*card_height + 20)) // 2

            for i, card in enumerate(self.gacha_results):
                row = i // cols
                col = i % cols
                x = start_x + col * (card_width + 20)
                y = start_y + row * (card_height + 30)
                
                # 创建当前卡片的rect对象
                card_rect = pygame.Rect(x, y, card_width, card_height)  # 新增
                
                # 绘制卡牌
                color = none_color if card is None else card_color
                pygame.draw.rect(overlay, color, card_rect, border_radius=8)  # 使用rect对象
                
                # 文字居中（使用当前卡片的rect）
                text = FONTS['medium'].render(str(card) if card else "None", True, (40,40,40))
                text_rect = text.get_rect(center=card_rect.center)  # 使用当前卡片的中心点
                overlay.blit(text, text_rect)

        screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def gacha(self, times): # 抽卡
        results = []
        for _ in range(times):
            if random.random() < 0.85:    # 0.15概率有牌
                card = None
            else:
                if not self.gacha_pool:  # 卡池为空时补充（概率其实很小）
                    self.init_gacha_pool()
                card = random.choice(self.gacha_pool)
                if card: 
                    self.gacha_pool.remove(card)
                    li_cards.append(card)  # 实际卡牌添加
            results.append(card)
        self.gacha_results = results
        self.showing_gacha = True

    def run(self):  # 主循环
        clock = pygame.time.Clock()
        self.update_round_button()  # 初始化按钮
        #running = True
        current_tab = '战斗'

        while True:
            screen.fill(COLORS['black'])
            self.draw_top_bar()
            self.draw_bottom_menu(current_tab)

            # 根据当前标签绘制不同界面
            if current_tab == '图鉴':
                self.draw_handbook_interface()
            elif current_tab == '卡牌':
                self.draw_gacha_interface()
            else:
                self.draw_battle_interface()
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # 鼠标滚轮
                if event.type == MOUSEWHEEL:
                    if current_tab == "图鉴":
                        self.scroll_y -= event.y * 20
                    elif current_tab == "卡牌":
                        self.scroll_x += event.x * 20
                
                # 鼠标点击
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # 底部菜单切换
                    if self.HEIGHT - 80 < y < self.HEIGHT:
                        tab_width = self.WIDTH // 3-12
                        for i in range(3):
                            btn_x = 10 + i * (tab_width + 10)
                            if btn_x < x < btn_x + tab_width:
                                current_tab = ['战斗','卡牌','图鉴'][i]
                    
                    # 图鉴模式切换
                    if current_tab == "图鉴" and 100 < y < 160:
                        if 20 < x < 180:
                            self.handbook_mode = 'cards'
                            self.scroll_y = 0
                        elif 180 < x < 350:
                            self.handbook_mode = 'monsters'
                            self.scroll_y = 0
                    
                    # 抽卡按钮
                    if current_tab == "卡牌":
                        if self.showing_gacha:  
                            self.showing_gacha = False
                            continue
                        # 检查按钮前确保坐标存在
                        if self.single_btn_screen and self.single_btn_screen.collidepoint(x, y):
                            if self.coins >= 100:
                                self.coins -= 100
                                self.gacha(1)
                        elif self.multi_btn_screen and self.multi_btn_screen.collidepoint(x, y):
                            if self.coins >= 950:
                                self.coins -= 950
                                self.gacha(10)

                    # 战斗按钮
                    if current_tab == '战斗':
                        from my_game import game_loop
                        my_game.gs.reset(self.current_round)
                        battle_result = my_game.game_loop(round_num=self.current_round)

                        # 处理战斗结果
                        if battle_result['status'] == 'victory':
                            self.coins += battle_result['coins']
                            # 解锁下一关（不超过最大关卡数）
                            if self.current_round < 4:
                                self.current_round += 1
                                self.update_round_button()
                            else:
                                # 所有关卡完成，显示通关画面
                                self.has_won_game = True
                                ending_screen()

                pygame.display.flip()
                clock.tick(60)
    def load_music(self):
        """加载背景音乐"""
        try:
            # 确保项目目录下有
            self.background_music = pygame.mixer.Sound("music.mp3")
            self.background_music.set_volume(0.5)  # 设置音量
        except Exception as e:
            print(f"无法加载背景音乐: {e}")
            self.background_music = None

    def toggle_music(self):
            """切换音乐播放状态"""
            if self.background_music:
                if self.music_playing:
                    pygame.mixer.pause()
                    self.music_playing = False
                else:
                    pygame.mixer.unpause()
                    self.music_playing = True

    def play_music(self):
        """开始播放音乐"""
        if self.background_music and not self.music_playing:
            self.background_music.play(-1)  # -1表示循环播放
            self.music_playing = True

    def stop_music(self):
        """停止播放音乐"""
        if self.background_music:
            self.background_music.stop()
            self.music_playing = False




# 主程序流程 --------------------------------------------------
main_menu = MainMenu(screen, WIDTH, HEIGHT)   #初始化
if main_menu.run():
    #显示故事情节
    plot()

    #提示玩家输入昵称
    global player_nickname     #创建一个全局变量，保存之前输入的昵称，方便后续顶部状态栏显示
    player_nickname = input_nickname()

    # 进入游戏主界面
    game_interface = GameInterface(screen, WIDTH, HEIGHT)
    game_interface.play_music()  # 新增：启动游戏时自动播放
    game_interface.run()  # 当game_loop退出时会回到此处