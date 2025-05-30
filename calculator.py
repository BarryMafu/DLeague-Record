def to_point_zumo(h, f, is_oya):
    to_point_dict = {
        (1, 30): (300, 500),
        (1, 40): (400, 700),
        (1, 50): (400, 800),
        (1, 60): (500, 1000), 
        (1, 70): (600, 1200),  
        (1, 80): (700, 1300),
        (1, 90): (800, 1500),  
        (1, 100): (800, 1600),
        (1, 110): (900, 1800),
        (2, 20): (400, 700),
        (2, 25): (400, 800),
        (2, 30): (500, 1000),
        (2, 40): (700, 1300),
        (2, 50): (800, 1600),
        (2, 60): (1000, 2000),
        (2, 70): (1200, 2300),
        (2, 80): (1300, 2600),
        (2, 90): (1500, 2900),
        (2, 100): (1600, 3200),
        (2, 110): (1800, 3600),
        (3, 20): (700, 1300),
        (3, 25): (800, 1600),
        (3, 30): (1000, 2000),
        (3, 40): (1300, 2600),
        (3, 50): (1600, 3200),
        (4, 20): (1300, 2600),
        (4, 25): (1600, 3200),
    }
    s = ""
    oya = hima = 0
    if h >= 11: 
        s = "三倍満"
        oya, hima = 12000, 6000
    elif h >= 8: 
        s = "倍満"
        oya, hima = 8000, 4000
    elif h >= 6: 
        s = "跳満"
        oya, hima = 6000, 3000
    elif (h >= 5) or (h >= 4 and f >= 30) or (h == 3 and f >= 60): 
        s = "満貫"
        oya, hima = 4000, 2000
    else:
        s = f"{f}符{h}飜"
        hima, oya = to_point_dict[(h, f)]
    if is_oya:
        return s + f"{oya}点∀", oya
    else:
        return s + f"{hima}-{oya}点", hima, oya
    
def to_point_ron(h, f, is_oya):
    to_point_dict = {
        (1, 30): (1000, 1500),
        (1, 40): (1300, 2000),
        (1, 50): (1600, 2400),
        (1, 60): (2000, 2900),
        (1, 70): (2300, 3400),
        (1, 80): (2600, 3900),
        (1, 90): (2900, 4400),
        (1, 100): (3200, 4800),
        (1, 110): (3600, 5300),
        (2, 25): (1600, 2400),
        (2, 30): (2000, 2900),
        (2, 40): (2600, 3900),
        (2, 50): (3200, 4800),
        (2, 60): (3900, 5800),
        (2, 70): (4500, 6800),
        (2, 80): (5200, 7700),
        (2, 90): (5800, 8700),
        (2, 100): (6400, 9600),
        (2, 110): (7100, 10600),
        (3, 25): (3200, 4800),
        (3, 30): (3900, 5800),
        (3, 40): (5200, 7700),
        (3, 50): (6400, 9600),
        (4, 25): (6400, 9600),
    }
    s = ""
    oya = hima = 0
    if h >= 11: 
        s = "三倍満"
        oya, hima = 32000, 24000
    elif h >= 8:
        s = "倍満"
        oya, hima = 24000, 16000
    elif h >= 6:
        s = "跳満"
        oya, hima = 18000, 12000
    elif (h >= 5) or (h >= 4 and f >= 30) or (h == 3 and f >= 60):
        s = "満貫"
        oya, hima = 12000, 8000
    else:
        s = f"{f}符{h}飜"
        hima, oya = to_point_dict[(h, f)]
    if is_oya:
        return s + f"{oya}点", oya
    else:
        return s + f"{hima}点", hima

    
if __name__ == "__main__":
    print(to_point_zumo(4, 20, True))
    print(to_point_ron(31, 30, False))