import random
import pandas as pd

#讀取excel
def reels_excel(file_path):
    df = pd.read_excel(file_path)
    return [df[col].dropna().astype(str).tolist() for col in df.columns]

#黃金老鼠
def is_wild(sym):
    return sym in ['WW', 'W1', 'W2', 'W3']

#符號表
def symbol(sym):
    return sym in ['M1','M2','M3','M4','M5','M6','M7','M8','M9','C1'] or is_wild(sym)

#base game盤面 3*5
def spin_base(base_reels):
    grid = []
    for reel in base_reels:
        start = random.randint(0, len(reel) - 1)
        symbols = [reel[(start+i) % len(reel)] for i in range(3)]
        grid.append(symbols)
    return [[grid[c][r] for c in range(len(base_reels))] for r in range(3)]

#free game盤面 4*5
def spin_free(free_reels):
    grid = []
    for reel in free_reels:
        start = random.randint(0, len(reel) - 1)
        symbols = [reel[(start+i) % len(reel)] for i in range(4)]
        grid.append(symbols)
    return [[grid[c][r] for c in range(len(free_reels))] for r in range(4)]

#free game low盤面 4*5
def spin_free_low(free_reels_low):
    grid = []
    for reel in free_reels_low:
        start = random.randint(0, len(reel) - 1)
        symbols = [reel[(start+i) % len(reel)] for i in range(4)]
        grid.append(symbols)
    return [[grid[c][r] for c in range(len(free_reels_low))] for r in range(4)]
    
# 算盤面
def calc_base(grid, pay_table):
    total_win = 0
    hit_detail = []
    score_combo = 0      
    cols = len(grid[0])

    for target, payoff in pay_table.items():
        ways = []
        for c in range(cols):
            cnt = 0
            for r in range(len(grid)):
                cell = grid[r][c]
                if cell == target or (is_wild(cell) and target != 'C1'):
                    cnt += 1
            ways.append(cnt)
        for n in (5, 4, 3):
            if all(w > 0 for w in ways[:n]):
                combo = 1
                for w in ways[:n]:
                    combo *= w
                score = payoff[n - 1] * combo
                if score > 0:
                    total_win += score
                    hit_detail.append((target, n, combo, score))
                    score_combo += 1
                break
    return total_win, hit_detail, score_combo   

#刪除已得分組合
def del_combos(grid, hit_detail):
    rows, cols = len(grid), len(grid[0])
    to_clear = [[False]*cols for _ in range(rows)]
    for target, n, combo, score in hit_detail:
        for c in range(n):
            for r in range(rows):
                cell = grid[r][c] 
                if cell == target or (is_wild(cell) and target != 'C1'):
                    to_clear[r][c] = True
    for r in range(rows):
        for c in range(cols):
            if to_clear[r][c]:
                grid[r][c] = None
    return grid

#掉落表
def fill_score_combo(grid, table, total_combos):
    rows, cols = len(grid), len(grid[0])
    #轉換原始盤面
    for c in range(cols):
        for r in range(rows):
            sym = grid[r][c]
            if c >= 1:
                if total_combos >= 10 and sym == 'M1':
                    grid[r][c] = 'W1'
                elif total_combos >= 5 and sym == 'M2':
                    grid[r][c] = 'W2'
                elif total_combos >= 2 and sym == 'M3':
                    grid[r][c] = 'W3'
        #排到底下
        exist = [grid[r][c] for r in range(rows) if grid[r][c] is not None]
        empty_cnt = rows - len(exist)
        
        has_scatter = 'C1' in exist
        
        #設定掉落表機率
        bag = []
        for sym, counts in table.items():
            w = counts[c]
            if w <= 0:
                continue

            if c == 0 and sym.startswith('W'):
                continue
            
            if has_scatter and sym == 'C1':
                continue
            bag += [sym] * w
        #有放回的抽
        top = [random.choice(bag) for _ in range(empty_cnt)] if bag else []

        #處理重複c1
        c1_pos = [i for i,s in enumerate(top) if s == 'C1']
        if len(c1_pos) > 1:
            non_c1_bag = [x for x in bag if x != 'C1']
            for idx in c1_pos[1:]:
                top[idx] = random.choice(non_c1_bag) if non_c1_bag else None
                
        #變黃金老鼠
        for i, sym in enumerate(top):
            if c >= 1:
                if total_combos >= 10 and sym == 'M1':
                    top[i] = 'W1'
                elif total_combos >= 5 and sym == 'M2':
                    top[i] = 'W2'
                elif total_combos >= 2 and sym == 'M3':
                    top[i] = 'W3'

        new_col = top + exist
        for r in range(rows):
            grid[r][c] = new_col[r] if r < len(new_col) else None

    return grid

