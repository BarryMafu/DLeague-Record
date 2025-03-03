import codecs
import json
import dicts
import mahjong_pool as mp

def convert(SID : int, GID : int, players = ["gy", "wk", "tb", "cc"]):
    folder_name = f"Split Records/S{SID}_G{GID}/"
    for player_idx, player_name in enumerate(players):
        file_name = folder_name + f"S{SID}_G{GID}_" + player_name
        jfile_name = folder_name + f"J_S{SID}_G{GID}_" + player_name

        input_file = file_name + ".tex"
        output_file = jfile_name + ".json"

        lines = []
        idxs = []
        current_idx = -1

        try:

            print(f"[{1 + 4 * player_idx : 02d}/{4 * len(players)}] 正在读取并解析文件: " + input_file + " ...")

            with codecs.open(input_file, 'r', 'utf-8') as file:
                for idx, line in enumerate(file):
                    line = line.strip()
                    line = line.replace(' ', '')

                    if len(line)>0 and line[0] == "%": continue

                    if "%" in line:
                        line = line[:line.index("%")]

                    line = line.lower()
                    lines.append(line)
                    idxs.append(idx)

            data = {}

            print(f"[{2 + 4 * player_idx : 02d}/{4 * len(players)}] 正在解析头部 ...")

            def pop_idxs():
                nonlocal current_idx
                if len(idxs) == 0: return
                current_idx = idxs.pop(0)

            position_dict = {
                "e": 0,
                "s": 1,
                "w": 2,
                "n": 3
            }

            pop_idxs()
            season_id, game_id = lines.pop(0).split(",")
            pop_idxs()
            start_position = position_dict[lines.pop(0)]
            pop_idxs()
            player_name = lines.pop(0)
            data["title"] = "DLeague S" + season_id + " G" + game_id
            data["start_position"] = start_position
            data["name"] = player_name

            print(f"[{3 + 4 * player_idx : 02d}/{4 * len(players)}] 正在解析动作 ...")

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
                    elif c in "mspz":
                        if c == "z":
                            for t in temp:
                                if t not in "1234567": raise ValueError(f"无效麻将牌表示: {tiles}")
                        l.extend([t + c for t in temp])
                        temp = []
                    else:
                        raise ValueError(f"无效麻将牌表示: {tiles}")
                return [tile_to_num(t) for t in l]

            all_games = []
            game = []

            is_reach = False 

            def parse_all(tile, tehai, hiki : bool):
                # print(tehai.)
                if tile == "": return 60
                if is_tile(tile): 
                    tehai.draw_or_cut(tile_to_num(tile), hiki)
                    return tile_to_num(tile)
                if tile[0] in "c":
                    tile = tile[1:]
                    index_left = tile.index("[")
                    index_right = tile.index("]")
                    tile_chi = tile[index_left + 1: index_right]
                    tile = tile[:index_left] + tile[index_right + 1:]
                    string_chi = str(tile_to_num(tile_chi))
                    string_else = "".join([str(t) for t in parse_tiles(tile)])
                    tehai.remove_from_pool(tile_to_num(tile_chi), hint="吃牌时")
                    tehai.cuts(parse_tiles(tile))
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
                    if tile[0] != "k":
                        tehai.cuts(parse_tiles(tile_move_left))
                        tehai.cuts(parse_tiles(tile_move_right))
                    if tile[0] == "p":
                        tehai.remove_from_pool(tile_to_num(tile_move), hint="碰牌时")
                    elif tile[0] == "a":
                        tehai.cut(tile_to_num(tile_move))
                    elif tile[0] == "m":
                        tehai.remove_from_pool(tile_to_num(tile_move), hint="明杠时")
                    elif tile[0] == "k":
                        tehai.cut(tile_to_num(tile_move))
                    return string_left + tile[0] + string_move + string_right
                if tile[0] in "r":
                    nonlocal is_reach
                    is_reach = True
                    return "r" + str(parse_all(tile[1:], tehai, hiki))
                if tile[0] in "f":
                    return "r" + str(parse_all(tile[1:], tehai, hiki))
                raise ValueError(f"无效麻将牌或动作表示: {tile}")
                

            def parse_nagashi(nagashi):
                if "<" in nagashi:
                    return "流局", [nagashi.replace("<", "").split(",")]
                if ">" in nagashi:
                    houjuu_mono, agari_mono = nagashi.split(">")
                    return "和了", [agari_mono, houjuu_mono]
                else:
                    raise ValueError(f"点棒流动方向未知: {nagashi}")

            def parse_yaku(l):
                yaku, fu = l.split("#")
                yaku = yaku.split(";")
                yaku = [y for y in yaku if y != ""]
                fu = int(fu)
                if fu not in [20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110]:
                    raise ValueError(f"不合理的符数：{fu}")
                han = sum([dicts.calc_hansu(y) for y in yaku])
                yaku_dict = dicts.yaku_dict
                yakus = []
                for y in yaku:
                    if isinstance(yaku_dict[y], list):
                        yakus.extend(yaku_dict[y])
                    else:
                        yakus.append(yaku_dict[y])

                yakus = sorted(yakus)

                return [han, fu], yakus
                

            while True:
                if len(lines) == 0: break
                pop_idxs()
                states = [int(x) for x in lines.pop(0).split(",")]
                # print("Now parsing:", states[0], states[1])
                game.append(states)
                pop_idxs()
                doraura = lines.pop(0)
                if "." not in doraura:
                    raise ValueError("未检测到宝牌分隔符")
                doras, uras = doraura.split(".")
                doras = parse_tiles(doras)
                uras = parse_tiles(uras)
                game.append(doras)
                game.append(uras)
                pop_idxs()
                haipai = parse_tiles(lines.pop(0))
                tehai = mp.Tehai(haipai)
                game.append(haipai)

                nagashi = ""
                zumo = []
                kiru = []
                while True:
                    pop_idxs()
                    l = lines.pop(0)
                    # print(l)
                    if "/" in l:
                        l1, l2 = l.split("/")
                        zumo.append(parse_all(l1, tehai, True))
                        if l2 != "a": kiru.append(parse_all(l2,tehai, False))
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
                    pop_idxs()
                    l = lines.pop(0)
                    hafu, yakus = parse_yaku(l)
                    result.append(hafu)
                    result.append(yakus)
                game.append(result)

                game.append(is_reach) # if_isreach
                is_reach = False

                all_games.append(game)
                game = []

                while len(lines) > 0 and len(lines[0]) == 0:
                    pop_idxs()
                    lines.pop(0)
                    pass

            data["log"] = all_games

            print(f"[{4 + 4 * player_idx : 02d}/{4 * len(players)}] 正在写入输出.json文件: " + output_file + " ...")

            with codecs.open(output_file, 'w', 'utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            from colorama import Fore
            print(Fore.RED + "---------错误---------" + Fore.RESET)
            print(f"发生错误，文件： {input_file}")
            print("输入行 " + Fore.RED + f"{current_idx + 1} " + Fore.RESET + "中包含错误：")
            print(e)
            print(Fore.RED + "----------------------" + Fore.RESET)
            exit(1)


    print("[Complete] 所有文件已成功转换")

if __name__ == "__main__":
    sid, gid = input("请输入 SID 和 GID （中间用空格隔开）").split(" ")
    name = input("请输入需要解析的名字（中间用空格隔开）").split(" ")
    print(f"请确认文件是否在目录 /Split Records/S{sid}_G{gid} 下并且以 .tex 为后缀。")
    yn = input("是否开始解析？ [y/n]")
    if(yn == "y"):
        convert(sid, gid, name)

