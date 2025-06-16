# 此py文件下是各种功能牌
import pygame
import my_game
import random
from monster import li_monsters

# 全局游戏状态
gs = my_game.GameState()


def choose_monster(mouse_pos, count):           # 用来选择功能牌作用的对象
    mouse_x, mouse_y = mouse_pos         #解包鼠标位置
    # 存活怪物初始位置
    y_pos = 140
    # 存储每个方框的矩形区域，用于鼠标检测
    hover_boxes = []
    for pid in range(1, count):
        box_rect = pygame.Rect(646, y_pos, 250, 40)
        y_pos += 40
        hover_boxes.append((box_rect,pid))
    # 根据鼠标点击位置确定作用对象
    flag = 0
    for (box_rect, pid) in hover_boxes:
        if box_rect.collidepoint(mouse_x, mouse_y ):
            flag = 1
            return pid

    #若没有选择怪物则返回0，gameloop函数继续执行选择命令，直到玩家选择怪物

    if flag == 0:
        return 0


class Prop:
    def __init__(self, name, serial_number, function):
        self.name = name
        self.number = serial_number
        self.function = function

    def card_func(self, player, score_anger, cards_hand, cards_monsters_hand, players_alive, choose = 0):
        if self.name in ("寒冰"):
            my_game.gs.score_anger -= 10
            print(f"猫猫愤怒值降10, 当前猫猫愤怒值为：{score_anger}")

        elif self.name in ("炽热"):
            if player:          # player不为0
                j = 0
                for card in cards_hand:
                    if isinstance(card, int):
                        my_game.gs.cards_hand[j] += 2
                    else:
                        continue
                    j += 1
            else:
                i = 0
                for card in cards_monsters_hand[choose - 1]:
                    if isinstance(card, int):
                        my_game.gs.cards_monsters_hand[choose - 1][i] += 2
                    else:
                        continue
                    i += 1
                monster = players_alive[choose]
                print(f"{monster.name}({choose})的所有数字牌+2")

        elif self.name in ("下注"):
            my_game.gs.cards_hand = []
            for _ in range(3):
                my_game.gs.draw_card(0)

        elif self.name in ("净化"):
            my_game.purify_debuff()                     #直接在my_game里写了修改全局变量的函数，然后在这里引用就可以了

        elif self.name in ("先机"):
            my_game.gs.score_anger += 3
            my_game.designdated_card_add(0)

        elif self.name in ("喷发"):
            my_game.gs.cards_monsters_hand[choose - 1][random.randint(0, 3)] = 10

        elif self.name in ("祈雨"):
            my_game.buff_add("祈雨")
            my_game.debuff_monster_add("祈雨")

        elif self.name in ("淘金"):
            my_game.gs.coins += 500

        elif self.name in ("冰爆术"):
            my_game.gs.score_anger -= 20
            my_game.gs.cards_hand.pop(random.randint(0, 2))
            my_game.gs.draw_card(0)
        
        elif self.name in("薄荷"):
            count = random.randint(1, 3)
            for _ in range(count):
                idx = random.randint(0, len(cards_hand)-1)
                if isinstance(cards_hand[idx], int):
                    cards_hand[idx] = 0
        
        elif self.name in(""):
            if choose != 0:  # 确保选择了目标
                # 交换手牌
                player_hand = cards_hand.copy()
                monster_hand = cards_monsters_hand[choose-1].copy()
                cards_hand = monster_hand
                cards_monsters_hand[choose-1] = player_hand
                gs.add_message(f"与{players_alive[choose].name}互换了手牌！")

        elif self.name in ("烈火"):
            my_game.debuff_add("烈火")

        elif self.name in ("召唤"):
            my_game.gs.players_alive.append(li_monsters[7])

        elif self.name in ("偷窃"):
            my_game.gs.coins -= 200
        
        elif self.name in ("Jocker"):
            if random.random() < 0.5:  # 50%好效果
                prev = score_anger
                score_anger = max(1, score_anger // 2)  # 愤怒值减半(至少为1)
                gs.add_message(f"幸运Joker！愤怒值减半：{prev} → {score_anger}")
            else:  # 50%坏效果：手牌数字全部翻倍
                new_hand = []
                for card in cards_hand:
                    if isinstance(card, int):
                        new_hand.append(min(card * 2, 10))  # 怒气值翻倍但上限为10
                    else:
                        new_hand.append(card)  # 功能牌不变
                cards_hand = new_hand
                gs.add_message("疯狂Joker！手牌数字全部翻倍了！") 
        elif 1:
            1  
        return score_anger, cards_hand, cards_monsters_hand, players_alive


blank = Prop("空白", 0, "无效果")
frozen = Prop("寒冰", 1, "令猫猫愤怒值下降10")
redhot = Prop("炽热", 2, "目标手中所有数字牌+2")
roll = Prop("下注", 3, "弃掉所有手牌，重新抽四张牌")
purify = Prop("净化", 4, "去除所有debuff")
advantage = Prop("先机", 5, "增加3怒气，使下一回合抽到的牌一定为0")
erupt = Prop("喷发", 6, "使指定的目标的随机一张牌变为10")
rain_pray = Prop("祈雨", 7, "获得buff：每次到自己的回合时，使怒气减5,到下个怪物回合，再使怒气加5")
gold = Prop("淘金", 8, "获得500金币")
ice_magic = Prop("冰爆术", 9, "随机弃一张牌，使怒气降低20")
mint = Prop("薄荷",10,"随机将1张手牌变为0")
exchange = Prop("交换",11,"与目标怪物交换手牌")
gamble = Prop("放手一搏",12,"50%概率怒气值增加10或0")

#怪物卡牌
fire = Prop("烈火", 13, "使用后给玩家增加debuff:每次轮到玩家的回合，怒气加4")
summon = Prop("召唤", 14, "使用后召唤一个死灵骷髅")
steal = Prop("偷窃", 15, "使用后偷取玩家200金币")
jocker = Prop("Jocker",16,"50%概率愤怒值减半，50%概率手牌怒气值均翻倍")

# 列表便于图鉴中展示
li_props = [blank, frozen, redhot, roll, purify, advantage, erupt, rain_pray, gold, ice_magic,mint, exchange, gamble]
# 字典便于在game函数中调用
#总卡牌
dict_props = {"空": blank, "寒冰": frozen, "炽热": redhot, "下注": roll, "净化":purify, "先机":advantage, "喷发":erupt, "祈雨":rain_pray, "淘金":gold, "冰爆术":ice_magic, "薄荷":mint, "交换":exchange, 
              "放手一搏": gamble, "烈火":fire,"召唤": summon, "偷窃":steal, "Jocker": jocker}  # "空"占位
#玩家卡牌
dict_props_palyer = {"空": blank, "寒冰": frozen, "炽热": redhot, "下注": roll, "净化":purify, "先机":advantage, "喷发":erupt, "祈雨":rain_pray, "淘金":gold, "冰爆术":ice_magic, "薄荷":mint, "交换":exchange, "放手一搏": gamble}  # "空"占位

choose_props = {"炽热": redhot, "喷发": erupt}             #需要指定玩家的卡牌集合