#進去free game
def enter_free(grid, row_limit, reward_table, scatter='C1'):
    count = sum(
        1
        for r in range(row_limit)
        for c in range(5)
        if grid[r][c] == scatter
    )
    if count < 3:
        return False, 0
    return True, reward_table.get(count, reward_table[5])

#讀取excel
base_reels = reels_excel('boom_base_reels.xlsx')
free_reels = reels_excel('boom_free_reels.xlsx')
free_reels_low = reels_excel('boom_free_low_reels.xlsx')

#賠分表
pay_table = {
    'M1':[0,0,100,300,1000], 'M2':[0,0,50,150,500],
    'M3':[0,0,50,100,300], 'M4':[0,0,20,40,100],
    'M5':[0,0,20,40,100], 'M6':[0,0,20,40,100],
    'M7':[0,0,10,20,50], 'M8':[0,0,10,20,50],
    'M9':[0,0,10,20,50]
}

#base game
combo1 = {
    'WW': [0,10,9,13,12],
    'C1': [1,1,2,2,3],
    'M1': [0,1,1,1,3],
    'M2': [1,2,2,2,3],
    'M3': [3,6,6,6,12],
    'M4': [26,2,3,14,12],
    'M5': [3,27,5,14,12],
    'M6': [3,5,22,14,12],
    'M7': [3,20,10,6,6],
    'M8': [22,2,10,6,6],
    'M9': [3,6,12,6,6],
    'W1': [0,0,0,0,0],
    'W2': [0,0,0,0,0],
    'W3': [0,0,0,0,0]
    } 
combo24 = {
    'WW': [0,6,6,9,10],
    'C1': [1,1,2,2,3],
    'M1': [0,1,1,1,3],
    'M2': [3,6,6,7,8],
    'M3': [2,0,0,0,0],
    'M4': [12,10,10,13,10],
    'M5': [12,14,14,12,13],
    'M6': [12,14,14,12,13],
    'M7': [6,6,6,5,6],
    'M8': [6,6,6,4,5],
    'M9': [6,6,6,4,5],
    'W1': [0,0,0,0,0],
    'W2': [0,0,0,0,0],
    'W3': [0,18,19,10,15]
    }
combo59 = {
    'WW': [0,2,2,2,2],
    'C1': [1,1,2,2,3],
    'M1': [0,4,4,2,3],
    'M2': [2,0,0,0,0],
    'M3': [2,0,0,0,0],
    'M4': [10,1,1,4,2],
    'M5': [2,5,1,3,3],
    'M6': [2,1,6,3,3],
    'M7': [4,2,2,4,2],
    'M8': [1,6,2,2,2],
    'M9': [1,2,6,2,2],
    'W1': [0,0,0,0,0],
    'W2': [0,8,7,5,5],
    'W3': [0,10,9,6,6]
    }
combo10 = {
    'WW': [0,15,15,2,1],
    'C1': [10,10,20,2,3],
    'M1': [20,0,0,0,0],
    'M2': [30,0,0,0,0],
    'M3': [40,0,0,0,0],
    'M4': [1,10,10,6,6],
    'M5': [1,10,10,6,6],
    'M6': [1,10,10,7,6],
    'M7': [89,85,85,1,1],
    'M8': [89,85,85,1,1],
    'M9': [89,85,85,1,1],
    'W1': [0,30,30,1,1],
    'W2': [0,40,40,1,2],
    'W3': [0,50,50,2,2]
    }
combo11 = {
    'WW': [0,0,0,0,0],
    'C1': [3,2,2,2,3],
    'M1': [2,0,0,0,0],
    'M2': [3,0,0,0,0],
    'M3': [4,0,0,0,0],
    'M4': [22,1,0,1,4],
    'M5': [0,33,1,1,4],
    'M6': [1,0,28,1,4],
    'M7': [23,1,0,4,1],
    'M8': [0,34,1,4,1],
    'M9': [1,0,30,4,1],
    'W1': [0,0,0,1,1],
    'W2': [0,0,0,1,1],
    'W3': [0,0,0,1,1]
    }
