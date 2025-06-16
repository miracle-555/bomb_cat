import pygame
import random
import sys
from time import sleep
import you
import prop
import round
import monster
from monster import li_monsters
from collections import Counter


# 初始化Pygame
pygame.init()

# 设置游戏窗口尺寸（使用与主界面一致的尺寸）
WIDTH, HEIGHT = 1792 // 2, 1024 // 2  # 896x512，与main.py中保持一致
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("炸弹猫")

# 设置逻辑分辨率（用于布局计算）
SCREEN_WIDTH = WIDTH
SCREEN_HEIGHT = HEIGHT

# 确保所有界面元素使用SCREEN_WIDTH和SCREEN_WIDTH进行计算
clock = pygame.time.Clock()

LOG_PANEL_DRAGGING = False
LOG_PANEL_OFFSET = (0, 0)
LOG_PANEL_POS = [20, 300]  # 初始位置
LOG_PANEL_SIZE = (300, 160)  # 面板尺寸
MAX_LOG_LINES = 6  # 最大显示行数

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
    "bg": (30, 30, 30),  # 战斗背景色
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

IMAGES = {'battle_background': pygame.image.load('battle_bg.jpg')}

global debuff, buff
global debuff_monster, buff_monster
global designdated_card
global scavenger_skill
debuff = []
buff = []
designdated_card = []
buff_monster = []
debuff_monster = []
scavenger_skill = 0

def designdated_card_add(card):                    #指定卡牌函数
    global designdated_card
    designdated_card.append(card)


def purify_debuff():                              #净化函数
    global debuff
    debuff = []


def buff_add(addbuff):                            #增加buff函数
    global buff
    buff.append(addbuff)

def debuff_add(addbuff):                              #增加debuff函数
    global debuff
    debuff.append(addbuff)

def debuff_monster_add(addbuff):
    global debuff_monster
    debuff_monster.append(addbuff)

def buff_executed():                               #buff执行函数
    if "祈雨" in buff:
        prev_anger = gs.score_anger
        gs.score_anger -= 5
        gs.add_message(f"祈雨发动，愤怒值变化：{prev_anger} → {gs.score_anger}")


def debuff_executed():
    if "烈火" in debuff:
        prev_anger = gs.score_anger
        gs.score_anger += 4
        gs.add_message(f"烈火发动，愤怒值变化：{prev_anger} → {gs.score_anger}")

def buff_monster_executed():
    1

def debuff_monster_executed():
    if "祈雨" in debuff_monster:
        prev_anger = gs.score_anger
        gs.score_anger += 5
        gs.add_message(f"祈雨发动，愤怒值变化：{prev_anger} → {gs.score_anger}")



# 洗牌函数
def shuffle_cards(player, cards_hand, monster_cards=None):
    if player == 0:
        # 玩家牌库处理，使用深拷贝避免修改原始卡牌列表
        remaining = you.li_cards.copy()
        # 从剩余牌库中移除手牌中的卡牌（支持重复卡牌）
        for card in cards_hand:
            if card in remaining:
                remaining.remove(card)
        random.shuffle(remaining)
        return remaining
    else:
        # 怪物牌库处理
        cards = monster_cards.copy()
        random.shuffle(cards)
        return cards



