# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート
from dual_network import dual_network
from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network

import os
import shutil
import datetime
import time

# デュアルネットワークの作成
dual_network()

for i in range(10):
    print('Train',i,'====================')
    # セルフプレイ部
    self_play()

    # パラメータ更新部
    train_network()

    # google Drive
    contents = datetime.datetime.now().strftime('%Y%m%d %H%M%S')
    shutil.copyfile("./model/best.h5", "/content/drive/MyDrive/Colab Notebooks/5_5_Shogi/best/" + contents + "best.h5")
    shutil.copyfile("./model/latest.h5", "/content/drive/MyDrive/Colab Notebooks/5_5_Shogi/latest/" + contents + "latest.h5")

    # 新パラメータ評価部
    evaluate_network()

    # google Drive
    contents = datetime.datetime.now().strftime('%Y%m%d %H%M%S')
    shutil.copyfile("./model/best.h5", "/content/drive/MyDrive/Colab Notebooks/5_5_Shogi/best/" + contents + "best.h5")
    shutil.copyfile("./model/latest.h5","/content/drive/MyDrive/Colab Notebooks/5_5_Shogi/latest/" + contents + "latest.h5")
