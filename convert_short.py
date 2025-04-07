import dicts
import calculator

SID = 3
GID = 11

SIGN_RYUUKYOKU = 3879456
SIGN_AGARI     = 9817462

kyouku_to_name = [
    "东一局", "东二局", "东三局", "东四局",
    "南一局", "南二局", "南三局", "南四局",
]

def convert_short(sid, gid, create_json, create_template, verbose, start_point = 25000):
    with open(f"Short/S{sid}_G{gid}.short", "r") as file:
        lines = file.readlines()
    lines = [line.strip().replace(" ", "") for line in lines]  # Remove empty lines and strip whitespace 

    if verbose: print(f"- 正在解析第{sid}赛季第{gid}场比赛")

    line = lines.pop(0)
    players = line.split(",")
    scores = [start_point] * 4 
    op_list = [["S"] * 4]
    score_list = [scores.copy()]
    result_list = []
    name_to_playerid = {player: i for i, player in enumerate(players)}
    if verbose: print(f"- 参与游戏的玩家有: {players}")
    
    def parse_nagashi(nagashi):
        if "<" in nagashi:
            tenpai_mono = nagashi.replace("<", "").split(",")
            return SIGN_RYUUKYOKU, [sorted(tenpai_mono)]
        if ">" in nagashi:
            houjuu_mono, agari_mono = nagashi.split(">")
            return SIGN_AGARI, [agari_mono, houjuu_mono]
        else:
            raise ValueError(f"点棒流动方向未知: {nagashi}")
    
    if verbose: print(f"- 具体内容：")

    kyouku = 0; honba = 0; kyoutaku = 0    
    while True:
        oya = players[kyouku % 4] 
        to_next = True
        if kyouku == 8: break
        if len(lines) == 0: 
            raise ValueError("文件内容不足")
        if verbose: print(f"    + {kyouku_to_name[kyouku]} {honba}本场，场供{kyoutaku}根")
        current_op = [""] * 4
        reach_players = []
        while True:
            line = lines[0]
            if line.startswith("r") and not ">" in line and not "<" in line:
                reach_player = line[1:]
                lines.pop(0)
                if verbose: print(f"        * {reach_player} 立直")
                reach_players.append(reach_player)
                current_op[name_to_playerid[reach_player]] = "R"
                scores[name_to_playerid[reach_player]] -= 1000
                kyoutaku += 1
            else:
                break
        nagashi = lines.pop(0)
        sign, monos = parse_nagashi(nagashi)
        # monos = monos[0]
        # 流局 
        if sign == SIGN_RYUUKYOKU:
            monos = monos[0]
            if verbose: print(f"        $ 流局，听牌者：{monos}")
            if oya in monos: to_next = False
            for o in current_op: o += "N"
            if not(len(monos) == 4 or len(monos) == 0):
                for player in players:
                    if player in monos:
                        scores[name_to_playerid[player]] += 3000 // len(monos)
                    else:
                        scores[name_to_playerid[player]] -= 3000 // (4 - len(monos))
        # 和了
        if sign == SIGN_AGARI:
            result = lines.pop(0)
            yaku, fu = result.split("#")
            yaku = yaku.split(";")
            yaku = [y for y in yaku if y != ""]
            fu = int(fu)
            if fu not in [20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110]:
                raise ValueError(f"不合理的符数：{fu}")
            han = sum([dicts.calc_hansu(y) for y in yaku])
            A = monos[0]
            if A == oya: to_next = False

            for player in players:
                if player == A:
                    current_op[name_to_playerid[player]] += "A"
                elif player == monos[1]:
                    current_op[name_to_playerid[player]] += "F"
                else:
                    current_op[name_to_playerid[player]] += "N"

            if monos[1] != "":
                # 放铳 
                A, H = monos[0], monos[1] 
                _, p = calculator.to_point_ron(han, fu, oya == A)
                if verbose: print(f"        $ 放铳：{H} -> {A}；{han}番{fu}符 {p}")
                scores[name_to_playerid[A]] += p + 300 * honba + 1000 * kyoutaku
                scores[name_to_playerid[H]] -= p + 300 * honba 
            if monos[1] == "":
                # 自摸
                if oya == A:
                    _, p = calculator.to_point_zumo(han, fu, True)
                    if verbose: print(f"        $ 自摸：{A}；{han}番{fu}符 {p}ALL")
                    for player in players:
                        if player == A:
                            scores[name_to_playerid[player]] += 3 * p + 300 * honba + 1000 * kyoutaku
                        else:
                            scores[name_to_playerid[player]] -= p + 100 * honba
                else:
                    _, p_hima, p_oya = calculator.to_point_zumo(han, fu, False)
                    if verbose: print(f"        $ 自摸：{A}；{han}番{fu}符 {p_hima} / {p_oya}")
                    for player in players:
                        if player == A:
                            scores[name_to_playerid[player]] += 2 * p_hima + p_oya + 300 * honba + 1000 * kyoutaku
                        elif player == oya:
                            scores[name_to_playerid[player]] -= p_oya + 100 * honba
                        else:
                            scores[name_to_playerid[player]] -= p_hima + 100 * honba
            
            kyoutaku = 0
        
        if verbose:
            print(f"        $ 目前分数：")
            for i, player in enumerate(players):
                print(f"            * {player}: {scores[i]}")

        result = {
            "op": current_op,
            "scores": scores.copy(),
            "kyouku": kyouku,
            "honba": honba,
            "kyoutaku": kyoutaku,
            "reach": reach_players
        }
        result_list.append(result)

        if to_next:
            kyouku += 1
            honba = 0
        else:
            honba += 1

if __name__ == "__main__":
    convert_short(SID, GID, False, False, True)
    print("转换完成")