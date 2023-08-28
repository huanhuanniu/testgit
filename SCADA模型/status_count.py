# -*- coding: utf-8 -*-
"""
Created on 2023/6/21 9:57

@author: Wang Chenxu
"""

'''
功能: 
输入: 
输出: 
'''

import pandas as pd
import os
import re
import copy
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')


# 画图参数
def setpic(xname, yname):  # 美化图片，改变图片字号
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fontdict1={'size':15}
    fontdict2={'size':15}
    plt.legend(prop=fontdict2)#,loc='upper right'
    plt.ylabel(yname,fontdict1)
    plt.xlabel(xname,fontdict1)
    plt.tick_params(labelsize=14)
    plt.grid(linestyle='-.')
    plt.tight_layout()


def count_freq(data, var):
    result = pd.DataFrame(data.groupby('wtid').agg({'ts_diff':'sum', 'status':'count'}))
    result.reset_index(inplace=True, drop=False)
    result.columns = ['wtid', 'duration', 'count']
    result['status'] = var

    return result


def status_count_plot(data):
    plot_data_starting = data[data['status'] == 'starting']
    plot_data_starting.reset_index(inplace=True, drop=True)
    plot_data_stop = data[data['status'] == 'stop']
    plot_data_stop.reset_index(inplace=True, drop=True)
    plot_data_standstill = data[data['status'] == 'standstill']
    plot_data_standstill.reset_index(inplace=True, drop=True)

    fig, axs = plt.subplots(3, 1, figsize=(25, 24))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 启机
    label_list_0 = plot_data_starting['wtid'].tolist()
    num_list_0 = plot_data_starting['duration_h'].tolist()
    x_0 = range(len(num_list_0))

    axs[0].bar(x=x_0, height=num_list_0, width=0.3, label="启机总时长")
    axs[0].set_xticks([index + 0.2 for index in x], label_list_0)

    for a, b in zip(x_0, plot_data_starting['duration_h']):
        axs[0].text(a, b + 0.1, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs[0].set_title('启机情况展示', fontsize=16)
    axs[0].set_ylabel('启机时长[h]', fontsize=14)
    axs[0].set_xlabel('机组编号', fontsize=14)

    axs_0_1 = axs[0].twinx()
    axs_0_1.plot(plot_data_starting['wtid'], plot_data_starting['count'], 'o-', c='r', label="启机总频次")
    for a, b in zip(plot_data_starting['wtid'], plot_data_starting['count']):
        plt.text(a, b + 80, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs_0_1.set_ylim(0, 5500)
    axs_0_1.legend()
    axs_0_1.set_ylabel('启机频次', fontsize=14)

    # 停机
    label_list_1 = plot_data_stop['wtid'].tolist()
    num_list_1 = plot_data_stop['duration_h'].tolist()
    x_1 = range(len(num_list_1))

    axs[1].bar(x=x_1, height=num_list_1, width=0.3, label="停机总时长")
    axs[1].set_xticks([index + 0.2 for index in x], label_list_1)

    for a, b in zip(x_1, plot_data_stop['duration_h']):
        axs[1].text(a, b + 0.1, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs[1].set_title('停机情况展示', fontsize=16)
    axs[1].set_ylabel('停机时长[h]', fontsize=14)
    axs[1].set_xlabel('机组编号', fontsize=14)

    axs_1_1 = axs[1].twinx()
    axs_1_1.plot(plot_data_stop['wtid'], plot_data_stop['count'], 'o-', c='r', label="停机总频次")
    for a, b in zip(plot_data_stop['wtid'], plot_data_stop['count']):
        plt.text(a, b + 80, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs_1_1.set_ylim(0, 5500)
    axs_1_1.legend()
    axs_1_1.set_ylabel('停机频次', fontsize=14)

    # 待机
    label_list_2 = plot_data_standstill['wtid'].tolist()
    num_list_2 =plot_data_standstill['duration_h'].tolist()
    x_2 = range(len(num_list_2))

    axs[2].bar(x=x_2, height=num_list_2, width=0.3, label="待机总时长")
    axs[2].set_xticks([index + 0.2 for index in x], label_list_2)

    for a, b in zip(x_2, plot_data_standstill['duration']):
        axs[2].text(a, b + 0.1, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs[2].set_title('待机情况展示', fontsize=16)
    axs[2].set_ylabel('待机时长[h]', fontsize=14)
    axs[2].set_xlabel('机组编号', fontsize=14)

    axs_2_1 = axs[2].twinx()
    axs_2_1.plot(plot_data_standstill['wtid'], plot_data_standstill['count'], 'o-', c='r', label="待机总频次")
    for a, b in zip(plot_data_standstill['wtid'], plot_data_standstill['count']):
        plt.text(a, b + 80, '%.0f' % b, ha='center', va='bottom', fontsize=14)
    axs_2_1.set_ylim(0, 5500)
    axs_2_1.legend()
    axs_2_1.set_ylabel('待机频次', fontsize=14)


def ts_ws_bin(data, status, wtid, wt_type, ts_step=5, ws_step=0.1):
    data['windbin'] = round(data['ws_mean'] / ws_step + 0.00000001) * ws_step
    data['tsbin'] = round(data['ts_diff'] / ts_step + 0.00000001) * ts_step
    data_plot = pd.DataFrame(data.groupby(['windbin', 'tsbin']).agg({'ts_end':'count'}))
    data_plot.reset_index(drop=False, inplace=True)
    data_plot.columns=['windbin', 'tsbin', 'count']

    plt.figure(figsize=(12, 8), dpi=80)
    sc=plt.scatter(data_plot['tsbin'], data_plot['windbin'], s=data_plot['count']*6, c=data_plot['count'],marker='o',cmap='Spectral_r')#x,y表示点的坐标，s为点大小的向量，当然s=20这样定义为统一大小，c为颜色深浅向量，cmap颜色设置，这里是数值越大颜色越浅
    plt.colorbar(sc)
    plt.title(wtid+ ' ' + wt_type+ ' ' + status + '状态风速-时长散点图', fontsize=18)
    setpic('时长[s]', '风速[m/s]')
    #plt.text(data_plot.tsbin.max()-160, data_plot.windbin.max()-3, '风速分仓步长为'+str(ws_step)+'\n 时长分仓步长为'+str(ts_step), fontsize=15)
    #plt.show()


def dataProcess(pdir, result_dir):
    df_count_freq = pd.DataFrame()
    for id in ids:
        wt_type = config_id.loc[config_id['机位号'] == id, '机型'].values[0]
        id_starting_df = pd.read_csv(pdir + id + '_starting.csv')
        id_stop_df = pd.read_csv(pdir + id + '_stop.csv')
        id_standstill_df = pd.read_csv(pdir + id + '_standstill.csv')

        id_starting_count = count_freq(id_starting_df, 'starting')
        df_count_freq = pd.concat([df_count_freq, id_starting_count])
        id_stop_count = count_freq(id_stop_df, 'stop')
        df_count_freq = pd.concat([df_count_freq, id_stop_count])
        id_standstill_count = count_freq(id_standstill_df, 'standstill')
        df_count_freq = pd.concat([df_count_freq, id_standstill_count])

        result_dir_starting = result_dir + 'starting/'
        if not os.path.exists(result_dir_starting):
            os.makedirs(result_dir_starting)
        ts_ws_bin(id_starting_df, status='启机', wtid=id, wt_type=wt_type, ts_step=5, ws_step=0.1)
        plt.savefig(result_dir_starting + id + '_starting_scatters.png')

        result_dir_standstill = result_dir + 'standstill/'
        if not os.path.exists(result_dir_standstill):
            os.makedirs(result_dir_standstill)
        ts_ws_bin(id_standstill_df, status='待机', wtid=id, wt_type=wt_type, ts_step=5, ws_step=0.1)
        plt.savefig(result_dir_standstill + id + '_standstill_scatters.png')

        result_dir_stop = result_dir + 'stop/'
        if not os.path.exists(result_dir_stop):
            os.makedirs(result_dir_stop)
        ts_ws_bin(id_stop_df, status='停机', wtid=id, wt_type=wt_type, ts_step=5, ws_step=0.1)
        plt.savefig(result_dir_stop + id + '_stop_scatters.png')




    df_count_freq.reset_index(inplace=True, drop=True)
    df_count_freq.to_csv(result_dir + 'start_stop_count.csv')
    df_count_freq['duration_h'] = df_count_freq['duration']/3600

    status_count_plot(df_count_freq)
    plt.savefig(result_dir + 'start_stop_count.png')
    plt.close()



if __name__ == '__main__':
    ids = [f"FJ{i:02}" for i in range(1, 34)]
    pdir = r'E:\08-娑婆风电场\05-计算结果\SCADA结果\启停机各机组汇总csv\\'
    result_dir = r'E:\08-娑婆风电场\05-计算结果\SCADA结果\启停机结果图\\'
    pdir_config = r'E:\08-娑婆风电场\config\\'
    config_id = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='机组号')
    dataProcess(pdir, result_dir)
data = pd.read_csv(r'E:\08-娑婆风电场\计算结果\SCADA结果\启停机统计\start_stop_count.csv')