# 使用面向对象的GameState类管理游戏状态
class GameState:
    def __init__(self):
        self.reset()
        self.current_round_num = 1  # 新增当前轮次
        self.coins = 0  # 本局游戏额外获得的金币

    # 摸牌函数
    def draw_card(self, player):
        global designdated_card
        try:
            if player == 0:  # 玩家摸牌
                if designdated_card == []:               #判断是否有指定抽牌
                    if not self.cards:
                        # 调用洗牌函数，传入当前手牌
                        self.cards = shuffle_cards(0, self.cards_hand)
                    card = self.cards.pop()
                    self.cards_hand.append(card)
                    self.add_message(f"你摸到了卡牌：{card}")
                else:                                     #进行指定抽牌，并且删除指定抽牌的命令。防止重复执行
                    self.cards_hand.append(designdated_card[0])
                    self.add_message(f"你摸到了卡牌：{designdated_card[0]}")
                    designdated_card.pop(0)


            else:  # 怪物摸牌`
                if player not in self.players_alive:  # 检查怪物是否存活
                    return
                idx = player - 1
                if not self.cards_monsters[idx]:
                    # 获取怪物牌库并洗牌
                    monster = self.players_alive[player]
                    self.cards_monsters[idx] = shuffle_cards(player, None, monster.cards)
                card = self.cards_monsters[idx].pop()
                self.cards_monsters_hand[idx].append(card)
        except IndexError:
            self.add_message("抽牌出错！", COLORS["warning"])

    def get_round_config(self, num):
        # 根据关卡号返回配置，需要与round.py配合实现
        if num == 1:
            return round.Round1
        elif num == 2:
            return round.Round2
        elif num == 3:
            return round.Round2
        elif num == 4:
            return round.Round4

    # 重置游戏状态
    def reset(self,round_num=1):
        # 核心游戏数据
        self.score_anger = random.randint(30, 80)
        self.players_alive = {0: "玩家"}
        self.cards_hand = []
        self.cards_monsters_hand = []
        self.flag = 0  # 0:进行中 1:胜利 -1:失败

        # 界面相关
        self.message_log = []
        self.input_text = ""
        self.input_active = False
        self.selected_card = None

        # 初始化关卡
        self.current_round_num = round_num  # 设置当前关卡号
        self.load_round(self.get_round_config(round_num))  # 加载对应关卡


        # 玩家摸4张
        for _ in range(4):
            self.draw_card(0)

        # 每个怪物摸4张
        for pid in self.players_alive:
            if pid != 0:  # 跳过玩家
                for _ in range(4):
                    self.draw_card(pid)

    def roll(self):                   #弃牌，重新摸四张牌
        self.cards_hand = []
        for _ in range(4):
            self.draw_card(0)

    def end_player_turn(self):
        self.is_player_turn = False

    # 加载指定关卡
    def load_round(self, round_obj):
        self.current_round = round_obj
        N = len(round_obj.li)
        li_monsters_now = [li_monsters[n - 1] for n in round_obj.li]

        # 初始化怪物
        self.players_alive = {0: "玩家"}
        for i in range(1, N + 1):
            self.players_alive[i] = li_monsters_now[i - 1]

        # 初始化牌库
        self.cards = shuffle_cards(0, self.cards_hand)
        self.cards_monsters = [shuffle_cards(i + 1, None, monster.cards) for i, monster in enumerate(li_monsters_now)]
        self.cards_monsters_hand = [[] for _ in range(N)]

    # 添加游戏消息
    def add_message(self, text, color=COLORS["text"]):
        self.message_log.append((text, color))
        if len(self.message_log) > 10:
            self.message_log.pop(0)

    #处理胜利情况
    def handle_victory(self):
        #解锁下一关（不超过最大关卡数）
        if self.current_round_num < 4:
            self.current_round_num += 1
            self.add_message(f"解锁第 {self.current_round_num} 关！")

        #重置游戏状态（保留金币）
        self.reset(self.current_round_num)

# 全局游戏状态
gs = GameState()

# 检测鼠标点击选择卡牌函数
def handle_card_selection():
    mouse_pos = pygame.mouse.get_pos()  # 获取当前鼠标的屏幕坐标
    screen_height = screen.get_height()

    card_start_x = 350  # 第一张手牌横坐标
    card_y = screen_height - 120  # 手牌纵坐标

    for i, card in enumerate(gs.cards_hand):
        card_rect = pygame.Rect(card_start_x + i * 90, card_y, 80, 110)
        if card_rect.collidepoint(mouse_pos):
            return card
    return None

# 战斗界面绘制函数
log_scroll = 0

