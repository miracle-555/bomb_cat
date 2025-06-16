import random

class Monster:
    def __init__(self, nickname, serial_number, cards, strategy):
        self.name = nickname   # 怪物的昵称
        self.number = serial_number   # 怪物的编号
        self.cards = cards             # 怪物的牌库
        self.strategy = strategy      # 怪物的出牌策略

    def func_card(self, hand, current_anger):   # 怪物的出牌机制(此函数的多样性是该项目最核心的内容之一)
        # 预处理：过滤None值
        valid_hand = [c for c in hand if c is not None]

        # 嘤嘤怪：完全随机出牌
        if self.name == "嘤嘤怪":
            return random.choice(valid_hand) if valid_hand else None

        # 幸运儿：优先出小牌，将功能牌视为0
        elif self.name == "幸运儿":
            temp_hand = []
            for card in valid_hand:
                if isinstance(card, int):
                    temp_hand.append(card)
                else:
                    temp_hand.append(0)  # 功能牌视为0
            return min(temp_hand) if temp_hand else None

        # 胆小鬼：始终出最小牌，功能牌视为0
        elif self.name == "胆小鬼":
            temp_hand = []
            for card in valid_hand:
                if isinstance(card, int):
                    temp_hand.append(card)
                else:
                    temp_hand.append(0)  # 功能牌视为0
            return min(temp_hand) if temp_hand else None

        # 小丑：有10%概率使用Joker牌
        elif self.name == "小丑":
            # 优先使用Joker牌
            jokers = [c for c in valid_hand if c == "Joker"]
            if jokers and random.random() < 0.1:
                return "Joker"
            # 否则出最小数字牌
            numbers = [c for c in valid_hand if isinstance(c, int)]
            return min(numbers) if numbers else None

        # 魔女：愤怒值高时优先使用功能牌
        elif self.name == "魔女":
            if current_anger > 70:
                func_cards = [c for c in valid_hand if not isinstance(c, int)]
                if func_cards:
                    return random.choice(func_cards)
            # 否则随机出牌
            return random.choice(valid_hand) if valid_hand else None

        # 默认策略：随机出牌
        else:
            return random.choice(valid_hand) if valid_hand else None

    def exhibit(self):
        print(self.strategy)

# 怪物总列表
li_monsters = [
    Monster("史莱姆", 1, [i for i in range(11)], "撞击：随机出一张牌"),
    Monster("幸运儿", 2, [0, 0, 1, 1, 2, 2, 3, 4, 5, 6], "好运：卡牌堆里小牌多"),
    Monster("胆小鬼", 3, [i for i in range(9)], "谨慎：始终出最小的牌(因为过于谨慎, 所以功能牌只会被视为数字牌0打出)"),
    Monster("小丑", 4, [i for i in range(9)] + ["Joker"], "有10%概率使用Joker牌"),
    Monster("清道夫", 5, [i for i in range(11)], "每当有怪物死亡时，将手牌中的随即一张替换为0"),
    Monster("阎魔", 6, [i for i in range(11)] + ["烈火"], "拥有特殊牌烈火，使用后给玩家增加debuff:每次轮到玩家的回合，怒气加4"),
    Monster("死灵髅楼", 7, [i for i in range(5, 11)], "死亡后随即将玩家的一张牌替换为10"),
    Monster("死灵法师", 8, [i for i in range(11)] + ["召唤"], "拥有特殊牌召唤，使用后召唤一个死灵骷髅"),
    Monster("扒手", 9, [i for i in range(11)] + ["偷窃"], "拥有特殊牌偷窃，使用后偷取玩家200金币,被击杀可重新获取,并额外获得300金币"),
    Monster("狐狸", 10, [i for i in range(11)] + ["薄荷"], "拥有将随机手牌清零的能力"),
Monster("魔女", 11, [i for i in range(5)] * 2 + ["炽热", "寒冰", "光明", "黑暗", "紊乱"], "愤怒值高时优先使用功能牌"),
]