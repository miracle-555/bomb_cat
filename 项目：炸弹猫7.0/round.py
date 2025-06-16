# 本py文件用来记录关卡
class Round:
    def __init__(self,li_monster_number):
        self.li = li_monster_number

    def exhibit(self):
        # li_monster_exhibited = # 用来展示给玩家看的
        print(" ".join(name for name in self.li_monster))   


Round1 = Round([1,1])
Round2 = Round([1, 2])
Round3 = Round([1, 2, 3])
Round4 = Round([2, 2, 3, 4])
Round5 = Round([3,4,5,6])
Round6 = Round([7.8,9])
Round7 = Round([9,10])
Round8 = Round([11])