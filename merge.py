import calculator
import json
import codecs

folder_name = "Split Records/S2_G50/"
file_names = [folder_name + "S2_G50_" + s + ".json" for s in ["cc", "tb", "gy", "wk"]]
output_file = "Final/" + "S2_G50.json"

data = {}
raw_datas = []
for file_name in file_names:
    with codecs.open(file_name, 'r', 'utf-8') as file:
        raw_datas.append(json.load(file))

def agree(l : list, key : str):
    if l[0][key] == l[1][key] == l[2][key] == l[3][key]:
        return l[0][key]
    if l[0][key] == l[1][key] == l[2][key]:
        print("<Warning> Inconsistent " + key + " for " + l[3]["name"])
        return l[0][key]
    if l[0][key] == l[1][key] == l[3][key]:
        print("<Warning> Inconsistent " + key + " for " + l[2]["name"])
        return l[0][key]
    if l[0][key] == l[2][key] == l[3][key]:
        print("<Warning> Inconsistent " + key + " for " + l[1]["name"])
        return l[0][key]
    if l[1][key] == l[2][key] == l[3][key]:
        print("<Warning> Inconsistent " + key + " for " + l[0]["name"])
        return l[1][key]
    raise ValueError("Inconsistent " + key)

def agree2(l : list, hint):
    if l[0] == l[1] == l[2] == l[3]:
        return l[0]
    if l[0] == l[1] == l[2]:
        print("<Warning> Inconsistent " + hint + " for 4")
        return l[0]
    if l[0] == l[1] == l[3]:
        print("<Warning> Inconsistent " + hint + " for 3")
        return l[0]
    if l[0] == l[2] == l[3]:
        print("<Warning> Inconsistent " + hint + " for 2")
        return l[0]
    if l[1] == l[2] == l[3]:
        print("<Warning> Inconsistent " + hint + " for 1")
        return l[1]
    raise ValueError("Inconsistent " + hint)

data["title"] = [agree(raw_datas, "title"), ""]

name_to_idx = {}
for d in raw_datas:
    name_to_idx[d["name"]] = d["start_position"]

idx_to_name = [None] * 4
for k, v in name_to_idx.items():
    idx_to_name[v] = k

print("positions: ", name_to_idx)

data["name"] = idx_to_name
data["rule"] = {
    "disp": "DLeague Rules",
    "aka": 1
}

all_games = []
scores = [25000] * 4

for l1, l2, l3, l4 in zip(*[d["log"] for d in raw_datas]):
    game = []
    statistics = agree2([l1[0], l2[0], l3[0], l4[0]], "statistics")
    ba, hb, kt = statistics 
    print(f"b{ba} h{hb} k{kt}")

    game.append(statistics)
    game.append(scores)

    doras = agree2([l1[1], l2[1], l3[1], l4[1]], "doras")
    uras = agree2([l1[2], l2[2], l3[2], l4[2]], "uras")
    game.append(doras)
    game.append(uras)

    game.extend([l1[3], l1[4], l1[5]])
    game.extend([l2[3], l2[4], l2[5]])
    game.extend([l3[3], l3[4], l3[5]])
    game.extend([l4[3], l4[4], l4[5]])

    result = agree2([l1[6], l2[6], l3[6], l4[6]], "result")
    s = ""
    change = [0] * 4
    show = []
    if result[0] == "和了":
        h, f = result[2]
        agari_mono = name_to_idx[result[1][0]]
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
                show = [agari_mono, houju_mono, agari_mono]
                s, score = calculator.to_point_ron(h, f, False)
                change[agari_mono] = score + 300 * hb + 1000 * kt
                change[houju_mono] = -score - 300 * hb
        
        for i, c in enumerate(change):
            scores[i] += c
        
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

    all_games.append(game)

data["log"] = all_games


with codecs.open(output_file, 'w', 'utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

    
