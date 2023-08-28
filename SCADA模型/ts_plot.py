# -*- coding: utf-8 -*-
"""
Created on 2023/5/11 14:22

@author: Wang Chenxu
"""

'''
功能: 
输入: 
输出: 
'''

import pandas as pd
import os
import matplotlib.pyplot as plt


#画图参数
def setpic(xname,yname): #美化图片，改变图片字号
    #plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fontdict1={'size':18}
    fontdict2={'size':16}
    plt.legend(prop=fontdict2)#,loc='upper right'
    plt.ylabel(yname,fontdict1)
    plt.xlabel(xname,fontdict1)
    plt.tick_params(labelsize=14)
    plt.grid(linestyle='-.')
    plt.tight_layout()


def read_path(folder):
    lst = []
    for root, dirs, files in os.walk(folder):
        if len(files)==0:
            continue
        for f in files:
            if f.endswith(".csv"):
                path = root + os.path.sep + f
                lst.append(path)
    return lst



def dataProcess(pdir, result_dir):
    file_list = read_path(pdir)
    for file in file_list:
        data = pd.read_csv(file, index_col=0)
        wtid = file.split('\\')[-1].split('.')[0].split('_')[0]

        data['time'] = pd.to_datetime(data['time'])
        data.sort_values('time', inplace=True)
        data.reset_index(drop=True, inplace=True)

        plt.figure(figsize=(18, 8), dpi=120)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(data['time'], data['CI_PitchPositionA3_mean'], 'o', label='桨距角3', alpha=0.8)
        plt.plot(data['time'], data['CI_PitchPositionA1_mean'], 'o', label='桨距角1', alpha=0.8)
        plt.plot(data['time'], data['CI_PitchPositionA2_mean'], 'o', label='桨距角2', alpha=0.8)
        #plt.ylim(-0.1, 1.2)
        plt.title(wtid + ' 桨距角变化时序图', fontsize=20)
        plt.legend()
        setpic('时间', '桨距角[deg]')

        plt.tight_layout()
        # plt.show()
        plt.savefig(result_dir + str(wtid) + '#_blade_ts.png')
        plt.close()

        plt.figure(figsize=(18, 8), dpi=120)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(data['time'], data['CI_RotorSpeed_mean'], label='叶轮转速1', alpha=0.8)
        plt.plot(data['time'], data['CI_RotorSpeed2_mean'], label='叶轮转速2', alpha=0.8)
        #plt.ylim(-0.1, 1.2)
        plt.title(wtid + ' 叶轮转速变化时序图', fontsize=20)
        plt.legend()
        setpic('时间', '叶轮转速')

        plt.tight_layout()
        # plt.show()
        plt.savefig(result_dir + str(wtid) + '#_rotor_speed_ts.png')
        plt.close()

        plt.figure(figsize=(18, 8), dpi=120)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(data['time'], data['CI_WindSpeed1_mean'], label='风速1', alpha=0.8)
        plt.plot(data['time'], data['CI_WindSpeed1_mean'], label='风速2', alpha=0.8)
        #plt.ylim(-0.1, 1.2)
        plt.title(wtid + ' 风速变化时序图', fontsize=20)
        plt.legend()
        setpic('时间', '风速[m/s]')

        plt.tight_layout()
        # plt.show()
        plt.savefig(result_dir + str(wtid) + '#_wind_speed_ts.png')
        plt.close()



if __name__ == '__main__':
    pdir = r'E:\08-娑婆风电场\计算结果\合并10分钟数据\\'
    result_dir = r'E:\08-娑婆风电场\计算结果\SCADA结果\多变量时序图\\'
    dataProcess(pdir, result_dir)



