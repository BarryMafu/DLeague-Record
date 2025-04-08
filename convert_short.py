import dicts
import calculator
import json 
import codecs

SIGN_RYUUKYOKU = 3879456
SIGN_AGARI     = 9817462

kyouku_to_name = [
    "东一局", "东二局", "东三局", "东四局",
    "南一局", "南二局", "南三局", "南四局",
]

def convert_short(sid, gid, create_json, create_template, verbose, start_point = 25000):
    with open(f"Short/S{sid}_G{gid}.short", "r") as file:
        lines = file.readlines()
    lines = [line.strip().replace(" ", "").lower() for line in lines]  # Remove empty lines and strip whitespace 

    if verbose: print(f"- 正在解析第{sid}赛季第{gid}场比赛")

    line = lines.pop(0)
    players = line.split(",")
    scores = [start_point] * 4 
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
        end_lines = [nagashi.replace(">", " > ").replace("<", " < ")]
        # monos = monos[0]
        # 流局 
        if sign == SIGN_RYUUKYOKU:
            monos = monos[0]
            if verbose: print(f"        $ 流局，听牌者：{monos}")
            if oya in monos: to_next = False
            for i in range(len(current_op)): current_op[i] = "N"
            if not(len(monos) == 4 or len(monos) == 0):
                for player in players:
                    if player in monos:
                        scores[name_to_playerid[player]] += 3000 // len(monos)
                    else:
                        scores[name_to_playerid[player]] -= 3000 // (4 - len(monos))
        # 和了
        if sign == SIGN_AGARI:
            result = lines.pop(0)
            end_lines.append(result.replace(";", "; ").replace("#", " # "))
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
            "op": current_op.copy(),
            "scores": scores.copy(),
            "kyouku": kyouku,
            "honba": honba,
            "kyoutaku": kyoutaku,
            "reach": reach_players,
            "end": end_lines,
        }
        result_list.append(result)

        if to_next:
            kyouku += 1
            honba = 0
        else:
            honba += 1
    
    # 创建 scop
    if create_json:
        scop_json = []
        for j in range(4):
            person_data = {}
            person_data["SID"] = sid
            person_data["GID"] = gid 
            import time
            person_data["Time"] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
            person_data["PlayerId"] = dicts.name_to_hash[players[j]]
            person_data["Score"] = [start_point] + [r['scores'][j] for r in result_list]
            person_data["Operations"] = ["S"] + [r['op'][j] for r in result_list]
            scop_json.append(person_data)

        scop_json_file = f"Json/S{sid}_G{gid}.json"
        with codecs.open(scop_json_file, 'w', 'utf-8') as file:
            json.dump(scop_json, file, indent=0, ensure_ascii=False)
    
    # 创建 tex 模板
    if create_template:
        import os
        idx_to_wind = ['E', 'S', 'W', 'N']
        idx_to_wind_2 = ['East', 'South', 'West', 'North']
        for idx, player in enumerate(players):
            file_name = f"Split Records/S{sid}_G{gid}/S{sid}_G{gid}_{player}.tex"
            if not os.path.exists(file_name):
                lines = []
                lines.append(f"% ┌─────────────────────────")
                lines.append(f"% |  << DLeague Record >> ")
                lines.append(f"% |  ")
                lines.append(f"% | Generated by Short2Tex")
                lines.append(f"% | Player: {player}")
                lines.append(f"% | Season: {sid}")
                lines.append(f"% | Game: {gid}")
                lines.append(f"% | Copyright: Mizu Studio")
                lines.append(f"% └─────────────────────────")
                lines.append(f"%")
                lines.append(f"{sid}, {gid} % S{sid}G{gid}")
                lines.append(f"{idx_to_wind[idx]} %{idx_to_wind_2[idx]}")
                lines.append(f"{player}")
                for r in result_list:
                    lines.append(f"%")
                    lines.append(f"% ┌─────────────────────────┐")
                    lines.append(f"% |     {kyouku_to_name[r['kyouku']]}     {r['honba']}本场     |")
                    lines.append(f"% └─────────────────────────┘")
                    lines.append(f"{r['kyouku']}, {r['honba']}, {r['kyoutaku']}")
                    if player in r['reach']:
                        lines.append(f"% Reached")
                    else:
                        lines.append(f"% Not Reached")
                    lines.extend(r['end'])

                with open(file_name, "w", encoding='utf-8') as file:
                    file.write("\n".join(lines))





if __name__ == "__main__":
    sid = input("请输入SID：")
    gid = input("请输入GID：")
    create_json = input("是否创建scop文件？(y/n)：") == "y"
    create_template = input("是否创建tex模板？(y/n)：") == "y"
    verbose = input("是否详细输出？(y/n)：") == "y"
    convert_short(int(sid), int(gid), create_json, create_template, verbose)