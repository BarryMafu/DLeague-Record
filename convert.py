import codecs
import json

#TODO: 你只需要修改如下两项即可
folder_name = "Split Records/S2_G50/"
file_name = folder_name + "S2_G50_tb"

input_file = file_name + ".txt"
output_file = file_name + ".json"

lines = []

print("Reading & cleaning file: " + input_file + " ... (1 / 4)")

with codecs.open(input_file, 'r', 'utf-8') as file:
    counter = 0
    for line in file:
        line = line.strip()
        line = line.replace(' ', '')

        if len(line)>0 and line[0] == "%": continue

        if "%" in line:
            line = line[:line.index("%")]

        line = line.lower()
        lines.append(line)

data = {}

print("Parsing Header ... (2 / 4)")

position_dict = {
    "e": 0,
    "s": 1,
    "w": 2,
    "n": 3
}

season_id, game_id = lines.pop(0).split(",")
start_position = position_dict[lines.pop(0)]
player_name = lines.pop(0)
data["title"] = "DLeague S" + season_id + " G" + game_id
data["start_position"] = start_position
data["name"] = player_name

print("Parsing Moves ... (3 / 4)")

def is_tile(tile : str) -> bool:
    return len(tile) == 2 and tile[0] in "0123456789" and tile[1] in "mspz"

def tile_to_num(tile : str) -> int:
    type_dict = {
        "m": 1,
        "p": 2,
        "s": 3,
        "z": 4
    }
    t = type_dict[tile[1]]
    if(tile[0] == "0"): return 50 + t
    return t * 10 + int(tile[0])

def parse_tiles(tiles : str) -> list:
    l = []
    temp = []
    for c in tiles:
        if c in "0123456789": temp.append(c)
        if c in "mspz":
            l.extend([t + c for t in temp])
            temp = []
    return [tile_to_num(t) for t in l]

all_games = []
game = []

def parse_all(tile):
    if tile == "": return 60
    if is_tile(tile): return tile_to_num(tile)
    if tile[0] in "c":
        tile = tile[1:]
        index_left = tile.index("[")
        index_right = tile.index("]")
        tile_chi = tile[index_left + 1: index_right]
        tile = tile[:index_left] + tile[index_right + 1:]
        string_chi = str(tile_to_num(tile_chi))
        string_else = "".join([str(t) for t in parse_tiles(tile)])
        return "c" + string_chi + string_else
    if tile[0] in "pamk":
        tile1 = tile[1:]
        index_left = tile1.index("[")
        index_right = tile1.index("]")
        tile_move = tile1[index_left + 1: index_right]
        tile_move_left = tile1[:index_left]
        tile_move_right = tile1[index_right + 1:]
        string_move = "".join([str(t) for t in parse_tiles(tile_move)])
        string_left = "".join([str(t) for t in parse_tiles(tile_move_left)])
        string_right = "".join([str(t) for t in parse_tiles(tile_move_right)])
        return string_left + tile[0] + string_move + string_right
    if tile[0] in "r":
        return "r" + str(tile_to_num(tile[1:]))
    

    

def parse_nagashi(nagashi):
    if "<" in nagashi:
        return "流局", [nagashi.replace("<", "").split(",")]
    if ">" in nagashi:
        houjuu_mono, agari_mono = nagashi.split(">")
        return "和了", [agari_mono, houjuu_mono]