"""
combo1 = {
    'WW': [ 0,  0,  0,  0,  0],
    'C1': [ 5,  5,  5,  5,  5],
    'M1': [ 0,  0,  0,  0,  0],
    'M2': [ 0,  0,  0,  0,  0],
    'M3': [ 0,  0,  0,  0,  0],
    'M4': [ 0,  0,  0,  0,  0],
    'M5': [ 0,  0,  0,  0,  0],
    'M6': [ 0,  0,  0,  0,  0],
    'M7': [ 0,  0,  0,  0,  0],
    'M8': [ 0,  0,  0,  0,  0],
    'M9': [ 0,  0,  0,  0,  0],
    'W1': [ 0,  0,  0,  0,  0],
    'W2': [ 0,  0,  0,  0,  0],
    'W3': [ 0,  0,  0,  0,  0],
    }
combo24 = {
    'WW': [ 0,  0,  0,  0,  0],
    'C1': [ 0,  0,  0,  0,  0],
    'M1': [ 0,  0,  0,  0,  0],
    'M2': [ 10,  10,  10,  10,  10],
    'M3': [ 0,  0,  0,  0,  0],
    'M4': [ 0,  0,  0,  0,  0],
    'M5': [ 10,  0,  0,  0,  0],
    'M6': [ 0,  0,  0,  0,  0],
    'M7': [ 0,  0,  0,  0,  0],
    'M8': [ 0,  0,  0,  0,  0],
    'M9': [ 0,  0,  0,  0,  0],
    'W1': [ 0,  0,  0,  0,  0],
    'W2': [ 0,  0,  0,  0,  0],
    'W3': [ 0,  0,  0,  0,  0],
    }
"""


#free game
free_combo1 = {
    'WW': [0,48,48,14,0],
    'C1': [0,0,0,1,1],
    'M1': [3,3,3,4,3],
    'M2': [18,8,8,10,12],
    'M3': [25,15,15,36,60],
    'M4': [34,30,26,0,110],
    'M5': [27,21,24,10,110],
    'M6': [26,24,23,10,110],
    'M7': [11,17,10,132,10],
    'M8': [16,11,17,122,10],
    'M9': [17,14,16,122,10],
    'W1': [0,0,0,0,0],
    'W2': [0,0,0,0,0],
    'W3': [0,0,0,0,0]
    } 
free_combo24 = {
    'WW': [0,20,20,1,1],
    'C1': [0,0,0,1,1],
    'M1': [0,1,1,1,0],
    'M2': [4,4,10,4,5],
    'M3': [26,0,0,0, 0],
    'M4': [10,20,25,1,54],
    'M5': [30,18,25,1,54],
    'M6': [25,20,20,1,54],
    'M7': [48,33,40,59,6],
    'M8': [30,30,40,59,6],
    'M9': [30,33,34,59,6],
    'W1': [ 0,0,0,0,0],
    'W2': [ 0,0,0,0,0],
    'W3': [ 0,40,40,5,0],
    } 
free_combo59 = {
    'WW': [0,2, 2,1, 0],
    'C1': [1,1,1,2,2],
    'M1': [2,3,0,4,0],
    'M2': [3,0,0,0,0],
    'M3': [8,0,0,0,0],
    'M4': [22,1,2,1,17],
    'M5': [1,19,2,1,17],
    'M6': [1,1,35,1,17],
    'M7': [24,2,1,17,1],
    'M8': [4,14,1,17,1],
    'M9': [4,2,35,17,1],
    'W1': [0,0,0,0,0],
    'W2': [0,7,9,1,1],
    'W3': [0,11,8,1,0]
    } 
free_combo10 = {
    'WW': [0,2,2,1,0],
    'C1': [1,1,1,1,1],
    'M1': [2,0,0,0,0],
    'M2': [3,0,0,0,0],
    'M3': [2,0,0,0,0],
    'M4': [0,8,6,1,0],
    'M5': [23,0,7,1,4],
    'M6': [24,5,0,1,6],
    'M7': [0,7,7,12,8],
    'M8': [29,0,7,12,8],
    'M9': [29,7,0,12,8],
    'W1': [0,7,6,4,0],
    'W2': [0,7,6,2,0],
    'W3': [0,5,5,2,0]
    } 
free_combo11 = {
    'WW': [0,0,0,0,0],
    'C1': [3,1,2,2,3],
    'M1': [2,0,0,0,0],
    'M2': [3,0,0,0,0],
    'M3': [4,0,0,0,0],
    'M4': [23,1,0,15,15],
    'M5': [0,27,1,19,15],
    'M6': [1,0,26,1,5],
    'M7': [29,1,0,19,15],
    'M8': [0,35,1,20,20],
    'M9': [1,0,35,1,5],
    'W1': [0,0,0,1,1],
    'W2': [0,0,0,1,1],
    'W3': [0,0,0,1,1]
    } 

#base_table
combo_list = (
    [None] +
    [combo1] +
    [combo24] * 3 +
    [combo59] * 5 +
    [combo10] +
    [combo11]
)

# free_table
free_list = (
    [None] +
    [free_combo1] +
    [free_combo24] * 3 +
    [free_combo59] * 5 +
    [free_combo10] +
    [free_combo11]
)

def get_drop_table(score_combo):
    idx = score_combo if score_combo < len(combo_list) else len(combo_list) - 1
    return combo_list[idx]

def get_free_table(free_combo_count):
    idx = free_combo_count if free_combo_count < len(free_list) else len(free_list) - 1
    return free_list[idx]


