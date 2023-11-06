# ====================
# 簡易将棋
# ====================

# パッケージのインポート
import random
import math
from tkinter import *
from tkinter import ttk

# ゲームの状態
class State:
    # 初期化
    def __init__(self, pieces=None, enemy_pieces=None, depth=0):
        # 方向定数
        self.dxy = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
                    (0, -2), (2, -2), (2, 0), (2, 2), (0, 2), (-2, 2), (-2, 0), (-2, -2),
                    (0, -3), (3, -3), (3, 0), (3, 3), (3, 3), (-3, 3), (-3, 0), (-3, -3),
                    (0, -4), (4, -4), (4, 0), (4, 4), (0, 4), (-4, 4), (-4, 0), (-4, -4))

        # 駒の配置
        self.pieces = pieces if pieces != None else [0] * (25 + 5)
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * (25 + 5)
        self.depth = depth

        # 駒ID
        # 0:なし, 1:歩兵, 2,角行, 3:飛車, 4:銀将, 5:金将, 6:と金, 7:龍馬, 8:龍王, 9:成銀, 10:王将
        # 持ち駒
        # 11:歩兵, 12:角行, 13:飛車, 14:銀将, 15:金将

        # 駒の初期配置
        if pieces == None or enemy_pieces == None:
            self.pieces = [0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0,
                           1, 0, 0, 0, 0,
                           10, 5, 4, 2, 3,
                           0, 0, 0, 0, 0]
            self.enemy_pieces = [0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0,
                                 1, 0, 0, 0, 0,
                                 10, 5, 4, 2, 3,
                                 0, 0, 0, 0, 0]


    # 負けかどうか
    def is_lose(self):
        for i in range(25):
            if self.pieces[i] == 10:  # 王将存在
                return False
        return True


    # 引き分けかどうか
    def is_draw(self):
        return self.depth >= 300  # 300手


    # ゲーム終了かどうか
    def is_done(self):
        return self.is_lose() or self.is_draw()


    # ゲーム結果
    def result_game(self):
        if self.is_lose() == True:
            return -1
        elif self.is_draw() == True:
            return 0
        else:
            return 1


    # デュアルネットワークの入力の2次元配列の取得
    def pieces_array(self):
        # プレイヤー毎のデュアルネットワークの入力の2次元配列の取得
        def pieces_array_of(pieces):
            table_list = []
            # 0:歩兵, 1:角行, 2:飛車, 3:銀将, 4:金将, 5:と金, 6:龍馬, 7:龍王, 8:成銀, 9:王将
            for j in range(1, 11):
                table = [0] * 25
                table_list.append(table)
                for i in range(25):
                    if pieces[i] == j:
                        table[i] = 1

            # 持ち駒
            # 10:歩兵, 11:角行, 12:飛車, 13:銀将, 14:金将
            for j in range(1, 6):
                flag = 1 if pieces[24 + j] > 0 else 0
                table = [flag] * 25
                table_list.append(table)
            return table_list

        # デュアルネットワークの入力の2次元配列の取得
        return [pieces_array_of(self.pieces), pieces_array_of(self.enemy_pieces)]


    # 駒の移動先と移動元を行動に変換
    def position_to_action(self, position, direction):
        return position * 37 + direction


    # 行動を駒の移動先と移動元に変換
    def action_to_position(self, action):
        return (int(action / 37), action % 37)


    # 合法手のリストの取得
    def legal_actions(self):
        actions = []
        for p in range(25):
            # 駒の移動時
            if self.pieces[p] != 0:
                actions.extend(self.legal_actions_pos(p))

            # 持ち駒の配置時
            if self.pieces[p] == 0 and self.enemy_pieces[24 - p] == 0:
                for capture in range(1, 6):
                    if self.pieces[24 + capture] != 0:
                        if(capture == 1): # 歩だったら
                            if(p > 4): # いちばん奥ではない
                                t = p % 5
                                fu = 0
                                for i in range(0, 5):
                                    fu_p = t + 5 * i
                                    if(self.pieces[fu_p] == 1):
                                        fu += 1
                                if(fu == 0):
                                    actions.append(self.position_to_action(p, 31 + capture))

                        else:
                            actions.append(self.position_to_action(p, 31 + capture))
        return actions


    # 駒の移動時の合法手のリストの取得
    def legal_actions_pos(self, position_src):
        actions = []

        # 駒の移動可能な方向
        piece_type = self.pieces[position_src]
        #if piece_type > 4: piece_type - 1
        directions = []
        if piece_type == 1:  # 歩兵
            directions = [0]
        elif piece_type == 2:  # 角行
            directions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
        elif piece_type == 3:  # 飛車
            directions = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
        elif piece_type == 4:  # 銀将
            directions = [0, 1, 3, 5, 7]
        elif piece_type == 5:  # 金将
            directions = [0, 1, 2, 4, 6, 7]
        elif piece_type == 6: # と金
            directions = [0, 1, 2, 4, 6, 7]
        elif piece_type == 7: # 龍馬
            directions = [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
        elif piece_type == 8:  # 龍王
            directions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
        elif piece_type == 9:  # 成銀
            directions = [0, 1, 2, 4, 6, 7]
        elif piece_type == 10:  # 王将
            directions = [0, 1, 2, 3, 4, 5, 6, 7]

        # 合法手の取得
        f = [0, 0, 0, 0, 0, 0, 0, 0]
        for direction in directions:
            # 駒の移動元
            x = position_src % 5 + self.dxy[direction][0]
            y = int(position_src / 5) + self.dxy[direction][1]
            p = x + y * 5

            # 移動可能時は合法手として追加
            if 0 <= x and x <= 4 and 0 <= y and y <= 4:
                if self.pieces[p] == 0:
                    if f[direction % 8] == 0:
                        actions.append(self.position_to_action(p, direction))
                if self.pieces[p] != 0 or self.enemy_pieces[24 - p] != 0:
                    f[direction % 8] = 1
        return actions


    # 成る場合
    def become(self, root, position_dst, state):
        state.pieces[position_dst] += 5
        root.quit()
        root.destroy()


    # 成らない場合
    def not_become(self, root):
        root.quit()
        root.destroy()


    # 次の状態の取得
    def next(self, action, player=0):
        # 次の状態の作成
        state = State(self.pieces.copy(), self.enemy_pieces.copy(), self.depth + 1)

        # 行動を(移動先, 移動元)に変換
        position_dst, position_src = self.action_to_position(action)


        # 駒の移動
        if position_src < 32:
            # 駒の移動元
            x = position_dst % 5 - self.dxy[position_src][0]
            y = int(position_dst / 5) - self.dxy[position_src][1]
            position_src = x + y * 5

            # 駒の移動
            state.pieces[position_dst] = state.pieces[position_src]
            state.pieces[position_src] = 0

            # 相手の駒が存在する時は取る
            piece_type = state.enemy_pieces[24 - position_dst]
            if piece_type != 0:
                if piece_type != 10:  # 王将でなければ
                    pt = piece_type
                    if(pt > 5 and pt < 10): # 成っていたら戻す
                        pt -= 5
                    state.pieces[24 + pt] += 1  # 持ち駒+1
                state.enemy_pieces[24 - position_dst] = 0

            # 敵陣に入ったら成る
            if (int(position_dst / 5) == 0): # AIの場合
                if player == 0:
                    if (state.pieces[position_dst] >= 1 and state.pieces[position_dst] <= 3):
                        state.pieces[position_dst] += 5
                    elif (state.pieces[position_dst] == 4):
                        if random.randint(0, 1) == 0:
                            state.pieces[position_dst] += 5
                else: # 人間の場合
                    if state.pieces[position_dst] == 1:
                        state.pieces[position_dst] += 5
                    elif state.pieces[position_dst] >= 2 and state.pieces[position_dst] <= 4:
                        root = Tk()
                        root.title('')
                        # Frame as Widget Container
                        frame1 = ttk.Frame(
                            root,
                            padding=10)
                        frame1.grid()

                        # Label
                        label = ttk.Label(
                            frame1,
                            text='成りますか?',
                            width=20,
                            anchor=W,
                            padding=(20))
                        label.grid(row=0, column=1)

                        # ボタン
                        button1 = ttk.Button(
                            frame1,
                            text='はい',
                            command=lambda: self.become(root, position_dst, state))
                        button1.grid(row=1, column=0)

                        button2 = ttk.Button(
                            frame1,
                            text='いいえ',
                            command=lambda: self.not_become(root))
                        button2.grid(row=1, column=1)

                        root.mainloop()
        # 持ち駒の配置
        else:
            capture = position_src - 31
            state.pieces[position_dst] = capture
            state.pieces[24 + capture] -= 1  # 持ち駒-1

        # 駒の交代
        w = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = w
        """
        print(state)
        print()
        """
        return state


    # 先手かどうか
    def is_first_player(self):
        return self.depth % 2 == 0


    # 文字列表示
    def __str__(self):
        pieces0 = self.pieces if self.is_first_player() else self.enemy_pieces
        pieces1 = self.enemy_pieces if self.is_first_player() else self.pieces
        hzkr0 = ('', '歩', '角', '飛', '銀', '金', 'ト', '馬', '龍', '全', '王')
        hzkr1 = ('', 'ふ', 'か', 'ひ', 'ぎ', 'き', 'と', 'ま', 'り', 'ぜ', 'お')

        # 後手の持ち駒
        str = ' ['
        for i in range(25, 30):
            if pieces1[i] >= 2: str += ' ' + hzkr1[i - 24]
            if pieces1[i] >= 1: str += ' ' + hzkr1[i - 24]
        str += ' ]\n'

        # ボード
        for i in range(25):
            if pieces0[i] != 0:
                str += ' ' + hzkr0[pieces0[i]]
            elif pieces1[24 - i] != 0:
                str += ' ' + hzkr1[pieces1[24 - i]]
            else:
                str += ' ー'
            if i % 5 == 4:
                str += '\n'

        # 先手の持ち駒
        str += ' ['
        for i in range(25, 30):
            if pieces0[i] >= 2: str += ' ' + hzkr0[i - 24]
            if pieces0[i] >= 1: str += ' ' + hzkr0[i - 24]
        str += ' ]\n'
        return str


# ランダムで行動選択
def random_action(state):
    legal_actions = state.legal_actions()
    r = random.randint(0, len(legal_actions) - 1)
    return legal_actions[r]


# 動作確認
if __name__ == '__main__':
    # 状態の生成
    state = State()

    # ゲーム終了までのループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 次の状態の取得
        state = state.next(random_action(state))

        # 文字列表示
        print(state)
        print()