def draw_interface():
    # 背景图
    global log_scroll
    IMAGES['battle_background'] = pygame.transform.scale(IMAGES['battle_background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(IMAGES['battle_background'], (0, 0))

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # 愤怒值
    anger_text = FONTS["normal"].render(
        f"猫猫愤怒值：{gs.score_anger}/100",
        True,
        COLORS["warning"] if gs.score_anger > 80 else COLORS["text"]
    )
    screen.blit(anger_text, (20, 20))

    # 存活单位初始位置
    y_pos = 80
    # 存储每个方框的矩形区域，用于鼠标检测
    hover_boxes = []
    for pid, entity in gs.players_alive.items():
        # 确定名称
        name = entity.name if pid != 0 else "玩家"
        # 渲染文本
        text = FONTS["normal"].render(f"{name} ({pid}号)", True, COLORS["text"])
        text_width, text_height = text.get_size()

        # 计算背景框的位置和大小
        box_x = screen_width - 200 - 10  # 文本左侧留10像素边距
        box_y = y_pos - 5  # 文本上方留5像素边距
        box_width = text_width + 20  # 文本左右各加10像素边距
        box_height = text_height + 10  # 文本上下各加5像素边距

        # 创建矩形对象用于鼠标检测
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        hover_boxes.append((box_rect, pid))  # 保存矩形和对应的玩家ID

        # 根据鼠标悬停状态选择背景颜色
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if box_rect.collidepoint(mouse_x, mouse_y):
            bg_color = (255, 165, 0, 150)  # 悬停时半透明橙色
        else:
            bg_color = (128, 128, 128, 100)  # 默认半透明灰色

        # 绘制背景框
        background = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        background.fill(bg_color)
        screen.blit(background, (box_x, box_y))

        # 绘制文本（在背景框上方）
        screen.blit(text, (screen_width - 200, y_pos))
        y_pos += 35

    # 消息日志（可滚动）
    log_panel = pygame.Surface(LOG_PANEL_SIZE, pygame.SRCALPHA)  # 消息面版
    log_panel.fill((128,128,128,100))

    y_msg = 10 - log_scroll * 25
    for msg, color in gs.message_log:
        msg_surf = FONTS["small"].render(msg, True, color)
        log_panel.blit(msg_surf, (10, y_msg))
        y_msg += 25

    screen.blit(log_panel, LOG_PANEL_POS)

    if len(gs.message_log) > MAX_LOG_LINES:  # 滚动条
        scroll_height = LOG_PANEL_SIZE[1] * MAX_LOG_LINES / len(gs.message_log)
        scroll_y = LOG_PANEL_POS[1] + (LOG_PANEL_SIZE[1] - scroll_height) * (log_scroll / len(gs.message_log))
        pygame.draw.rect(screen, COLORS["gray"], (LOG_PANEL_POS[0] + LOG_PANEL_SIZE[0] - 15, scroll_y, 10, scroll_height))

    # 玩家手牌（高亮）
    mouse_pos = pygame.mouse.get_pos()
    card_start_x = 350
    card_y = screen_height - 120
    for i, card in enumerate(gs.cards_hand):
        card_rect = pygame.Rect(card_start_x + i * 90, card_y, 80, 110)
        # 卡牌背景
        color = COLORS["gold"] if card_rect.collidepoint(mouse_pos) else COLORS["card_bg"]
        pygame.draw.rect(screen, color, card_rect, border_radius=8)
        # 卡牌文字
        card_text = FONTS["normal"].render(str(card), True, COLORS["text"])
        text_rect = card_text.get_rect(center=card_rect.center)
        screen.blit(card_text, text_rect)

    pygame.display.flip()  # 刷新显示


#不会高亮显示卡牌的备用绘制界面函数，写这个的原因是不知道为啥怪物回合时调用绘制函数，鼠标位置不更新，所以怪物回合时选的卡牌会一直高亮
def draw_interface_2():
    # 背景图
    global log_scroll
    IMAGES['battle_background'] = pygame.transform.scale(IMAGES['battle_background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(IMAGES['battle_background'], (0, 0))

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # 愤怒值
    anger_text = FONTS["normal"].render(
        f"猫猫愤怒值：{gs.score_anger}/100",
        True,
        COLORS["warning"] if gs.score_anger > 80 else COLORS["text"]
    )
    screen.blit(anger_text, (20, 20))

    # 存活单位初始位置
    y_pos = 80
    # 存储每个方框的矩形区域，用于鼠标检测
    hover_boxes = []
    for pid, entity in gs.players_alive.items():
        # 确定名称
        name = entity.name if pid != 0 else "玩家"
        # 渲染文本
        text = FONTS["normal"].render(f"{name} ({pid}号)", True, COLORS["text"])
        text_width, text_height = text.get_size()

        # 计算背景框的位置和大小
        box_x = screen_width - 200 - 10  # 文本左侧留10像素边距
        box_y = y_pos - 5  # 文本上方留5像素边距
        box_width = text_width + 20  # 文本左右各加10像素边距
        box_height = text_height + 10  # 文本上下各加5像素边距

        # 创建矩形对象用于鼠标检测
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        hover_boxes.append((box_rect, pid))  # 保存矩形和对应的玩家ID

        # 根据鼠标悬停状态选择背景颜色
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if box_rect.collidepoint(mouse_x, mouse_y):
            bg_color = (255, 165, 0, 150)  # 悬停时半透明橙色
        else:
            bg_color = (128, 128, 128, 100)  # 默认半透明灰色

        # 绘制背景框
        background = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        background.fill(bg_color)
        screen.blit(background, (box_x, box_y))

        # 绘制文本（在背景框上方）
        screen.blit(text, (screen_width - 250, y_pos))
        y_pos += 35

    # 消息日志（可滚动）
    log_panel = pygame.Surface(LOG_PANEL_SIZE, pygame.SRCALPHA)  # 消息面版
    log_panel.fill((128, 128, 128, 100))

    y_msg = 10 - log_scroll * 25
    for msg, color in gs.message_log:
        msg_surf = FONTS["small"].render(msg, True, color)
        log_panel.blit(msg_surf, (10, y_msg))
        y_msg += 25

    screen.blit(log_panel, LOG_PANEL_POS)

    if len(gs.message_log) > MAX_LOG_LINES:  # 滚动条
        scroll_height = LOG_PANEL_SIZE[1] * MAX_LOG_LINES / len(gs.message_log)
        scroll_y = LOG_PANEL_POS[1] + (LOG_PANEL_SIZE[1] - scroll_height) * (log_scroll / len(gs.message_log))
        pygame.draw.rect(screen, COLORS["gray"],
                         (LOG_PANEL_POS[0] + LOG_PANEL_SIZE[0] - 15, scroll_y, 10, scroll_height))

    # 玩家手牌（高亮）
    mouse_pos = pygame.mouse.get_pos()
    card_start_x = 350
    card_y = screen_height - 120
    for i, card in enumerate(gs.cards_hand):
        card_rect = pygame.Rect(card_start_x + i * 90, card_y, 80, 110)
        # 卡牌背景
        color = COLORS["card_bg"]
        pygame.draw.rect(screen, color, card_rect, border_radius=8)
        # 卡牌文字
        card_text = FONTS["normal"].render(str(card), True, COLORS["text"])
        text_rect = card_text.get_rect(center=card_rect.center)
        screen.blit(card_text, text_rect)

    pygame.display.flip()  # 刷新显示               #


# 出牌函数
def play_card(player, card, choose = 0):
    try:
        if player == 0:  # 玩家出牌逻辑
            gs.cards_hand.remove(card)
            gs.add_message(f"你使用了 {'数字牌' if isinstance(card, int) else '功能牌'}：{card}")

            # 数字牌处理
            if isinstance(card, int):
                gs.score_anger += card
                check_anger(0)  # 检查愤怒值状态
                gs.add_message(f"猫猫愤怒值: {gs.score_anger - card} → {gs.score_anger}")

            # 功能牌处理
            else:
                card_obj = prop.dict_props[card]  # 获取功能牌对象并执行效果
                gs.add_message(f"触发效果：{card_obj.function}（{card}）", COLORS["text"])

                # 执行卡牌功能
                prev_anger = gs.score_anger
                card_obj.card_func(player, gs.score_anger, gs.cards_hand, gs.cards_monsters_hand, gs.players_alive,choose)

                # 显示愤怒值变化
                if gs.score_anger != prev_anger:
                    gs.add_message(f"愤怒值变化：{prev_anger} → {gs.score_anger}")



        else:  # 怪物出牌逻辑
            monster = gs.players_alive[player]

            # 自动选择卡牌
            monster_card = monster.func_card(gs.cards_monsters_hand[player - 1], gs.score_anger)
            gs.add_message(f"{monster.name} ({player}号) 使用了 {'数字牌' if isinstance(monster_card, int) else '功能牌'}：{monster_card}")

            # 数字牌处理
            if isinstance(monster_card, int):
                gs.score_anger += monster_card
                check_anger(player)
                gs.cards_monsters_hand[player - 1].remove(monster_card)
                gs.add_message(f"猫猫愤怒值：{gs.score_anger - monster_card} → {gs.score_anger}")

            # 功能牌处理
            else:
                card_obj = prop.dict_props[monster_card]
                gs.add_message(f"{monster.name} 触发效果：{card_obj.function}", COLORS["text"])
                card_obj.card_func(player, gs.score_anger, gs.cards_hand, gs.cards_monsters_hand, gs.players_alive)

    # 异常处理
    except ValueError as ve:
        gs.add_message(f"操作失败：{str(ve)}" if str(ve) else "无效的卡牌操作！", COLORS["warning"])
    except KeyError:
        gs.add_message("错误：未定义的功能牌！", COLORS["warning"])
    except Exception as e:
        gs.add_message(f"未知错误：{str(e)}", COLORS["warning"])

# 检查愤怒值状态函数
def check_anger(current_player):
    global gs
    global scavenger_skill
    if gs.score_anger >= 100:
        if current_player == 0:
            # 玩家导致愤怒值超限，游戏失败
            gs.add_message("猫猫愤怒值爆炸！你输了", COLORS["warning"])
            gs.flag = -1
        else:
            # 怪物导致愤怒值超限，淘汰该怪物并调整愤怒值
            monster = gs.players_alive.get(current_player)
            if monster:
                # 淘汰怪物
                if monster.name == "死灵髅楼":
                    gs.cards_hand[random.randint(0, 3)] = 10

                if monster.name == "扒手":
                    gs.coins += 500

                del gs.players_alive[current_player]
                scavenger_skill += 1
                gs.add_message(f"猫猫愤怒值爆炸！{monster.name}{current_player}号倒地", COLORS["warning"])
                if monster.name == "死灵髅楼":
                    gs.add_message(f"死灵髅楼死亡,玩家手牌随机增加一张10", COLORS["warning"])
                # 调整愤怒值：199 - 当前值
                gs.score_anger = max(199 - gs.score_anger, 0)
                # 检查是否所有怪物已被淘汰
                if len(gs.players_alive) == 1 and 0 in gs.players_alive:  # 仅剩玩家
                    gs.handle_victory()
                    gs.add_message("所有怪物已被击败，恭喜你获得本局胜利！", COLORS["text"])
                    gs.flag = 1

# 显示游戏结束界面函数
def show_game_result():
    # 创建半透明背景层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 半透明黑色背景
    screen.blit(overlay, (0, 0))

    # 游戏结果文本
    result_text = FONTS['title'].render(
        "游戏胜利！" if gs.flag == 1 else "游戏失败...",
        True,
        COLORS["gold"] if gs.flag == 1 else COLORS["warning"]
    )
    result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(result_text, result_rect)

    # 附加信息文本
    info_text = FONTS['normal'].render(
        f"获得金币: {gs.coins + (100 * gs.current_round_num if gs.flag == 1 else 0)}",
        True,
        COLORS["text"]
    )
    info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(info_text, info_rect)

    # 提示文本
    prompt_text = FONTS['medium'].render(
        "点击任意位置继续...",
        True,
        COLORS["text"]
    )
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(prompt_text, prompt_rect)

    pygame.display.flip()

    # 等待重新开始
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return 'victory' if gs.flag == 1 else 'failed'
# 游戏主循环函数
def game_loop(round_num=1):
    global LOG_PANEL_DRAGGING, LOG_PANEL_OFFSET, LOG_PANEL_POS, log_scroll
    clock = pygame.time.Clock()
    is_player_turn = True
    is_buff_execute = True
    is_debuff_execute = True
    is_buff_monster_execute = True
    is_debuff_monster_execute = True
    choose_card = False

    if round_num == 1:
        gs.load_round(round.Round1)
    elif round_num == 2:
        gs.load_round(round.Round2)
    elif round_num == 3:
        gs.load_round(round.Round3)
    elif round_num == 4:
        gs.load_round(round.Round4)

    global debuff, buff
    global debuff_monster, buff_monster
    global designdated_card
    global scavenger_skill
    debuff = []
    buff = []
    buff_monster = []
    debuff_monster = []
    designdated_card = []
    scavenger_skill = 0
    gs.coins = 0
    gs.flag = 0

    while True:
        # 0表示游戏进行中，1表示你赢了，-1表示你输了
        if gs.flag != 0:
            result = show_game_result()  # 获取结果
            coin_win_the_battle = 100 * gs.current_round_num if result == 'victory' else 0
            return {
                'status': result,
                'coins': coin_win_the_battle + gs.coins}

        for event in pygame.event.get():
            # 若检测到QUIT事件（如点击窗口关闭按钮），则调用pygame.quit()和sys.exit()安全退出游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 消息面板拖动处理
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查是否点击了日志面板
                panel_rect = pygame.Rect(
                    LOG_PANEL_POS[0],
                    LOG_PANEL_POS[1],
                    LOG_PANEL_SIZE[0],
                    LOG_PANEL_SIZE[1]
                )
                if panel_rect.collidepoint(event.pos):
                    LOG_PANEL_DRAGGING = True
                    LOG_PANEL_OFFSET = (
                        event.pos[0] - LOG_PANEL_POS[0],
                        event.pos[1] - LOG_PANEL_POS[1]
                    )

            elif event.type == pygame.MOUSEMOTION and LOG_PANEL_DRAGGING:
                # 计算新位置并限制在屏幕范围内
                new_x = event.pos[0] - LOG_PANEL_OFFSET[0]
                new_y = event.pos[1] - LOG_PANEL_OFFSET[1]

                # 边界检查（保留10像素边距）
                new_x = max(10, min(new_x, SCREEN_WIDTH - LOG_PANEL_SIZE[0] - 10))
                new_y = max(10, min(new_y, SCREEN_HEIGHT - LOG_PANEL_SIZE[1] - 10))

                LOG_PANEL_POS = [new_x, new_y]

            elif event.type == pygame.MOUSEBUTTONUP:
                LOG_PANEL_DRAGGING = False

            # 消息日志滚动
            if event.type == pygame.MOUSEWHEEL:
                panel_rect = pygame.Rect(LOG_PANEL_POS[0], LOG_PANEL_POS[1], LOG_PANEL_SIZE[0], LOG_PANEL_SIZE[1])
                if panel_rect.collidepoint(pygame.mouse.get_pos()):  # 检查鼠标是否在日志面板区域
                    log_scroll = max(0, min(log_scroll + event.y, len(gs.message_log) - MAX_LOG_LINES))

            # 玩家回合
            if is_player_turn:
                if is_buff_execute:  # 执行buff和debuff
                    buff_executed()
                    is_buff_execute = False
                if is_debuff_execute:
                    debuff_executed()
                    is_debuff_execute = False
                if event.type == pygame.MOUSEBUTTONDOWN and not LOG_PANEL_DRAGGING:
                    if not choose_card:
                        selected = handle_card_selection()  # 鼠标点击选择卡牌
                        if selected is not None:
                            if selected not in prop.choose_props:
                                play_card(0, selected)  # 玩家出牌
                                gs.draw_card(0)  # 玩家摸牌
                                is_player_turn = False  # 玩家回合结束，轮到怪物
                                is_buff_execute = True  # 回合结束，重置buff状态
                                is_debuff_execute = True  ##回合结束，重置debuff状态
                            else:
                                choose_card = True
                                gs.add_message(f"请点击该功能牌你想作用的对象：")
                    else:
                        choose = prop.choose_monster(pygame.mouse.get_pos(), len(gs.players_alive))
                        if choose != 0:  # 如果选择了怪物就开始执行，否则继续选择
                            play_card(0, selected, choose)
                            gs.draw_card(0)  # 玩家摸牌
                            is_player_turn = False  # 玩家回合结束，轮到怪物
                            choose_card = False  # 选择结束
                            is_buff_execute = True  # 回合结束，重置buff状态
                            is_debuff_execute = True  ##回合结束，重置debuff状态

        # 怪物回合
        if not is_player_turn and gs.flag == 0:
            if is_buff_monster_execute:  # 执行buff_monster和debuff_monster
                buff_monster_executed()
                is_buff_monster_execute = False
            if is_debuff_monster_execute:
                debuff_monster_executed()
                is_debuff_monster_execute = False
            for pid in list(gs.players_alive.keys()):
                if pid == 0:
                    continue  # 跳过玩家
                if pid not in gs.players_alive:
                    continue  # 跳过已淘汰的怪物

                monster = gs.players_alive[pid]
                hand = gs.cards_monsters_hand[pid - 1]

                if monster.name == "清道夫":
                    if scavenger_skill:
                        gs.cards_monsters_hand[pid - 1][random.randint(0, 3)] = 0
                        scavenger_skill -= 1

                if not hand:
                    gs.draw_card(pid)
                monster_card = monster.func_card(hand, gs.score_anger)

                if monster_card is not None:
                    play_card(pid, monster_card)
                    gs.draw_card(pid)
                    sleep(0.7)

                if gs.flag != 0:
                    break
                draw_interface()

            is_player_turn = True  # 怪物回合结束，回到玩家
            is_buff_monster_execute = True  # 回合结束，重置buff状态
            is_debuff_monster_execute = True  ##回合结束，重置debuff状态

        draw_interface()
        clock.tick(60)


if __name__ == "__main__":
    # pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    game_loop()