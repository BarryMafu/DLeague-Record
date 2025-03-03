import calculator
import json
import codecs
import dicts

def merge(SID, GID):
    folder_name = f"Split Records/S{SID}_G{GID}/"
    file_names = [folder_name + f"J_S{SID}_G{GID}_" + s + ".json" for s in ["gy", "wk", "tb", "cc"]]
    output_file = "Final/" + f"S{SID}_G{GID}.json"

    data = {}
    raw_datas = [None] * 4
    for file_name in file_names:
        with codecs.open(file_name, 'r', 'utf-8') as file:
            d_temp = json.load(file)
            idx = d_temp["start_position"]
            raw_datas[idx] = d_temp

    def agree(l : list, key : str):
        if l[0][key] == l[1][key] == l[2][key] == l[3][key]:
            return l[0][key]
        if l[0][key] == l[1][key] == l[2][key]:
            print("<警告> 不一致的： " + key + "。 " + l[3]["name"] + "的声明与其他人不一致。")
            return l[0][key]
        if l[0][key] == l[1][key] == l[3][key]:
            print("<警告> 不一致的： " + key + "。 " + l[2]["name"] + "的声明与其他人不一致。")
            return l[0][key]
        if l[0][key] == l[2][key] == l[3][key]:
            print("<警告> 不一致的： " + key + "。 " + l[1]["name"] + "的声明与其他人不一致。")
            return l[0][key]
        if l[1][key] == l[2][key] == l[3][key]:
            print("<警告> 不一致的： " + key + "。 " + l[0]["name"] + "的声明与其他人不一致。")
            return l[1][key]
        raise ValueError("<错误> 不一致的： " + key + " 且无法解决。")

    def agree2(l : list, hint):
        if l[0] == l[1] == l[2] == l[3]:
            return l[0]
        if l[0] == l[1] == l[2]:
            print("<警告> 不一致的： " + hint + "。起家北家(3)声明被认为有误。")
            return l[0]
        if l[0] == l[1] == l[3]:
            print("<警告> 不一致的： " + hint + "。起家西家(2)声明被认为有误。")
            return l[0]
        if l[0] == l[2] == l[3]:
            print("<警告> 不一致的： " + hint + "。起家南家(1)声明被认为有误。")
            return l[0]
        if l[1] == l[2] == l[3]:
            print("<警告> 不一致的： " + hint + "。起家東家(0)声明被认为有误。")
            return l[1]
        raise ValueError("<错误> 不一致的： " + hint + " 且无法解决。")

    data["title"] = [agree(raw_datas, "title"), ""]

    name_to_idx = {}
    for d in raw_datas:
        name_to_idx[d["name"]] = d["start_position"]

    idx_to_name = [None] * 4
    for k, v in name_to_idx.items():
        idx_to_name[v] = k

    print("起家位置: ", name_to_idx)

    data["name"] = idx_to_name
    data["rule"] = {
        "disp": "DLeague Rules",
        "aka": 1
    }

    all_games = []
    scores = [25000] * 4

    score_table = [[25000] * 4]
    op_table = [["S"] * 4]

    for l1, l2, l3, l4 in zip(*[d["log"] for d in raw_datas]):
        game = []
        statistics = agree2([l1[0], l2[0], l3[0], l4[0]], "statistics")
        ba, hb, kt = statistics 
        print(f"解析到 场次 {ba}   本场 {hb}   供托 {kt}")

        game.append(statistics)
        score_copy = scores.copy()
        game.append(score_copy)

        doras = agree2([l1[1], l2[1], l3[1], l4[1]], "doras")
        uras = agree2([l1[2], l2[2], l3[2], l4[2]], "uras")
        game.append(doras)
        game.append(uras)

        game.extend([l1[3], l1[4], l1[5]])
        game.extend([l2[3], l2[4], l2[5]])
        game.extend([l3[3], l3[4], l3[5]])
        game.extend([l4[3], l4[4], l4[5]])

        kt += sum([l1[7], l2[7], l3[7], l4[7]])

        result = agree2([l1[6], l2[6], l3[6], l4[6]], "result")
        s = ""
        change = [0] * 4 

        ops = [""] * 4

        show = []
        if result[0] == "和了":
            h, f = result[2]
            agari_mono = name_to_idx[result[1][0]]
            ops[agari_mono] = "A"
            if (agari_mono - ba) % 4 == 0:
                # oya
                if result[1][1] == "":
                    #zimo-agari
                    show = [agari_mono] * 3
                    s, score = calculator.to_point_zumo(h, f, True)
                    change = [-score - 100 * hb] * 4
                    change[agari_mono] = 3 * score + 300 * hb + 1000 * kt
                else:
                    #ron-agari
                    houju_mono = name_to_idx[result[1][1]]
                    ops[houju_mono] = "F"
                    show = [agari_mono, houju_mono, agari_mono]
                    s, score = calculator.to_point_ron(h, f, True)
                    change[agari_mono] = score + 300 * hb + 1000 * kt
                    change[houju_mono] = -score - 300 * hb
            else:
                # hima
                if result[1][1] == "":
                    #zimo-agari
                    show = [agari_mono] * 3
                    s, score_hima, score_oya = calculator.to_point_zumo(h, f, False)
                    change = [-score_hima - 100 * hb] * 4
                    change[agari_mono] = 2 * score_hima + score_oya + 300 * hb + 1000 * kt
                    change[ba % 4] = -score_oya - 100 * hb
                else:
                    #ron-agari
                    houju_mono = name_to_idx[result[1][1]]
                    ops[houju_mono] = "F"
                    show = [agari_mono, houju_mono, agari_mono]
                    s, score = calculator.to_point_ron(h, f, False)
                    change[agari_mono] = score + 300 * hb + 1000 * kt
                    change[houju_mono] = -score - 300 * hb
            
            
            show.append(s)
            show.extend(result[3])
            game.append(["和了", change, show])
        else:
            #流局
            tenpai_list = []
            for name in result[1][0]:
                idx = name_to_idx[name]
                tenpai_list.append(idx)
            if len(tenpai_list) == 0:
                game.append(["全員不聴", [0, 0, 0, 0]])
            elif len(tenpai_list) == 1:
                change = [-1000] * 4
                change[tenpai_list[0]] = 3000
                game.append(["流局", change])
            elif len(tenpai_list) == 2:
                change = [-1500] * 4
                for idx in tenpai_list:
                    change[idx] = 1500
                game.append(["流局", change])
            elif len(tenpai_list) == 3:
                change = [-3000] * 4
                for idx in tenpai_list:
                    change[idx] = 1000
                game.append(["流局", change])
            else:
                game.append(["流局", [0, 0, 0, 0]])

        for i in range(4):
            if ops[i] == "": ops[i] = "N"

        if l1[7] == True: scores[0] -= 1000; ops[0] = "R" + ops[0]
        if l2[7] == True: scores[1] -= 1000; ops[1] = "R" + ops[1]
        if l3[7] == True: scores[2] -= 1000; ops[2] = "R" + ops[2]
        if l4[7] == True: scores[3] -= 1000; ops[3] = "R" + ops[3]

        for i, c in enumerate(change):
            scores[i] += c
        
        score_copy_2 = scores.copy()
        score_table.append(score_copy_2)
        op_table.append(ops)

        all_games.append(game)

    data["log"] = all_games

    print()
    from colorama import Fore
    mylist = []
    print(Fore.BLUE + "============ 分数表 与 操作表 ============" + Fore.RESET)
    for j in range(4):
        person_data = {}
        person_data["SID"] = SID
        person_data["GID"] = GID 
        import time
        person_data["Time"] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        person_data["PlayerId"] = dicts.name_to_hash[idx_to_name[j]]
        person_data["Score"] = [l[j] for l in score_table]
        person_data["Operations"] = [l[j] for l in op_table]
        mylist.append(person_data)

        print(Fore.LIGHTCYAN_EX + f"Player{j + 1} < {idx_to_name[j]} >" + Fore.RESET)
        print("Score: ", end="")
        print([l[j] for l in score_table])
        print("Operations: ", end="")
        print([l[j] for l in op_table])
        if j != 3: print()
    print(Fore.BLUE + "========================================" + Fore.RESET)

    json_file = f"Json/S{SID}_G{GID}.json"
    with codecs.open(json_file, 'w', 'utf-8') as file:
        json.dump(mylist, file, indent=0, ensure_ascii=False)

    print(f"分数和操作表已经写入 {json_file}")

    with codecs.open(output_file, 'w', 'utf-8') as file:
        json.dump(data, file, indent=0, ensure_ascii=False)

    
