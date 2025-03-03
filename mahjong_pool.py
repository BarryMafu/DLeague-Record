all_tiles = [
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 23, 24, 25, 26, 27, 28, 29,
    31, 32, 33, 34, 35, 36, 37, 38, 39,
    41, 42, 43, 44, 45, 46, 47,
]

def hai_to_str(hai: int) -> str:
    ten = hai // 10
    mod = hai % 10
    type_list = ["m", "p", "s", "z"]
    if ten <= 4:
        return str(mod) + type_list[ten - 1]
    elif ten == 5:
        return "0" + type_list[mod - 1]

class Pool:
    def __init__(self):
        # append 4 at a time
        def append4(l: list, item):
            l.extend([item] * 4)
        
        self.pool = []
        for item in all_tiles:
            append4(self.pool, item)
        # add aka dora
        self.pool.remove(15)
        self.pool.remove(25)
        self.pool.remove(35)
        self.pool.append(51)
        self.pool.append(52)
        self.pool.append(53)

    def draw(self, hai: int):
        try:
            self.pool.remove(hai)
        except ValueError:
            raise ValueError(f"尝试从牌山中取出 {hai_to_str(hai)}， 但牌山中已无该牌")

class Tehai:
    def __init__(self, hai: list[int]):
        self.tehai = hai.copy()
        self.pool = Pool()

        # Try if the tehai is valid 
        if len(hai) != 13:
            raise ValueError(f"手牌不是13张，输入了 {len(hai)} 张")

        try:
            for h in self.tehai:
                self.pool.draw(h)
        except ValueError: 
            raise ValueError(f"无法构建手牌：{hai_to_str(hai)}，可能是重复太多次")
    
    def draw_or_cut(self, h, hiki: bool):
        if hiki: self.draw(h)
        else: self.cut(h)

    def draw(self, hd):
        self.tehai.append(hd)
        self.pool.draw(hd)
    
    def cut(self, hc):
        try:
            self.tehai.remove(hc)
        except ValueError:
            raise ValueError(f"尝试从手牌中切出 {hai_to_str(hc)}， 但手牌中没有该牌")

    def remove_from_pool(self, hai, hint=""):
        try:
            self.pool.draw(hai)
        except ValueError as e:
            raise ValueError(hint + e) 

    def cuts(self, hcs):
        for hd in hcs:
            self.cut(hd)