def parse_yaku(l):
    yaku, fu = l.split("#")
    yaku = yaku.split(";")
    fu = int(fu)
    han = sum([int(y.split(",")[1]) for y in yaku])
    yaku = sorted(yaku, key=lambda x: x.split(",")[0])
    yaku_dict = {
        "lz,1": "立直(1飜)",
        "llz,2": "両立直(2飜)",
        "yf,1": "一発(1飜)", 
        "zm,1": "門前清自摸和(1飜)",
        "d,1": "ドラ(1飜)",
        "a,1": "赤ドラ(1飜)",
        "u,1": "裏ドラ(1飜)",
        "d,2": "ドラ(2飜)",
        "a,2": "赤ドラ(2飜)",
        "u,2": "裏ドラ(2飜)",
        "d,3": "ドラ(3飜)",
        "a,3": "赤ドラ(3飜)",
        "u,3": "裏ドラ(3飜)",
        "d,4": "ドラ(4飜)",
        "u,4": "裏ドラ(4飜)",
        "d,5": "ドラ(5飜)",
        "u,5": "裏ドラ(5飜)",
        "d,6": "ドラ(6飜)",
        "u,6": "裏ドラ(6飜)",
        "d,7": "ドラ(7飜)",
        "u,7": "裏ドラ(7飜)",
        "d,8": "ドラ(8飜)",
        "u,8": "裏ドラ(8飜)",
        "d,9": "ドラ(9飜)",
        "u,9": "裏ドラ(9飜)",
        "d,10": "ドラ(10飜)",
        "u,10": "裏ドラ(10飜)",
        "d,11": "ドラ(11飜)",
        "u,11": "裏ドラ(11飜)",
        "d,12": "ドラ(12飜)",
        "u,12": "裏ドラ(12飜)",
        "ph,1": "平和(1飜)",
        "dyj,1": "断幺九(1飜)",
        "qg,1":"槍槓(1飜)",
        "lskh,1":"嶺上開花(1飜)",
        "hdmy,1":"海底摸月(1飜)",
        "hdly,1":"河底撈魚(1飜)",
        "ssts,1": "三色同順(1飜)",
        "ssts,2": "三色同順(2飜)",
        "sstk,2": "三色同刻(2飜)",
        "yqtg,1": "一気通貫(1飜)",
        "yqtg,2": "一気通貫(2飜)",
        "5z,1": "役牌 白(1飜)",
        "6z,1": "役牌 發(1飜)",
        "7z,1": "役牌 中(1飜)",
        "1z,1": "自風 東(1飜)",
        "2z,1": "自風 南(1飜)",
        "3z,1": "自風 西(1飜)",
        "4z,1": "自風 北(1飜)",
        "cf1z,1": "場風 東(1飜)",
        "cf2z,1": "場風 南(1飜)",
        "qdz,1": "七対子(2飜)",
        "hqdyj,1": "混全帯幺九(1飜)",
        "hqdyj,2": "混全帯幺九(2飜)", 
        "sangz,2": "三槓子(2飜)",
        "ddh,2": "対々和(2飜)",
        "sanak,2": "三暗刻(2飜)",
        "xsy,2": "小三元(2飜)",
        "hlt,2": "混老頭(2飜)",
        "lbk,3": "二盃口(3飜)",
        "cqdyj,2": "純全帯幺九(2飜)",
        "cqdyj,3": "純全帯幺九(3飜)",
        "hys,2": "混一色(2飜)",
        "hys,3": "混一色(3飜)",
        "qys,5": "清一色(5飜)",
        "qys,6": "清一色(6飜)",
        "lys,-1":"緑一色(満貫)",
        "dsy,-1":"大三元(役満)",
        "sinak,-1":"四暗刻(役満)",
        "siakdq,-1":"四暗刻単騎(役満)",
        "dsx,-1":"大四喜(役満)",
        "xsx,-1":"小四喜(役満)",
        "zys,-1":"字一色(役満)",
        "qlt,-1":"清老頭(役満)",
        "gsws,-1":"国士無双(役満)",
        "gswsssm,-1":"国士無双１３面(役満)",
        "jlbd,-1":"九蓮宝燈(役満)",
        "czjlbd,-1":"純正九蓮宝燈(役満)",
        "sigz,-1":"四槓子(役満)",
        "th,-1":"天和(役満)",
        "dh,-1":"地和(役満)"
    }
    yakus = [
        yaku_dict[y] for y in yaku
    ]

    return [han, fu], yakus
    

while True:
    if len(lines) == 0: break
    states = [int(x) for x in lines.pop(0).split(",")]
    print("Now parsing:", states[0], states[1])
    game.append(states)
    doras, uras = lines.pop(0).split(".")
    doras = [tile_to_num(d) for d in doras.split(",")]
    uras = [tile_to_num(u) for u in uras.split(",")] if uras != "" else []
    game.append(doras)
    game.append(uras)
    haipai = parse_tiles(lines.pop(0))
    game.append(haipai)

    nagashi = ""
    zumo = []
    kiru = []
    while True:
        
        l = lines.pop(0)
        print(l)
        if "/" in l:
            l1, l2 = l.split("/")
            zumo.append(parse_all(l1))
            if l2 != "a": kiru.append(parse_all(l2))
        else:
            game.append(zumo)
            game.append(kiru)
            nagashi = l
            break 

    result = []
    r, player = parse_nagashi(nagashi)
    result.append(r)
    result.append(player)
    if(r == "和了"):
        l = lines.pop(0)
        hafu, yakus = parse_yaku(l)
        result.append(hafu)
        result.append(yakus)
    game.append(result)

    all_games.append(game)
    game = []

    while len(lines) > 0 and len(lines[0]) == 0:
        lines.pop(0)
        pass

data["log"] = all_games

print("Writing to file: " + output_file + " ... (4 / 4)")

with codecs.open(output_file, 'w', 'utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