if __name__ == '__main__':
    
    #總得分
    full_base_score      = 0
    full_free_score      = 0
    #次數
    free_count           = 0
    base_win             = 0
    #scatter
    free_trigger_counts  = {3:0,4:0,5:0}
    free_score_by_trig   = {3:0,4:0,5:0}
    
    N = 1000000
    bet = 100
    max_spins = 50

    #re-tri
    total_retrigger_checks = 0
    retrigger_count = 0
    
    # 統計 Free Spin
    spin_total_counts   = [0] * max_spins
    spin_scoring_counts = [0] * max_spins
    
    base_spin_total  = 0
    base_spin_scored = 0
    base_score_on_hit   = 0

    for _ in range(N):
        # Base Game
        grid = spin_base(base_reels)
        base_spin_total += 1
        total_win = 0
        total_combos = 0
        while True:
            win, det, sc = calc_base(grid, pay_table)
            if not det: break
            total_win += win
            total_combos += 1
            grid = fill_score_combo(del_combos(grid, det), get_drop_table(total_combos), total_combos)

        if total_win > 0:
            base_spin_scored += 1
            base_score_on_hit += total_win
        full_base_score += total_win
        base_win += total_win


        # Free Game Trigger
        triggered, spins = enter_free(grid, 3, {3:10, 4:15, 5:20})
        if triggered:
            free_count += 1
            scat_ct = {10:3,15:4,20:5}[spins]
            free_trigger_counts[scat_ct] += 1
            spins_left = min(spins, max_spins)
            total_free_win = 0
            round_no = 0
            while spins_left > 0:
                round_no += 1
                spins_left -= 1
                # 統計
                spin_total_counts[round_no-1] += 1
                total_retrigger_checks += 1
                #設定高表次數
                fg = spin_free(free_reels) if round_no<=3 else spin_free_low(free_reels_low)
                spin_win = 0
                combo = 0
                while True:
                    w, d, sc2 = calc_base(fg, pay_table)
                    if not d: break
                    spin_win += w
                    total_free_win += w
                    combo += 1
                    fg = fill_score_combo(del_combos(fg, d), get_free_table(combo), combo)
                if spin_win>0:
                    spin_scoring_counts[round_no-1] += 1
                # retrigger
                rpt, ex = enter_free(fg, 4, {3:10, 4:15, 5:20})
                if rpt and spins_left + ex <= max_spins:
                    add = min(ex, max_spins - spins_left)
                    spins_left += add
                    total_free_win += 0 ###
                if rpt:
                    retrigger_count += 1
                
            full_free_score += total_free_win
            free_score_by_trig[scat_ct] += total_free_win

    # 原本輸出
    total_bet = N * bet
    base_rtp = (base_win / total_bet)*100
    free_rate = free_count / N
    avg_free_score = full_free_score / free_count if free_count else 0
    avg_free_rtp = avg_free_score / bet
    free_contrib = free_rate * avg_free_rtp * 100
    RTP = base_rtp + free_contrib
    retrigger_rate = retrigger_count / total_retrigger_checks

    print(f'free總得分： {full_free_score}')
    print(f'模擬局數: {N}')
    print(f'每局下注: {bet}')
    print(f'總下注額: {total_bet}')
    print(f'Base Game RTP: {base_rtp:.2f}')
    print(f"Free Game 觸發率：{free_rate:.4%}")
    print(f"Free Game RTP：{free_contrib:.2f}%")
    print(f"RTP：{RTP}")

    print("Scatter")
    for scatters, cnt in free_trigger_counts.items():
        rate = cnt / N * 100
        print(f"  {scatters}×C1 → {cnt} 次 ({rate:.4f}%)")

    print("=== 各 Scatter 觸發總／平均得分 ===")
    for k in (3,4,5):
        cnt = free_trigger_counts[k]
        tot = free_score_by_trig[k]
        print(f"  {k}×C1總得分：{tot}，pay back：{(tot/cnt)/100:.2f}")
        

    # 新增：Free Game 所有旋轉中有得分的比例
    total_spins  = sum(spin_total_counts)
    total_scored = sum(spin_scoring_counts)
    print(f"Free Game 旋轉有得分次數/總次數 = {total_scored}/{total_spins} = {total_scored/total_spins:.2%}")
    
    print(f"Free Game 中 re-trigger 檢查次數：{total_retrigger_checks}")
    print(f"實際 re-trigger 次數：{retrigger_count}")
    print(f"Re-trigger 機率：{retrigger_rate:.2%}")
    print(f"Base Game 機率: {base_spin_scored}/{base_spin_total} = {base_spin_scored/base_spin_total:.2%}")
    
    avg_score_per_hit = base_score_on_hit / base_spin_scored if base_spin_scored else 0
    print(f"Base Game 命中后平均得分: {avg_score_per_hit:.2f}")