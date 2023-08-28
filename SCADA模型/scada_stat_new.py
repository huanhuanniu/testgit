# *_*coding:utf-8 *_*
"""
Created on Mon Aug  5 12:15:29 2019

@author: wcx
"""


'''
功能: 
输入: 涉及数据为: 
输出: 
'''

import pandas as pd
import numpy as np
import os
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from matplotlib.pyplot import MultipleLocator
from scipy.interpolate import make_interp_spline
import warnings
warnings.filterwarnings('ignore')


def data_clean_wind(data):
    data['wind_diff'] = data['CI_WindSpeed1_mean'].diff()
    data['wind_diff_2'] = data['CI_WindSpeed1_mean'].diff(2)
    data['fixed_wind'] = (data['wind_diff'] == 0) & (data['wind_diff_2'] == 0)
    data = data[(data['fixed_wind'] == False) & (data['CI_WindSpeed1_mean'] > 0)]

    return data


def data_clean(data):
    #功率/1000
    # data['CI_IprRealPower_min'] = data['CI_IprRealPower_min'] / 1000
    # data['CI_IprRealPower_max'] = data['CI_IprRealPower_max'] / 1000
    # data['CI_IprRealPower_mean'] = data['CI_IprRealPower_mean'] / 1000
    # data['CI_IprRealPower_std'] = data['CI_IprRealPower_std'] / 1000
    #发电机转速/100
    data['CI_PcsMeasuredGeneratorSpeed_min'] = data['CI_PcsMeasuredGeneratorSpeed_min'] / 100
    data['CI_PcsMeasuredGeneratorSpeed_max'] = data['CI_PcsMeasuredGeneratorSpeed_max'] / 100
    data['CI_PcsMeasuredGeneratorSpeed_mean'] = data['CI_PcsMeasuredGeneratorSpeed_mean'] / 100
    data['CI_PcsMeasuredGeneratorSpeed_std'] = data['CI_PcsMeasuredGeneratorSpeed_std'] / 100
    # #叶轮转速*10
    # data['CI_RotorSpeed_min'] = data['CI_RotorSpeed_min'] * 10
    # data['CI_RotorSpeed_max'] = data['CI_RotorSpeed_max'] * 10
    # data['CI_RotorSpeed_mean'] = data['CI_RotorSpeed_mean'] * 10
    # data['CI_RotorSpeed_std'] = data['CI_RotorSpeed_std'] * 10

    #桨距角*57.3
    # data['CI_PitchPositionA1_mean'] = data['CI_PitchPositionA1_mean'] * 57.3
    # data['CI_PitchPositionA2_mean'] = data['CI_PitchPositionA2_mean'] * 57.3
    # data['CI_PitchPositionA3_mean'] = data['CI_PitchPositionA3_mean'] * 57.3
    # data['CI_PitchPositionA1_min'] = data['CI_PitchPositionA1_min'] * 57.3
    # data['CI_PitchPositionA2_min'] = data['CI_PitchPositionA2_min'] * 57.3
    # data['CI_PitchPositionA3_min'] = data['CI_PitchPositionA3_min'] * 57.3
    # data['CI_PitchPositionA1_max'] = data['CI_PitchPositionA1_max'] * 57.3
    # data['CI_PitchPositionA2_max'] = data['CI_PitchPositionA2_max'] * 57.3
    # data['CI_PitchPositionA3_max'] = data['CI_PitchPositionA3_max'] * 57.3
    # data['CI_PitchPositionA1_std'] = data['CI_PitchPositionA1_std'] * 57.3
    # data['CI_PitchPositionA2_std'] = data['CI_PitchPositionA2_std'] * 57.3
    # data['CI_PitchPositionA3_std'] = data['CI_PitchPositionA3_std'] * 57.3


    data = data[(data['CI_IprRealPower_mean'] > -100) & (data['CI_PcsMeasuredGeneratorSpeed_mean'] > 0) &
                (data['CI_RotorSpeed_mean'] > 0) &
                (data['CI_WindSpeed1_mean'] > 0) &
                (data['CI_IprRealPower_min'] > -300)]

    return data


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


def wind_frequency(data, wtid, wt_type):
    # 风频
    #data['windbin'] = round(data['wind_speed']/1 + 0.00000001)*1
    data['windbin'] = round(data['wind_speed']/0.5 + 0.00000001)*0.5
    result = pd.DataFrame(data.groupby(['windbin'])['time'].count())
    result = result.rename(columns={'time': 'count'})
    #result = result[result['windbin']>0]
    result.reset_index(inplace=True)
    result['ratio'] = result['count']/result['count'].sum()
    #result.to_csv(result_dir + 'wind_frequency.csv')
    x_smooth = np.linspace(result['windbin'].min(), result['windbin'].max(), 50)
    y1_smooth = make_interp_spline(result['windbin'], result['ratio'])(x_smooth)
    plt.figure(figsize=(12, 8), dpi=80)
    plt.grid()
    plt.bar(result['windbin'], result['ratio'], width=0.4, color='#4E79A7', edgecolor='black')
    plt.plot(result['windbin'], result['ratio'], color='r')
    plt.grid()
    #plt.plot(x_smooth, y1_smooth,c='r')
    setpic('Wind Bin[m/s]', 'Ratio')
    plt.title(wtid +' ' + wt_type + ' Wind Frequency', fontsize=20)
    plt.tight_layout()
    return result


def scatter_plot(data, wtid, wt_type):
    '''
    :param data: SCADA 10min数据
    :param result_dir: 结果保存路径
    :return: 散点图
    '''

    data = data[(data['CI_IprRealPower_mean'] > 0) & (data['starting_mean']==0) & (data['stop_mean']==0)]

    rotor_speed_1 = float(config_info[config_info['机型'] == wt_type]['最低叶轮转速'].values[0])
    rotor_speed_2 = float(config_info[config_info['机型'] == wt_type]['最高叶轮转速'].values[0])
    blade_best = float(config_info[config_info['机型'] == wt_type]['最优桨距角'].values[0])

    # 计算拟合曲线和R2
    func = np.polyfit(data['CI_RotorSpeed_mean'], data['CI_PcsMeasuredGeneratorSpeed_mean'], 1)
    p = np.poly1d(func)
    y_pre_rs = p(data['CI_RotorSpeed_mean'])
    ssr = sum((data['CI_PcsMeasuredGeneratorSpeed_mean'] - y_pre_rs)**2)
    sst = sum((data['CI_PcsMeasuredGeneratorSpeed_mean'] - np.mean(data['CI_PcsMeasuredGeneratorSpeed_mean']))**2)
    r2 = round(1-ssr/sst, 5)

    col_list = ['brown', 'chocolate', 'slategrey', 'navy', 'blueviolet', 'lightpink',
                'darkolivegreen', 'lightblue', 'tomato', 'darkseagreen', 'darkorange', 'LightPink']

    plt.figure(figsize=(14, 16), dpi=200)
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.suptitle(wtid + '  ' + wt_type, fontsize=14)

    plt.subplot(321)
    i = 0
    for month in data['month'].unique().tolist():
        data_plot = data[data['month'] == month]
        plt.scatter(data_plot['CI_IprRealPower_mean'], data_plot['CI_RotorSpeed_mean'], c=col_list[i], alpha=0.8,
                    s=3, label=month)
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    plt.yticks(np.arange(0, 21, step=1))
    plt.axhline(rotor_speed_1, ls='--')
    plt.axhline(rotor_speed_2, ls='--')
    plt.text(0, rotor_speed_1+0.5, '叶轮转速最小值为' + str(rotor_speed_1), fontsize=14)
    plt.text(0, rotor_speed_2+0.5, '叶轮转速最大值为' + str(rotor_speed_2), fontsize=14)
    setpic('Active Power', 'Rotor Speed')

    plt.subplot(322)
    i = 0
    for month in data['month'].unique().tolist():
        data_plot = data[data['month'] == month]
        plt.scatter(data_plot['wind_speed'], data_plot['CI_IprRealPower_mean'], c=col_list[i], alpha=0.8,
                    s=3, label=month)
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    setpic('Wind Speed', 'Active Power')

    plt.subplot(323)
    i = 0
    for month in data['month'].unique().tolist():
        data_plot = data[data['month'] == month]
        plt.scatter(data_plot['CI_RotorSpeed_mean'], data_plot['CI_PcsMeasuredElectricalTorque_mean'], c=col_list[i], alpha=0.8,
                    s=3, label=month)
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    setpic('Rotor Speed', 'Torque')

    plt.subplot(324)
    i = 0
    for month in data['month'].unique().tolist():
        data_plot = data[data['month'] == month]
        plt.scatter(data_plot['CI_RotorSpeed_mean'], data_plot['CI_PcsMeasuredGeneratorSpeed_mean'], c=col_list[i], alpha=0.8,
                    s=3, label=month)
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    plt.plot(data['CI_RotorSpeed_mean'], y_pre_rs, color='r', linewidth=1)
    plt.text(10, 6, 'y=' + str(round(p[1],3)) + 'x + (' + str(round(p[0],3)) + ')', fontsize=14)
    plt.text(10,4, 'R2=' + str(r2), fontsize=14)
    setpic('Rotor Speed', 'Generator Speed')

    plt.subplot(325)
    plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_min'], s=0.8, c='green', label='min')
    plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_max'], s=0.8, c='red', label='max')
    plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_mean'], s=0.8, c='blue', label='mean')
    #plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_std'], s=0.8, c='purple', label='std')
    plt.axhline(blade_best, ls='--')
    plt.text(data['CI_WindSpeed1_mean'].max()-5,blade_best-0.05, '最优桨距角为'+str(blade_best), fontsize=14)
    setpic('Wind Speed', 'Pitch Position')
    #plt.title(wtid + ' pitch position 1 vs wind speed')

    plt.subplot(326)
    plt.scatter(data['CI_IprRealPower_min'], data['CI_PitchPositionA1_mean'], s=0.8, c='green', label='min')
    plt.scatter(data['CI_IprRealPower_max'], data['CI_PitchPositionA1_mean'], s=0.8, c='red', label='max')
    plt.scatter(data['CI_IprRealPower_mean'], data['CI_PitchPositionA1_mean'], s=0.8, c='blue', label='mean')
    plt.scatter(data['CI_IprRealPower_std'], data['CI_PitchPositionA1_mean'], s=0.8, c='purple', label='std')
    plt.axhline(blade_best, ls='--')
    plt.text(data['CI_IprRealPower_mean'].max(),blade_best-0.05, '最优桨距角为'+str(blade_best), fontsize=14)
    setpic('Power', 'Pitch Position')


def scatter_plot_humidity(data, wtid, wt_type):
    '''
    :param data: SCADA 10min数据
    :param result_dir: 结果保存路径
    :return: 散点图
    '''

    # 计算拟合曲线和R2
    func = np.polyfit(data['CI_RotorSpeed_mean'], data['CI_PcsMeasuredGeneratorSpeed_mean'], 1)
    p = np.poly1d(func)
    y_pre_rs = p(data['CI_RotorSpeed_mean'])
    ssr = sum((data['CI_PcsMeasuredGeneratorSpeed_mean'] - y_pre_rs)**2)
    sst = sum((data['CI_PcsMeasuredGeneratorSpeed_mean'] - np.mean(data['CI_PcsMeasuredGeneratorSpeed_mean']))**2)
    r2 = round(1-ssr/sst, 5)

    #col_list = ['brown', 'navy']
    col_list = ['#4169E1', '#FF5733']

    plt.figure(figsize=(14, 14), dpi=200)
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.suptitle(wtid + '  ' + wt_type, fontsize=14)

    plt.subplot(221)
    i = 0
    for bool in [False, True]:
        data_plot = data[data['low_temp_high_humidity'] == bool]
        plt.scatter(data_plot['CI_IprRealPower_mean'], data_plot['CI_RotorSpeed_mean'], c=col_list[i], alpha=0.8,
                    s=3+i*2, label='低温高湿为'+str(bool))
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    plt.yticks(np.arange(0, 15, step=1))
    setpic('Active Power', 'Rotor Speed')

    plt.subplot(222)
    i = 0
    for bool in [False, True]:
        data_plot = data[data['low_temp_high_humidity'] == bool]
        plt.scatter(data_plot['wind_speed'], data_plot['CI_IprRealPower_mean'], c=col_list[i], alpha=0.8,
                    s=3+i*2, label='低温高湿为'+str(bool))
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    setpic('Wind Speed', 'Active Power')

    plt.subplot(223)
    i = 0
    for bool in [False, True]:
        data_plot = data[data['low_temp_high_humidity'] == bool]
        plt.scatter(data_plot['CI_RotorSpeed_mean'], data_plot['CI_PcsMeasuredElectricalTorque_mean'], c=col_list[i], alpha=0.8,
                    s=3+i*2, label='低温高湿为'+str(bool))
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
    setpic('Rotor Speed', 'Torque')


    plt.subplot(224)
    i = 0
    for bool in [False, True]:
        data_plot = data[data['low_temp_high_humidity'] == bool]
        #plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_min'], s=0.8, c='green', label='min')
        #plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_max'], s=0.8, c='red', label='max')
        plt.scatter(data_plot['CI_WindSpeed1_mean'], data_plot['CI_PitchPositionA1_mean'], c=col_list[i], alpha=0.8,
                    s=3+i*2, label='低温高湿为'+str(bool))
        plt.legend(fontsize=10, markerscale=2., scatterpoints=1)
        i = i + 1
        #plt.scatter(data['CI_WindSpeed1_mean'], data['CI_PitchPositionA1_std'], s=0.8, c='purple', label='std')
    setpic('Wind Speed', 'Pitch Position')
        #plt.title(wtid + ' pitch position 1 vs wind speed')


def ts_plot(data, wtid, wt_type):
    '''
    :param data: SCADA 10min数据
    :param wtid: 机组编号
    :param wt_type: 机型
    :return: 时序图
    '''
    plt.figure(figsize=(22, 14), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.suptitle(wtid + '  ' + wt_type, fontsize=14)

    plt.subplot(611)
    plt.plot(data['time'], data['wind_speed'], c='darkolivegreen', linewidth=1)
    plt.xticks(rotation=30)
    plt.title('风速时序图')
    setpic('Date', 'Wind Speed')

    plt.subplot(612)
    plt.plot(data['time'], data['CI_OutsideAirTemperature_mean'], c='darkolivegreen', linewidth=1)
    plt.xticks(rotation=30)
    plt.title('环境温度时序图')
    setpic('Date', 'Temperature')

    plt.subplot(613)
    plt.scatter(data['time'], data['CI_PitchRate1_mean'], s=0.8, c='green', label='pitch rate 1')
    plt.scatter(data['time'], data['CI_PitchRate2_mean'], s=0.8, c='red', label='pitch rate 2')
    plt.scatter(data['time'], data['CI_PitchRate3_mean'], s=0.8, c='blue', label='pitch rate 3')
    plt.xticks(rotation=30)
    setpic('Date', 'Pitch Rate')
    plt.title('变桨轴速率时序图')

    plt.subplot(614)
    plt.scatter(data['time'], data['CI_YawError1_mean'], s=0.8, c='green', label='yaw error 1')
    plt.scatter(data['time'], data['CI_YawError2_mean'], s=0.2, c='red', label='yaw error 2')
    plt.xticks(rotation=30)
    setpic('Date', 'Yaw Error')
    plt.title('对风偏差时序图')

    plt.subplot(615)
    plt.scatter(data['time'], data['CI_NacellePosition_mean'], s=0.8, c='green', label='nacelle position')
    plt.xticks(rotation=30)
    setpic('Date', 'Nacelle Position')
    plt.title('机舱位置时序图')
    plt.tight_layout()

    plt.subplot(616)
    plt.scatter(data['time'], data['CI_PitchPositionA1_mean'], s=0.8, c='red', label='blade 1')
    plt.scatter(data['time'], data['CI_PitchPositionA2_mean'], s=0.8, c='green', label='blade 2')
    plt.scatter(data['time'], data['CI_PitchPositionA3_mean'], s=0.8, c='blue', label='blade 3')
    plt.xticks(rotation=30)
    setpic('Date', 'Pitch Position')
    plt.title('桨距角时序图')
    plt.tight_layout()

    #plt.close()


def ts_plot_scatter(data, wtid, wt_type):
    #桨距角 对风偏差 机舱位置 时序图
    plt.figure(figsize=(12, 10), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.subplots_adjust(top=1.5)

    plt.subplot(311)
    plt.scatter(data['time'], data['CI_PitchRate1_mean'], s=0.8, c='green', label='pitch rate 1')
    plt.scatter(data['time'], data['CI_PitchRate1_mean'], s=0.8, c='red', label='pitch rate 2')
    plt.scatter(data['time'], data['CI_PitchRate1_mean'], s=0.8, c='blue', label='pitch rate 3')
    setpic('Date', 'Pitch Rate')
    plt.title(wtid + '  ' + wt_type + ' 变桨轴速率时序图')

    plt.subplot(312)
    plt.scatter(data['time'], data['CI_YawError1_mean'], s=0.8, c='green', label='yaw error 1')
    plt.scatter(data['time'], data['CI_YawError2_mean'], s=0.2, c='red', label='yaw error 2')
    setpic('Date', 'Yaw Error')
    plt.title(wtid + '  ' + wt_type + ' 对风偏差时序图')

    plt.subplot(313)
    plt.scatter(data['time'], data['CI_NacellePosition_mean'], s=0.8, c='green', label='nacelle position')
    setpic('Date', 'Nacelle Position')
    plt.title(wtid + '  ' + wt_type + ' 机舱位置时序图')
    plt.tight_layout()



def ws_pitch_plot(data, wtid, wt_type):
    #风速 桨距角
    plt.figure(figsize=(12,10), dpi=120)
    plt.subplots_adjust(top=1.5)

    plt.subplot(211)
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA1_min'], s=0.8, c='green', label='min')
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA1_max'], s=0.8, c='red', label='max')
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA1_mean'], s=0.8, c='blue', label='mean')
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA1_std'], s=0.8, c='purple', label='std')
    setpic(' ', 'Pitch Position')
    plt.title(wtid + '  ' + wt_type + ' pitch position 1 vs wind speed')

    plt.subplot(212)
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA1_mean'], s=0.8, c='green', label='pitch 1')
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA2_mean'], s=0.8, c='red', label='pitch 2')
    plt.scatter(data['wind_speed'], data['CI_PitchPositionA3_mean'], s=0.8, c='blue', label='pitch 3')
    setpic('Wind Speed', 'Pitch Position')
    plt.title(wtid + '  ' + wt_type + ' 1 vs 2 vs 3')


# def power_pitch_plot(data, wtid, wt_type):
#     #功率 桨距角
#     plt.figure(figsize=(12,8), dpi=120)
#     plt.rcParams['axes.unicode_minus'] = False
#     plt.scatter(data['CI_IprRealPower_min'], data['CI_PitchPositionA1_mean'], s=0.8, c='green', label='min')
#     plt.scatter(data['CI_IprRealPower_max'], data['CI_PitchPositionA1_mean'], s=0.8, c='red', label='max')
#     plt.scatter(data['CI_IprRealPower_mean'], data['CI_PitchPositionA1_mean'], s=0.8, c='blue', label='mean')
#     plt.scatter(data['CI_IprRealPower_std'], data['CI_PitchPositionA1_mean'], s=0.8, c='purple', label='std')
#     setpic('Power', 'Pitch Position')
#     plt.title(wtid + '  ' + wt_type + ' power vs pitch position 1', fontsize=16)
#     plt.gcf().subplots_adjust(left=0.05,top=0.91,bottom=0.09)
#     plt.tight_layout()


def power_ws(data, wtid, wt_type):
    plt.figure(figsize=(12,8), dpi=120)
    plt.rcParams['axes.unicode_minus'] = False
    plt.scatter(data['wind_speed'], data['CI_IprRealPower_min'], s=0.8, c='green', label='min')
    plt.scatter(data['wind_speed'], data['CI_IprRealPower_max'], s=0.8, c='red', label='max')
    plt.scatter(data['wind_speed'], data['CI_IprRealPower_mean'], s=0.8, c='blue', label='mean')
    plt.scatter(data['wind_speed'], data['CI_IprRealPower_std'], s=0.8, c='purple', label='std')
    setpic('Wind Speed', 'Power')
    y_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    plt.title(wtid + '  ' + wt_type + '  power vs wind speed', fontsize=16)
    plt.tight_layout()
    #plt.show()


# 风速-偏航偏差散点图
def ws_yaw(data, wtid, wt_type):
    data_plot = data[['wind_speed', 'CI_YawError1_mean']]

    data_plot['CI_YawError1_mean'] = data_plot['CI_YawError1_mean'] - 180
    data_plot['error_bin'] = round(data['CI_YawError1_mean'] / 0.1 + 0.00000001) * 0.1
    data_plot['windbin'] = round(data_plot['wind_speed']/1 + 0.00000001)*1
    result = pd.DataFrame(data_plot.groupby('error_bin').agg({'wind_speed':'count', 'CI_YawError1_mean':'mean'}))
    result.reset_index(drop=False, inplace=True)
    result.columns = ['error_bin', 'count', 'error_mean']
    error_most = result.loc[np.argmax(result['count']), 'error_mean']
    error_max = data_plot.loc[np.argmax(data_plot['wind_speed']), 'CI_YawError1_mean']
    error_diff = error_most - error_max


    yaw_mean_all = pd.DataFrame(data_plot.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_all.reset_index(drop=False, inplace=True)
    yaw_mean_all = yaw_mean_all.sort_values(by=['CI_YawError1_mean'])
    yaw_data_neg = data_plot[data_plot['CI_YawError1_mean']<0]
    yaw_mean_neg = pd.DataFrame(yaw_data_neg.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_neg.reset_index(drop=False, inplace=True)
    yaw_data_pos = data_plot[data_plot['CI_YawError1_mean']>0]
    yaw_mean_pos = pd.DataFrame(yaw_data_pos.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_pos.reset_index(drop=False, inplace=True)

    plt.figure(figsize=(12,8), dpi=80)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.scatter(data_plot['CI_YawError1_mean'], data_plot['wind_speed'], s=5)

    plt.plot(yaw_mean_all['CI_YawError1_mean'], yaw_mean_all['windbin'], marker='o', c='red', label='各风仓对风偏差均值')
    plt.plot(yaw_mean_pos['CI_YawError1_mean'], yaw_mean_pos['windbin'], marker='o', c='purple', label='各风仓对风偏差均值')
    plt.plot(yaw_mean_neg['CI_YawError1_mean'], yaw_mean_neg['windbin'], marker='o', c='darkgreen', label='各风仓对风偏差均值')
    plt.text(10, 20, '对风偏差平均值为'+str(round(yaw_mean_all['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.text(100, 12, '正向平均值为' + str(round(yaw_mean_pos['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.text(-150, 12, '负向平均值为' + str(round(yaw_mean_neg['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.grid()
    plt.ylim(0,25)
    # plt.axvline(x=error_most, ymin=0, ymax=1, c="red", ls="--", lw=2, alpha=0.7)
    # plt.axvline(x=error_max, ymin=0, ymax=1, c="red", ls="-", lw=2, alpha=0.7)
    # plt.text(max(error_max, error_most)+2, data_plot['wind_speed'].max()-2, '差值=' + str(abs(round(error_diff,2))), fontsize=16, c='red', weight='heavy')
    plt.title(wtid + ' ' + wt_type +' 风速-偏航偏差散点图', fontsize=18)
    setpic('Yaw Error', 'Wind Speed')


# 功率曲线 cp
def power_curve_cp(data, wtid, wt_type):
    data = data[(data['CI_IprRealPower_mean'] > 0) & (data['starting_mean']==0) & (data['stop_mean']==0)]
    # data['windbin'] = round(data['wind_speed'] / 1 + 0.00000001) * 1
    data['windbin'] = round(data['wind_speed'] / 0.5 + 0.00000001) * 0.5
    #data['windbin'] = round(data['wind_speed'] / 0.5 + 0.00000001) * 0.5  # 风速分仓 从切入风速开始， 3 代表2.75~3.25
    result = pd.DataFrame(data.groupby('windbin').agg({'CI_IprRealPower_mean':'mean', 'wind_speed':'mean', 'time':'count'}))
    result = result.reset_index(drop=False)
    result['ws_ratio'] = result['time'] / result['time'].sum()
    result = result.drop(['time'], axis=1)
    area = float(config_info[config_info['机型'] == wt_type]['扫风面积'].values[0])

    result['cp'] = result['CI_IprRealPower_mean'] / (1.225 * area * result['wind_speed']**3 / 2) * 1000
    gua_curve = config_gua_power[config_gua_power['机型'] == wt_type]
    gua_curve['cp'] = gua_curve['功率']/(1.225*area*gua_curve['风速']**3)*2000
    ws_min = gua_curve['风速'].min()
    ws_max = gua_curve['风速'].max()
    result = result[(result['windbin'] >= ws_min) * (result['windbin'] <= ws_max)]
    result['wtid'] = wtid
    result['wt_type'] = wt_type
    result.reset_index(drop=True, inplace=True)
    cp_max = round(result.loc[np.argmax(result['cp']), 'cp'], 2)
    cp_wind_max = round(result.loc[np.argmax(result['cp']), 'wind_speed'], 1)

    fig = plt.figure(figsize=(12, 8), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.suptitle(wtid + '  ' + wt_type, fontsize=14)
    ax1 = fig.add_subplot(111)

    ax1.plot(result['wind_speed'], result['CI_IprRealPower_mean'], 'b', label="实际功率曲线")
    ax1.plot(gua_curve['风速'], gua_curve['功率'], 'r', label="担保功率曲线")
    ax1.legend(loc=1)
    plt.grid()
    ax1.set_ylabel('功率')
    ax1.set_xlabel('风速')
    y_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)

    ax2 = ax1.twinx()  # this is the important function
    ax2.plot(result['wind_speed'], result['cp'], 'g', label="实际Cp")
    ax2.plot(gua_curve['风速'], gua_curve['cp'], 'orange', label="担保Cp")
    plt.text(cp_wind_max, cp_max+0.01, 'Cp最大值为：' + str(cp_max)+', 对应风速为'+str(cp_wind_max), horizontalalignment='center', weight='bold')
    ax2.legend(loc=2)
    ax2.set_ylabel('Cp')
    plt.xticks(np.arange(0, ws_max, step=1))
    #plt.show()
    return(result)


# 功率曲线无cp
def power_curve(data, wtid, wt_type):
    data = data[(data['CI_IprRealPower_mean'] > 0) & (data['starting_mean']==0) & (data['stop_mean']==0)]
    #data['windbin'] = round(data['wind_speed'] / 1 + 0.00000001) * 1
    data['windbin'] = round(data['wind_speed'] / 0.5 + 0.00000001) * 0.5  # 风速分仓 从切入风速开始， 3 代表2.75~3.25
    result = pd.DataFrame(data.groupby('windbin').agg({'CI_IprRealPower_mean':'mean', 'wind_speed':'mean', 'time':'count'}))
    result = result.reset_index(drop=False)
    result = result.rename(columns={'time': 'count'})

    # result['ws_ratio'] = result['time'] / result['time'].sum()
    # result = result.drop(['time'], axis=1)
    # area = float(config_info[config_info['机型'] == wt_type]['扫风面积'].values[0])
    # result['cp'] = result['CI_IprRealPower_mean'] / (1.225 * area * result['wind_speed']**3 / 2) * 1000
    gua_curve = config_gua_power[config_gua_power['机型'] == wt_type]
    #gua_curve['cp'] = gua_curve['功率']/(1.225*area*gua_curve['风速']**3)*2000
    ws_min = gua_curve['风速'].min()
    ws_max = gua_curve['风速'].max()
    result = result[(result['windbin'] >= ws_min) * (result['windbin'] <= ws_max)]
    result['wtid'] = wtid
    # result['wt_type'] = wt_type
    # result.reset_index(drop=True, inplace=True)
    # cp_max = round(result.loc[np.argmax(result['cp']), 'cp'], 2)
    # cp_wind_max = round(result.loc[np.argmax(result['cp']), 'wind_speed'], 1)

    gua_curve = config_gua_power[config_gua_power['机型'] == wt_type]
    gua_curve.columns = ['windbin', 'guaranteed_power_curve', 'wt_type']
    result = pd.merge(result, gua_curve, on='windbin', how='left')
    result['power/gua_power'] = result['CI_IprRealPower_mean']/result['guaranteed_power_curve']
    result['power/gua_power'] = result['power/gua_power'].apply(lambda x: "{:.1%}".format(x))

    plt.figure(figsize=(12, 8), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.title(wtid+'机组功率曲线', fontsize=18)
    plt.plot(result['wind_speed'], result['CI_IprRealPower_mean'], 'yellow', label="实际功率曲线")
    plt.plot(gua_curve['windbin'], gua_curve['guaranteed_power_curve'], 'red', label='合同功率曲线')
    plt.scatter(data['wind_speed'], data['CI_IprRealPower_mean'], s=10)
    plt.yticks(np.arange(0, 1700, step=100))
    plt.legend(loc=1)
    plt.grid()
    setpic('风速', '功率')
    #plt.show()
    result = result[(result['windbin'] >= 3) & (result['windbin'] <= 25)]
    result['CI_IprRealPower_mean'] = result['CI_IprRealPower_mean'].apply(lambda x: "%.2f" % x)
    result['wind_speed'] = result['wind_speed'].apply(lambda x: "%.2f" % x)
    #result = result.drop(['windbin'], axis=1)
    result.reset_index(drop=True, inplace=True)

    result = result[['wtid', 'wt_type', 'windbin', 'wind_speed', 'CI_IprRealPower_mean', 'guaranteed_power_curve', 'count', 'power/gua_power']]
    result.columns = ['机组编号', '机型', '风仓', '风速均值', '功率均值', '合同功率', '点数', '功率均值/合同功率*100%']
    return(result)


# 威布尔
def weibull_generation(wt_type, k, ws):
    gua_curve = config_gua_power[config_gua_power['机型'] == wt_type]
    gua_curve = gua_curve.reset_index(drop=True)
    gua_curve['accumulate'] = 1-np.exp(-(gua_curve['风速']/ws)**k)
    gua_curve['distribution'] = gua_curve['accumulate'].diff()
    gua_curve['distribution'][0] = gua_curve['accumulate'][0]
    gua_curve['功率_shift'] = gua_curve['功率'].shift()
    gua_curve['功率_shift'][0] = 0
    gua_curve['mean_power'] = (gua_curve['功率'] + gua_curve['功率_shift'])/2 * gua_curve['distribution']
    #weibull_power = gua_curve['mean_power'].sum() * 0.876
    return(gua_curve)


# 10分钟湍流
def turbulence_plot(data, wtid, wt_type):
    turbulence_data = data[['time', 'CI_WindSpeed1_mean', 'CI_WindSpeed1_std']]
    turbulence_data['10min_turb'] = turbulence_data['CI_WindSpeed1_std'] / turbulence_data['CI_WindSpeed1_mean']
    turbulence_data['windbin'] = round(turbulence_data['CI_WindSpeed1_mean']/1 + 0.00000001)*1
    turb_bin = pd.DataFrame(turbulence_data.groupby(['windbin'])['10min_turb'].mean())
    turb_bin.reset_index(drop=False, inplace=True)

    plt.figure(figsize=(12,8), dpi=80)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.scatter(turbulence_data['CI_WindSpeed1_mean'], turbulence_data['10min_turb'], s=5, label='机组风速仪湍流')
    plt.plot(turb_bin['windbin'], turb_bin['10min_turb'], marker='o', c='red', label='机组风速仪各风仓湍流均值')
    plt.plot(config_IEC['风速（m/s）'], config_IEC['IEC A+'], c='darkseagreen', label='IEC A+')
    plt.plot(config_IEC['风速（m/s）'], config_IEC['IEC A'], c='darkolivegreen', label='IEC A')
    plt.plot(config_IEC['风速（m/s）'], config_IEC['IEC B'], c='darkorange', label='IEC B')
    plt.plot(config_IEC['风速（m/s）'], config_IEC['IEC C'], c='tomato', label='IEC C')
    if (15 in turb_bin['windbin'].tolist()):
        plt.text(15, turb_bin.loc[turb_bin['windbin']==15]['10min_turb'].values[0]+0.03, round(turb_bin.loc[turb_bin['windbin']==15]['10min_turb'].values[0], 2), fontsize=14)
    elif (15 not in turb_bin['windbin'].tolist()) & (14 in turb_bin['windbin'].tolist()) & (16 in turb_bin['windbin'].tolist()):
        turb_15 = (turb_bin.loc[turb_bin['windbin']==14]['10min_turb'].values[0] + turb_bin.loc[turb_bin['windbin']==16]['10min_turb'].values[0]) / 2
        plt.text(15, turb_15+0.03, round(turb_15, 2), fontsize=14)

    plt.xlim(3, turbulence_data['windbin'].max())
    plt.ylim(0, 1)
    plt.legend()
    plt.title(wtid + ' ' + wt_type + ' 湍流强度', fontsize=18)
    setpic('风速[m/s]', '湍流强度')

    #plt.show()


# 对风偏差
def yaw_error_plot(data, wtid, wt_type):
    yaw_data = data[['time', 'CI_WindSpeed1_mean', 'CI_YawError1_mean']]
    yaw_data['CI_YawError1_mean'] = yaw_data['CI_YawError1_mean'] - 180
    yaw_data['windbin'] = round(yaw_data['CI_WindSpeed1_mean']/1 + 0.00000001)*1
    yaw_mean_all = pd.DataFrame(yaw_data.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_all.reset_index(drop=False, inplace=True)
    yaw_data_neg = yaw_data[yaw_data['CI_YawError1_mean']<0]
    yaw_mean_neg = pd.DataFrame(yaw_data_neg.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_neg.reset_index(drop=False, inplace=True)
    yaw_data_pos = yaw_data[yaw_data['CI_YawError1_mean']>0]
    yaw_mean_pos = pd.DataFrame(yaw_data_pos.groupby(['windbin'])['CI_YawError1_mean'].mean())
    yaw_mean_pos.reset_index(drop=False, inplace=True)


    plt.figure(figsize=(12,8), dpi=80)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.scatter(yaw_data['CI_WindSpeed1_mean'], yaw_data['CI_YawError1_mean'], s=5, label='10min平均值散点')
    plt.plot(yaw_mean_all['windbin'], yaw_mean_all['CI_YawError1_mean'], marker='o', c='red', label='各风仓对风偏差均值')
    plt.plot(yaw_mean_pos['windbin'], yaw_mean_pos['CI_YawError1_mean'], marker='o', c='purple', label='各风仓对风偏差均值')
    plt.plot(yaw_mean_neg['windbin'], yaw_mean_neg['CI_YawError1_mean'], marker='o', c='darkseagreen', label='各风仓对风偏差均值')
    plt.text(10, 0.5, '对风偏差平均值为'+str(round(yaw_mean_all['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.text(10, 20, '正向平均值为' + str(round(yaw_mean_pos['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.text(10, -20, '负向平均值为' + str(round(yaw_mean_neg['CI_YawError1_mean'].mean(), 4)), fontsize=15)
    plt.xlim(2, yaw_mean_all['windbin'].max())
    #plt.ylim(-4, 4)
    plt.legend()
    plt.title(wtid + ' ' + wt_type + ' 对风偏差', fontsize=18)
    setpic('风速[m/s]', '对风偏差[deg]')

    #plt.show()


# 空气密度划分
def density_level(num):
    if (num>0.9) & (num<=0.95):
        level = '(0.9, 0.95]'
    elif (num>0.95) & (num<=1):
        level = '(0.95, 1.00]'
    elif (num>1) & (num<=1.05):
        level = '(1.00, 1.05]'
    elif (num>1.05) & (num<=1.1):
        level = '(1.05, 1.10]'
    elif (num > 1.1) & (num<=1.15):
        level = '(1.1, 1.15]'
    else:
        level = '缺信息'
    return level
#
# def density_level(num):
#     #level = 0
#     if (num>1) & (num<=1.05):
#         level = '(1.00, 1.05]'
#     elif (num>1.05) & (num<=1.1):
#         level = '(1.05, 1.10]'
#     elif (num>1.1) & (num<=1.15):
#         level = '(1.10, 1.15]'
#     elif (num>1.15) & (num<=1.2):
#         level = '(1.15, 1.20]'
#     elif (num > 1.2) & (num<=1.25):
#         level = '(1.20, 1.25]'
#     elif num>1.25:
#         level = '(1.25,inf)'
#     else:
#         level = '缺信息'
#     return level


# 风速功率密度散点
def power_curve_density(data, wtid, wt_type):
    density_data = data[['time', 'wind_speed', 'CI_IprRealPower_mean', 'air_density_10min']]
    density_data[density_data.select_dtypes(include=['object']).columns] = density_data.select_dtypes(include=['object']).apply(
        pd.to_numeric, errors='coerce')
    #density_data = density_data[density_data['time'] <= '2022-05-31']
    density_data['density_level'] = density_data.apply(lambda x: density_level((x['air_density_10min'])), axis=1)


    plt.figure(figsize=(12,8), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    for i in sorted(density_data['density_level'].unique().tolist()):
        plot_data = density_data[density_data['density_level']==i]
        plot_data['windbin'] = round(plot_data['wind_speed'] / 0.5 + 0.00000001) * 0.5  # 风速分仓 从切入风速开始， 3 代表2.75~3.25
        result = pd.DataFrame(
            plot_data.groupby('windbin').agg({'CI_IprRealPower_mean': 'mean', 'wind_speed': 'mean'}))
        result = result.reset_index(drop=False)

        plt.plot(result['windbin'], result['CI_IprRealPower_mean'], label='空气密度属于' + str(i))
    plt.title(wtid + ' ' + wt_type + ' 区分空气密度的功率曲线', fontsize=18)
    setpic('风速[m/s]', '功率[kW]')

    #sns.scatterplot(data=density_data, x='wind_speed', y='CI_IprRealPower_mean', hue='density_level')
    #plt.scatter(density_data['wind_speed'], density_data['air_density_10min'], c=density_data['density_level'])




def dataProcess(pdir, result_dir):
    generation = pd.DataFrame()
    gen1_list = []
    gen2_list = []
    gen3_list = []
    wtid_list = []
    type_list = []

    usable_ratio = pd.DataFrame()
    usable_list = []

    ws_year_mean = pd.DataFrame()


    power_curve_df = pd.DataFrame()
    energy_all = pd.DataFrame(columns=['time', 'energy', 'wtid'])

    energy_year = pd.DataFrame()

    temperature_all = pd.DataFrame(columns=['time', 'CI_OutsideAirTemperature_mean', 'wtid'])
    air_density_all = pd.DataFrame(columns=['time', 'air_density', 'wtid'])
    del_reason_all = pd.DataFrame(columns=['起始时间', '结束时间', '原因', '机组编号'])

    humidity_all = pd.DataFrame()

    file_list = read_path(pdir)
    #para_k = input('Enter Weibull k: ')
    #para_ws = input('Enter Weibull wind speed: ')
    #print('k = ' + str(para_k) + ' and wind speed = ' + str(para_ws))
    for file in file_list:
        try:
            ori_data = pd.read_csv(file, index_col=0)
            wtid = file.split('\\')[-1].split('.')[0].split('_')[0]
            wt_type = config_id.loc[config_id['机位号'] == wtid, '机型'].values[0]

            ori_len = len(ori_data)
            ori_index = ori_data.index

            ori_data = ori_data.set_index('time')
            nan_len = len(ori_data[ori_data.isnull().T.all()])
            ori_data = ori_data.reset_index()

            wind_frequence_data = data_clean_wind(ori_data)

            wind_frequence_data['time'] = pd.to_datetime(wind_frequence_data['time'])

            wind_frequence_data = pd.merge(wind_frequence_data, config_density_10min, how='left', on='time')
            # data['wind_speed'] = data['CI_WindSpeed1_mean'] * (data['air_density'] / 1.225) ** (1 / 3)

            # 折算风速 --- 测风塔数据不准时使用 （海拔和温度 海拔1864）
            # data['air_density'] = (353.05 / (data['CI_OutsideAirTemperature_mean'] + 273.15)) * np.exp(
            #     -0.034 * (1864 / (data['CI_OutsideAirTemperature_mean'] + 273.15)))
            # data['wind_speed'] = data['CI_WindSpeed1_mean'] * (data['air_density'] / 1.225) ** (1 / 3)


            # 19#机组重新折算（y=0.925x+0.112）
            # data['CI_WindSpeed1_mean'] = data['CI_WindSpeed1_mean'].apply(lambda x: (x-0.112)/0.925)
            # # 风速乘0.88
            # data['CI_WindSpeed1_mean'] = data['CI_WindSpeed1_mean'].apply(lambda x: (x * 0.90))


            # 折算风速 -- 测风塔月均值折算
            # data['air_density'] = 0
            # for month in data['month'].unique().tolist():
            #     density = config_density.loc[config_density['时间'] == month, '空气密度'].values[0]
            #     data.loc[data[data['month'] == month].index, 'air_density'] = density

            wind_frequence_data['wind_speed'] = wind_frequence_data['CI_WindSpeed1_mean'] * (wind_frequence_data['air_density_10min']/1.225)**(1/3)



            ori_data['wind_diff'] = ori_data['CI_WindSpeed1_mean'].diff()
            ori_data['wind_diff_2'] = ori_data['CI_WindSpeed1_mean'].diff(2)
            ori_data['fixed_wind'] = (ori_data['wind_diff'] == 0) & (ori_data['wind_diff_2'] == 0)

            data = copy.deepcopy(ori_data)
            data = data[data['fixed_wind'] == False]
            data = data_clean(data)
            keep_index = data.index
            del_index = list(set(ori_index) - set(keep_index))
            del_data = ori_data.loc[del_index, :]

            del_data['风速连续不变'] = [('风速连续不变' if x == True else '数据超限') for x in del_data['fixed_wind']]
            del_data['功率均值超限'] = [('功率均值超限' if (x <= -100*1000) | np.isnan(x) else '') for x in del_data['CI_IprRealPower_mean']]
            del_data['功率最小值超限'] = [('功率最小值超限' if( x <= -300 * 1000) | np.isnan(x) else '') for x in del_data['CI_IprRealPower_min']]
            del_data['发电机转速超限'] = [('发电机转速超限' if (x <= 0) | np.isnan(x) else '') for x in del_data['CI_PcsMeasuredGeneratorSpeed_mean']]
            del_data['叶轮转速超限'] = [('叶轮转速超限' if (x <= 0) | np.isnan(x) else '') for x in del_data['CI_RotorSpeed_mean']]
            del_data['风速超限'] = [('风速超限' if (x <= 0) | np.isnan(x) else '') for x in del_data['CI_WindSpeed1_mean']]

            power_mean_len = len(del_data[del_data['功率均值超限'] == '功率均值超限'])
            power_min_len = len(del_data[del_data['功率最小值超限'] == '功率最小值超限'])
            gen_len = len(del_data[del_data['发电机转速超限'] == '发电机转速超限'])
            rotor_len = len(del_data[del_data['叶轮转速超限'] == '叶轮转速超限'])
            ws_len = len(del_data[del_data['风速超限'] == '风速超限'])
            fixed_len = len(del_data[del_data['风速连续不变'] == '风速连续不变'])


            del_len = pd.DataFrame({'主要参数': ['功率均值', '功率最小值', '发电机转速均值', '叶轮转速均值', '风速均值', '固定风速', '空值'],
                                    '合理范围': ['大于-100', '大于-300', '大于0', '大于0', '大于0', '连续三个点不变', '全为空值'],
                                    '异常点数': [power_mean_len, power_min_len, gen_len, rotor_len, ws_len, fixed_len, nan_len]})

            result_dir_len = result_dir + 'del_len/'
            if not os.path.exists(result_dir_len):
                os.makedirs(result_dir_len)
            del_len.to_csv(result_dir_len + wtid + '_del_len.csv')

            del_data['超限原因'] = del_data['功率均值超限'] + del_data['功率最小值超限'] + del_data['发电机转速超限'] + del_data['叶轮转速超限'] + del_data['风速超限']
            del_data = del_data.drop(columns=['功率均值超限', '功率最小值超限', '发电机转速超限', '叶轮转速超限', '风速超限', 'wind_diff', 'wind_diff_2'])
            del_data.reset_index(drop=True, inplace=True)

            result_dir_del = result_dir + 'del_data/'
            if not os.path.exists(result_dir_del):
                os.makedirs(result_dir_del)
            del_data.to_csv(result_dir_del + wtid + '_del_data.csv')

            del_data['time'] = pd.to_datetime(del_data['time'])
            del_data['time_diff'] = del_data['time'] - del_data['time'].shift()
            del_data.loc[0, 'time_diff'] = del_data.loc[1, 'time_diff']
            del_data['time_diff'] = del_data['time_diff'].apply(lambda x: x.total_seconds())

            start_list = []
            end_list = []
            reason_list = []
            grouped = del_data.groupby(((del_data['time_diff'].shift() != del_data['time_diff'])).cumsum())
            for k, v in grouped:
                # 两天288个点
                if (len(v) >= 288) & (600 in v['time_diff']):
                    v.reset_index(drop=True, inplace=True)
                    start = v.loc[0, 'time']
                    start_list.append(start)
                    end = v.loc[len(v)-1, 'time']
                    end_list.append(end)
                    reason = v['剔除原因'].unique()[0]
                    if reason == '数据超限':
                        reason = v['超限原因'].unique()[0]
                    reason_list.append(reason)

            del_reason = pd.DataFrame({'起始时间': start_list,
                                    '结束时间': end_list,
                                    '原因': reason_list})
            del_reason['机组编号'] = wtid
            del_reason_all = pd.concat([del_reason_all, del_reason])


            new_len = len(data)
            ratio = new_len / ori_len
            usable_list.append(ratio)

            data.reset_index(drop=True, inplace=True)
            data.drop([len(data) - 1], inplace=True)  # 最后一行是下个月
            data['month'] = data['time'].astype(str).apply(lambda x: x[0:7])
            data['time'] = data['time'].str[0:19]
            data['time'] = pd.to_datetime(data['time'])

            #去除2023多余数据
            data = data[data['month'] != '2023-01']


            data = pd.merge(data, tower_humidity, on='time', how='left')
            data['low_temp_high_humidity'] = data.apply(lambda x: (x['CI_OutsideAirTemperature_mean']<0) & (x['湿度']>80), axis=1)
            humidity_count = len(data[data['low_temp_high_humidity'] == True])
            humidity_id_df = pd.DataFrame({'机组编号': [wtid], '机型': [wt_type], '异常点数': [humidity_count]})
            humidity_all = pd.concat([humidity_all, humidity_id_df])


            data_temperature = data[['time', 'CI_OutsideAirTemperature_mean']]
            data_temperature['wtid'] = wtid
            temperature_all = pd.concat([temperature_all, data_temperature])


            # 折算风速 --- 测风塔数据准确时
            # 测风塔10min温度计算空气密度

            data = pd.merge(data, config_density_10min, how='left', on='time')
            # data['wind_speed'] = data['CI_WindSpeed1_mean'] * (data['air_density'] / 1.225) ** (1 / 3)

            # 折算风速 --- 测风塔数据不准时使用 （海拔和温度 海拔1864）
            # data['air_density'] = (353.05 / (data['CI_OutsideAirTemperature_mean'] + 273.15)) * np.exp(
            #     -0.034 * (1864 / (data['CI_OutsideAirTemperature_mean'] + 273.15)))
            # data['wind_speed'] = data['CI_WindSpeed1_mean'] * (data['air_density'] / 1.225) ** (1 / 3)


            # 19#机组重新折算（y=0.925x+0.112）
            # data['CI_WindSpeed1_mean'] = data['CI_WindSpeed1_mean'].apply(lambda x: (x-0.112)/0.925)
            # # 风速乘0.88
            # data['CI_WindSpeed1_mean'] = data['CI_WindSpeed1_mean'].apply(lambda x: (x * 0.90))


            # 折算风速 -- 测风塔月均值折算
            # data['air_density'] = 0
            # for month in data['month'].unique().tolist():
            #     density = config_density.loc[config_density['时间'] == month, '空气密度'].values[0]
            #     data.loc[data[data['month'] == month].index, 'air_density'] = density

            data['wind_speed'] = data['CI_WindSpeed1_mean'] * (data['air_density_10min']/1.225)**(1/3)

            ws_year_wtid = pd.DataFrame({'wtid': [wtid], 'ws_year_mean': [wind_frequence_data['wind_speed'].mean()]})
            #para_ws = data['wind_speed'].mean() + 3
            ws_year_mean = pd.concat([ws_year_mean, ws_year_wtid])


            data_density = data[['time', 'air_density_10min']]
            data_density['wtid'] = wtid
            air_density_all = pd.concat([air_density_all, data_density])



            # 绘制功率曲线+cp图
            power_curve_cp(data, wtid, wt_type)
            result_dir_pccp = result_dir + 'power_curve_cp_plot/'
            if not os.path.exists(result_dir_pccp):
                os.makedirs(result_dir_pccp)
            plt.savefig(result_dir_pccp + wtid + '_power_curve_plots.png')
            plt.close()


            # 绘制功率曲线和散点图
            power_curve_csv = power_curve(data, wtid, wt_type)
            result_dir_pc = result_dir + 'power_curve_plot/'
            if not os.path.exists(result_dir_pc):
                os.makedirs(result_dir_pc)
            power_curve_csv.to_csv(result_dir_pc + wtid + '_power_curve_plots.csv')
            plt.savefig(result_dir_pc + wtid + '_power_curve_plots.png')
            plt.close()


            # 绘制风频分布
            wind_frequency_df = wind_frequency(wind_frequence_data, wtid, wt_type)
            result_dir_wf = result_dir + 'wind_frequency/'
            if not os.path.exists(result_dir_wf):
                os.makedirs(result_dir_wf)
            plt.savefig(result_dir_wf + wtid + '_wind_frequency_plot.png')
            plt.close()


            # 绘制散点图
            scatter_plot(data, wtid, wt_type)
            result_dir_sp = result_dir + 'scatter_plot/'
            if not os.path.exists(result_dir_sp):
                os.makedirs(result_dir_sp)
            plt.savefig(result_dir_sp + wtid + '_scatter_plots.png')
            plt.close()

            # 湍流图
            turbulence_plot(data, wtid, wt_type)
            result_dir_turb = result_dir + 'turbulence_plot/'
            if not os.path.exists(result_dir_turb):
                os.makedirs(result_dir_turb)
            plt.savefig(result_dir_turb + wtid + '_turbulence_plot.png')
            plt.close()

            # 对风偏差图
            yaw_error_plot(data, wtid, wt_type)
            result_dir_yaw = result_dir + 'yaw_error_plot/'
            if not os.path.exists(result_dir_yaw):
                os.makedirs(result_dir_yaw)
            plt.savefig(result_dir_yaw + wtid + '_yaw_error_plot.png')
            plt.close()

            # 绘制湿度相关散点
            scatter_plot_humidity(data, wtid, wt_type)
            result_dir_humidity = result_dir + 'humidity/'
            if not os.path.exists(result_dir_humidity):
                os.makedirs(result_dir_humidity)
            plt.savefig(result_dir_humidity + wtid + '_scatter_plots_humidity.png')
            plt.close()

            # 绘制时序图
            ts_plot(data, wtid, wt_type)
            result_dir_tp = result_dir + 'ts_plot/'
            if not os.path.exists(result_dir_tp):
                os.makedirs(result_dir_tp)
            plt.savefig(result_dir_tp + wtid + '_ts_plots.png')
            plt.close()

            # 区分密度的风速功率散点
            power_curve_density(data, wtid, wt_type)
            result_dir_density = result_dir + 'power_curve_density_plot/'
            if not os.path.exists(result_dir_density):
                os.makedirs(result_dir_density)
            plt.savefig(result_dir_density + wtid + '_power_curve_density_plot.png')
            plt.close()

            # 时序散点图 -- 剔除
            #ts_plot_scatter(data, wtid, wt_type)
            #result_dir_ts = result_dir + 'ts_plot/'
            #if not os.path.exists(result_dir_ts):
            #    os.makedirs(result_dir_ts)
            #plt.savefig(result_dir_ts + wtid + '_time_series.png')
            #plt.close()

            # 绘制风速桨距角散点图  -- 剔除
            #ws_pitch_plot(data, wtid, wt_type)
            #result_dir_pitch_position = result_dir + 'pitch_position/'
            #if not os.path.exists(result_dir_pitch_position):
            #    os.makedirs(result_dir_pitch_position)
            #plt.savefig(result_dir_pitch_position + wtid + '_pitch_position.png')
            #plt.close()

            # 绘制功率桨距角散点图
            # power_pitch_plot(data, wtid, wt_type)
            # result_dir_pitch_power = result_dir + 'pitch_power/'
            # if not os.path.exists(result_dir_pitch_power):
            #     os.makedirs(result_dir_pitch_power)
            # plt.savefig(result_dir_pitch_power + wtid + '_pitch_power.png')
            # plt.close()

            # 绘制剔除限功率和正常停机的散点图
            power_ws(data, wtid, wt_type)
            result_dir_power_ws = result_dir + 'power_ws/'
            if not os.path.exists(result_dir_power_ws):
                os.makedirs(result_dir_power_ws)
            plt.savefig(result_dir_power_ws + wtid + '_power_ws.png')
            plt.close()

            # 绘制风速偏航偏差散点图
            ws_yaw(data, wtid, wt_type)
            result_dir_ws_yaw = result_dir + 'ws_yaw/'
            if not os.path.exists(result_dir_ws_yaw):
                os.makedirs(result_dir_ws_yaw)
            plt.savefig(result_dir_ws_yaw + wtid + '_ws_yaw.png')
            plt.close()

            # 计算发电量
            # 理论发电量 --- 威布尔
            # weibull_power_curve = weibull_generation(wt_type, float(para_k), float(para_ws))
            # weibull_power_curve = weibull_power_curve.rename(columns = {'风速':'windbin'})
            # gen1 = weibull_power_curve['mean_power'].sum() * 0.876
            # gen1_list.append(gen1)

            # # 理论发电量 --- 可研报告 -- 暂无
            # gen1 = config_keyan.loc[config_keyan[config_keyan['wtid'] == wtid].index, '理论发电量'].values[0]
            # gen1_list.append(gen1)

            # 实际功率曲线
            actual_power_curve = power_curve_cp(data, wtid, wt_type)
            actual_power_curve = pd.merge(actual_power_curve, wind_frequency_df, on='windbin')
            power_curve_df = pd.concat([power_curve_df, actual_power_curve], axis=0)
            power_curve_df.reset_index(inplace=True, drop=True)

            #merge_data = pd.merge(weibull_power_curve, actual_power_curve, how='inner', on='windbin')
            gua_power = config_gua_power[config_gua_power['机型']==wt_type]
            gua_power.reset_index(drop=True, inplace=True)
            gua_power = gua_power.rename(columns={'风速': 'windbin'})
            merge_data = pd.merge(gua_power, actual_power_curve, how='inner', on='windbin')
            gen2 = (merge_data['功率'] * merge_data['ratio']).sum() * 8.76
            gen2_list.append(gen2)

            # ratio : 新风频， ws_ratio: 原风频
            gen3 = (merge_data['CI_IprRealPower_mean'] * merge_data['ratio']).sum() * 8.76
            gen3_list.append(gen3)

            wtid_list.append(wtid)
            type_list.append(wt_type)


            # 发电量 -- 十分钟最大值减最小值
            # data['energy'] = data['CI_IprTotalEnergyReal_max'] - data['CI_IprTotalEnergyReal_min']
            # data = data.set_index('time')
            # energy_df = pd.DataFrame(data.resample('M').agg({'energy': 'sum'}))
            # energy_df = energy_df.reset_index(drop=False)
            # energy_df['time'] = energy_df['time'].apply(lambda x: str(x)[0:7])
            # energy_df['wtid'] = wtid
            # energy_all = pd.concat([energy_all, energy_df])

            # plt.figure(figsize=(12, 8), dpi=120)
            # plt.rcParams['axes.unicode_minus'] = False
            # plt.bar(energy_df['time'], energy_df['energy'])
            # setpic('Month', 'Energy')
            # plt.title(wtid + ' Monthly Energy', fontsize=16)
            # plt.tight_layout()
            # # plt.show()
            # result_dir_energy = result_dir + 'energy/'
            # if not os.path.exists(result_dir_energy):
            #     os.makedirs(result_dir_energy)
            # plt.savefig(result_dir_energy + wtid + '_month_energy.png')
            # plt.close()

            # 用全部数据的最大减最小计算的发电量
            energy_total = (data['CI_IprTotalEnergyReal_mean'].max() - data['CI_IprTotalEnergyReal_mean'].min()) / 1000
            energy_year_df = pd.DataFrame({'wtid': [wtid], 'energy': [energy_total]})
            energy_year = pd.concat([energy_year, energy_year_df])
        except Exception as e:
            print(file + e.__class__.__name__, e)

    del_reason_all.set_index('机组编号', inplace=True)
    del_reason_all.to_csv(result_dir + 'del_data/' + 'del_reason.csv')

    # 输出低温高湿异常点数
    result_dir_humidity = result_dir + 'humidity/'
    if not os.path.exists(result_dir_humidity):
        os.makedirs(result_dir_humidity)
    humidity_all.to_csv(result_dir_humidity + '低温高湿点数.csv')

    # 全年风速均值排序图
    ws_year_mean.sort_values(by='ws_year_mean', inplace=True, ascending=False)
    ws_year_mean.to_csv(result_dir+'ws_year_mean.csv')
    plt.figure(figsize=(18, 8), dpi=120)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.bar(ws_year_mean['wtid'], round(ws_year_mean['ws_year_mean'], 2), 0.3, color='b')
    plt.bar_label(fig, label_type='edge')
    plt.axhline(ws_year_mean['ws_year_mean'].mean(), ls='--')
    plt.text(ws_year_mean['wtid'].tolist()[-2], ws_year_mean['ws_year_mean'].mean()+0.1,
             '风速均值=' + str(round(ws_year_mean['ws_year_mean'].mean(),2)), fontsize=14)
    setpic('机组编号', '年平均风速[m/s]')
    plt.title('全场年平均风速排序图', fontsize=16)
    plt.tight_layout()
    plt.savefig(result_dir + 'ws_year_mean.png')


    # 各机组温度变化时序图
    # col_list = ['brown', 'chocolate', 'slategrey', 'navy', 'blueviolet', 'lightpink',
    #             'darkolivegreen', 'lightblue', 'tomato', 'darkseagreen', 'darkorange', 'LightPink']
    # temperature_all = temperature_all.sort_values(by=['wtid', 'time'], ascending=[True, True])
    #
    # plt.figure(figsize=(16, 10), dpi=120)
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # i = 0
    # for id in temperature_all['wtid'].unique().tolist():
    #     temperature_plot = temperature_all[temperature_all['wtid']==id]
    #     plt.plot(temperature_plot['time'], temperature_plot['CI_OutsideAirTemperature_mean'], label=id, alpha=0.7)
    #     i = i + 1
    # plt.legend()
    # #plt.ylim(-40, 40)
    # plt.title('环境温度时序图', fontsize=16)
    # setpic('时间', '环境温度')
    # plt.tight_layout()
    # plt.savefig(result_dir + 'all_temperature.png')
    # temperature_all.to_csv(result_dir + 'all_temperature.csv')
    #
    # # 输出超过100度的情况
    # temperature_all_exceed_100 = temperature_all[temperature_all['CI_OutsideAirTemperature_mean']>100]
    # temperature_all_exceed_100.to_csv(result_dir+'温度超过100的点.csv')



    # 各机组空气密度折线图
    # air_density_all['month'] = air_density_all['time'].astype(str).apply(lambda x: x[0:7])
    # density_month_mean = pd.DataFrame(air_density_all.groupby(['month','wtid'])['air_density'].mean())
    # density_month_mean.reset_index(inplace=True)
    # # 剔除1# 13# 18#
    # density_month_mean = density_month_mean[(density_month_mean['wtid'] != '1#') & (density_month_mean['wtid'] != '13#') &
    #                                         (density_month_mean['wtid'] != '18#')]
    #
    # all_month_mean = pd.DataFrame(density_month_mean.groupby(['month'])['air_density'].mean())
    # all_month_mean.to_csv(result_dir + 'scada_all_month_mean.csv')
    #
    #
    #
    # plt.figure(figsize=(12, 8), dpi=120)
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # i = 0
    # for id in density_month_mean['wtid'].unique().tolist():
    #     density_plot = density_month_mean[density_month_mean['wtid'] == id]
    #     plt.plot(density_plot['month'], density_plot['air_density'], label=id)
    #     i = i + 1
    # plt.legend()
    # plt.title('空气密度折线图')
    # setpic('时间', '空气密度')
    # plt.savefig(result_dir + 'all_density_month_mean.png')

    # 用十分钟最大减最小计算的发电量
    # energy_year = pd.DataFrame(energy_all.groupby('wtid').agg({'energy':'sum'}))
    # energy_year.reset_index(drop=False, inplace=True)
    # energy_year.sort_values(by=['energy'], inplace=True, ascending=False)
    # energy_year.reset_index(drop=True, inplace=True)
    # energy_year['energy'] = energy_year['energy']/1000
    # 用总体最大建最小算发电量作图
    energy_year = energy_year.sort_values(by='energy', ascending=False)
    energy_year.reset_index(drop=True, inplace=True)

    plt.figure(figsize=(20, 8), dpi=120)
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.bar(energy_year['wtid'], energy_year['energy'], width=0.3)
    plt.bar_label(fig, label_type='edge')
    setpic('ID', 'Energy')
    plt.title(' Accumulated Energy', fontsize=16)
    plt.tight_layout()
    result_dir_energy = result_dir + 'energy/'
    if not os.path.exists(result_dir_energy):
        os.makedirs(result_dir_energy)
    plt.savefig(result_dir_energy + 'Accumulated_energy_end-start.png')
    plt.close()
    energy_year.to_csv(result_dir_energy + 'Accumulated_energy_end-start.csv')

    #energy_year.loc['total', 'energy'] = energy_year['energy'].sum()
    #energy_year.to_csv(result_dir_energy + 'energy_year.csv')

    generation['机组编号'] = wtid_list
    generation['机组类型'] = type_list
    #generation['理论发电量'] = gen1_list
    generation['理论应发'] = gen2_list
    generation['实际应发'] = gen3_list
    generation = generation.sort_values(by=['机组类型'])
    #generation['性能损失'] = generation['理论应发'] - generation['实际应发']
    #generation['坐标轴'] = generation['机组编号'] #+ ' (' + generation['机组类型'] + ')'
    generation.reset_index(drop=True, inplace=True)
    generation = round(generation, 1)
    energy_year.columns = ['机组编号', '实际累计发电量']

    generation_merge = pd.merge(generation, energy_year, how='left', on='机组编号')
    # generation_merge['风资源损失发电量'] = generation_merge['理论发电量'] - generation_merge['理论应发'] # 不能计算
    generation_merge['性能损失发电量'] = generation_merge['理论应发'] - generation_merge['实际应发']
    generation_merge['其他损失发电量'] = generation_merge['实际应发'] - generation_merge['实际累计发电量']

    generation_merge.to_csv(result_dir_energy + '发电量分解.csv')


    # 各机组柱状图
    generation_merge = round(generation_merge, 1)
    generation_merge = generation_merge.sort_values(by='理论应发', ascending=False)

    wtid = generation_merge['机组编号'].apply(lambda x: str(x)).tolist()
    shijileiji = generation_merge['实际累计发电量'].tolist()
    xingnengsunshi = generation_merge['性能损失发电量'].tolist()
    qitasunshi = generation_merge['其他损失发电量'].tolist()
    # 设置颜色和标签
    colors = ['#008fd5', '#fc4f30', '#e5ae38']
    labels = ['实际累计发电量', '性能损失发电量', '其他损失发电量']
    # 创建堆叠的柱状图
    plt.figure(figsize=(10, 8), dpi=120)
    fig, ax = plt.subplots()
    ax.bar(wtid, shijileiji, color=colors[0], label=labels[0])
    ax.bar(wtid, xingnengsunshi, bottom=shijileiji, color=colors[1], label=labels[1])
    ax.bar(wtid, qitasunshi, bottom=[i + j for i, j in zip(shijileiji, xingnengsunshi)], color=colors[2],
           label=labels[2])
    # 设置图例和标题
    ax.legend(labels, loc=4)
    ax.set_xlabel('机组编号')
    ax.set_ylabel('发电量（MWh）')
    ax.set_title('各机组发电量柱状图')
    # 设置背景色和边框样式
    ax.set_facecolor('#f7f7f7')
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # 设置刻度线和刻度标签样式
    # ax.tick_params(axis='x', length=0)
    # ax.tick_params(axis='y', length=5, width=1, direction='inout')
    # 调整柱子宽度和间距
    bar_width = 0.3
    ax.set_xticks(np.arange(len(wtid)))
    ax.set_xticklabels(wtid)
    plt.xticks(rotation=0)
    # plt.xlim(-1.5*bar_width, len(wtid)-bar_width/2)

    # 在柱子上标注数字
    for i, v1, v2, v3 in zip(range(len(wtid)), shijileiji, xingnengsunshi, qitasunshi):
        ax.text(i, v1 / 2, str(v1), ha='center', va='center', color='white', fontsize=10, fontweight='bold')
        ax.text(i, v1 + v2 / 2, str(v2), ha='center', va='center', color='white', fontsize=10, fontweight='bold')
        ax.text(i, v1 + v2 + v3 / 2, str(v3), ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    # 调整图形尺寸和布局
    fig.set_size_inches(8, 6)
    fig.tight_layout()

    #plt.show()
    plt.savefig(result_dir_energy + 'energy_bar_plot.png')


    # generation_all = pd.DataFrame(columns=['理论发电量', '风资源损失发电量', '性能损失发电量', '其他损失发电量', '实际累计发电量'])
    # generation_all = pd.DataFrame(
    #     columns=['理论发电量', '风资源损失发电量', '性能损失发电量', '实际应发电量'])

    generation_all = pd.DataFrame(
        columns=['理论应发', '性能损失发电量', '实际应发', '其他损失发电量', '实际累计发电量'])





    # 不含风资源损失和理论发电量
    for id in generation_merge['机组编号'].tolist():
        bar_plot_df = generation_merge[generation_merge['机组编号'] == id]
        type = bar_plot_df['机组类型'].tolist()[0]
        #bar_plot_df = bar_plot_df[['理论发电量', '风资源损失发电量', '性能损失发电量', '其他损失发电量', '实际累计发电量']]
        bar_plot_df = bar_plot_df[['理论应发', '性能损失发电量', '实际应发', '其他损失发电量', '实际累计发电量']]
        bar_plot_df.reset_index(drop=True, inplace=True)
        df2 = pd.DataFrame([0,0,0,0,0]).T
        df2.columns = bar_plot_df.columns
        bar_plot_df = pd.concat([bar_plot_df, df2], ignore_index=True)
        bar_plot_df.iloc[1, 1] = bar_plot_df.iloc[0, 0] - bar_plot_df.iloc[0, 1]
        #bar_plot_df.iloc[1, 2] = bar_plot_df.iloc[1, 1] - bar_plot_df.iloc[0, 2]
        bar_plot_df.iloc[1, 3] = bar_plot_df.iloc[0, 2] - bar_plot_df.iloc[0, 3]
        bar_plot_df.loc[2] = bar_plot_df.apply(lambda x: x.sum())
        bar_plot_df = round(bar_plot_df, 1)
        #bar_plot_df['机组编号'] = id

        # # 含理论发电量
        # generation['机组编号'] = wtid_list
        # generation['机组类型'] = type_list
        # generation['理论发电量'] = gen1_list
        # generation['理论应发'] = gen2_list
        # generation['实际应发'] = gen3_list
        # generation = generation.sort_values(by=['机组类型'])
        # generation['性能损失'] = generation['理论应发'] - generation['实际应发']
        # generation['坐标轴'] = generation['机组编号'] + ' (' + generation['机组类型'] + ')'
        # generation.reset_index(drop=True, inplace=True)
        # generation = round(generation, 1)
        # energy_year.columns = ['机组编号', '实际累计发电量']
        #
        # generation_merge = pd.merge(generation, energy_year, how='left', on='机组编号')
        # generation_merge['风资源损失发电量'] = generation_merge['理论发电量'] - generation_merge['理论应发']
        # generation_merge['性能损失发电量'] = generation_merge['理论应发'] - generation_merge['实际应发']
        # generation_merge['其他损失发电量'] = generation_merge['实际应发'] - generation_merge['实际累计发电量']
        #
        # generation_all = pd.DataFrame(columns=['理论发电量', '风资源损失发电量', '性能损失发电量', '其他损失发电量', '实际累计发电量'])
        # # generation_all = pd.DataFrame(
        # #     columns=['理论发电量', '风资源损失发电量', '性能损失发电量', '实际应发电量'])


        # for id in generation_merge['机组编号'].tolist():
        #     bar_plot_df = generation_merge[generation_merge['机组编号'] == id]
        #     type = bar_plot_df['机组类型'].tolist()[0]
        #     bar_plot_df = bar_plot_df[['理论发电量', '风资源损失发电量', '性能损失发电量', '其他损失发电量', '实际累计发电量']]
        #     bar_plot_df.reset_index(drop=True, inplace=True)
        #     df2 = pd.DataFrame([0,0,0,0,0]).T
        #     df2.columns = bar_plot_df.columns
        #     bar_plot_df = pd.concat([bar_plot_df, df2], ignore_index=True)
        #     bar_plot_df.iloc[1, 1] = bar_plot_df.iloc[0, 0] - bar_plot_df.iloc[0, 1]
        #     bar_plot_df.iloc[1, 2] = bar_plot_df.iloc[1, 1] - bar_plot_df.iloc[0, 2]
        #     bar_plot_df.iloc[1, 3] = bar_plot_df.iloc[1, 2] - bar_plot_df.iloc[0, 3]
        #     bar_plot_df.loc[2] = bar_plot_df.apply(lambda x: x.sum())
        #     bar_plot_df = round(bar_plot_df, 1)

        #     bar_plot_df['机组编号'] = id



        # # 画发电相关柱状图 -- 4柱子
        # bar_plot_new = copy.deepcopy(bar_plot_df)
        # bar_plot_new['实际应发电量'] = bar_plot_new['其他损失发电量'] + bar_plot_new['实际累计发电量']
        # bar_plot_new = bar_plot_new.drop(['其他损失发电量', '实际累计发电量'], axis=1)
        # bar_plot_new.iloc[1,3] = 0
        # bar_plot_new.iloc[2, 3] = bar_plot_new.iloc[0,3]
        # bar_plot_new = round(bar_plot_new, 1)
        # fengziyuan_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,1] / bar_plot_new.iloc[0,0])
        # xingneng_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,2] / bar_plot_new.iloc[0,0])
        # yingfa_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,3] / bar_plot_new.iloc[0,0])
        #
        # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
        # plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
        # plt.figure(figsize=(10, 8), dpi=90)
        # plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[2].tolist()), width=0.3, color=['green', 'red', 'red', 'green'])
        # plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[1].tolist()), width=0.3, color='white')
        # plt.ylim(0, 9000)
        # plt.grid(ls='-.', axis='y')
        # plt.title(id + '  ' + type + '发电情况（MWh）', fontsize=16)
        # plt.text(bar_plot_new.columns.tolist()[0], bar_plot_new.iloc[0,0]+50, bar_plot_new.iloc[0,0], horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[1], bar_plot_new.iloc[1,1]-250, str(bar_plot_new.iloc[0,1])+' ('+str(fengziyuan_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[2], bar_plot_new.iloc[1,2]-250, str(bar_plot_new.iloc[0,2])+' ('+str(xingneng_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[3], bar_plot_new.iloc[0,3]+50, str(bar_plot_new.iloc[0,3])+' ('+str(yingfa_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.axhline(8558, ls='--')
        #
        # result_dir_generation_bar = result_dir + 'generation_bar/'
        # if not os.path.exists(result_dir_generation_bar):
        #     os.makedirs(result_dir_generation_bar)
        # plt.savefig(result_dir_generation_bar + id + '_generation_bar.png', bbox_inches='tight', pad_inches=0.07)
        # plt.close()
        # bar_plot_df.index = [id] * 3
        # generation_all = pd.concat([generation_all, bar_plot_new.iloc[0:1]])

        # #ctrl / 注释
        # 画发电相关柱状图 -- 5柱子
        # bar_plot_new = copy.deepcopy(bar_plot_df)
        # fengziyuan_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,1] / bar_plot_new.iloc[0,0])
        # xingneng_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,2] / bar_plot_new.iloc[0,0])
        # other_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,3] / bar_plot_new.iloc[0,0])
        # shijileiji_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,4] / bar_plot_new.iloc[0,0])
        #
        # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
        # plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
        # plt.figure(figsize=(10, 8), dpi=90)
        # plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[2].tolist()), width=0.3, color=['green', 'red', 'red', 'red', 'green'])
        # plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[1].tolist()), width=0.3, color='white')
        # plt.ylim(0, 9000)
        # plt.grid(ls='-.', axis='y')
        # plt.title(id + '  ' + type + ' 发电情况（MWh）', fontsize=18)
        # plt.text(bar_plot_new.columns.tolist()[0], bar_plot_new.iloc[0,0]+50, bar_plot_new.iloc[0,0], horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[1], bar_plot_new.iloc[1,1]-250, str(bar_plot_new.iloc[0,1])+' ('+str(fengziyuan_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[2], bar_plot_new.iloc[1,2]-250, str(bar_plot_new.iloc[0,2])+' ('+str(xingneng_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[3], bar_plot_new.iloc[1,3]-250, str(bar_plot_new.iloc[0,3])+' ('+str(other_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.text(bar_plot_new.columns.tolist()[4], bar_plot_new.iloc[0,4]+50, str(bar_plot_new.iloc[0,4])+' ('+str(shijileiji_ratio)+')', horizontalalignment='center', weight='bold')
        # plt.axhline(8558, ls='--')



        bar_plot_new = copy.deepcopy(bar_plot_df)
        xingneng_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,1] / bar_plot_new.iloc[0,0])
        yingfa_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,2] / bar_plot_new.iloc[0,0])
        other_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,3] / bar_plot_new.iloc[0,0])
        shijileiji_ratio = '{:.1%}'.format(bar_plot_new.iloc[0,4] / bar_plot_new.iloc[0,0])

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
        plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
        plt.figure(figsize=(10, 8), dpi=90)
        plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[2].tolist()), width=0.3, color=['green', 'red', 'green', 'red', 'green'])
        plt.bar(np.array(bar_plot_new.columns.tolist()), np.array(bar_plot_new.loc[1].tolist()), width=0.3, color='white')
        #plt.ylim(0, 9000)
        plt.grid(ls='-.', axis='y')
        plt.title(id + '  ' + type + ' 发电情况（MWh）', fontsize=18)
        plt.text(bar_plot_new.columns.tolist()[0], bar_plot_new.iloc[0,0]+30, bar_plot_new.iloc[0,0], horizontalalignment='center', weight='bold')
        plt.text(bar_plot_new.columns.tolist()[1], bar_plot_new.iloc[1,1]-70, str(bar_plot_new.iloc[0,1])+' ('+str(xingneng_ratio)+')', horizontalalignment='center', weight='bold')
        plt.text(bar_plot_new.columns.tolist()[2], bar_plot_new.iloc[0,2]+30, str(bar_plot_new.iloc[0,2])+' ('+str(yingfa_ratio)+')', horizontalalignment='center', weight='bold')
        plt.text(bar_plot_new.columns.tolist()[3], bar_plot_new.iloc[1,3]-70, str(bar_plot_new.iloc[0,3])+' ('+str(other_ratio)+')', horizontalalignment='center', weight='bold')
        plt.text(bar_plot_new.columns.tolist()[4], bar_plot_new.iloc[0,4]+30, str(bar_plot_new.iloc[0,4])+' ('+str(shijileiji_ratio)+')', horizontalalignment='center', weight='bold')

        result_dir_generation_bar = result_dir + 'generation_bar/'
        if not os.path.exists(result_dir_generation_bar):
            os.makedirs(result_dir_generation_bar)
        plt.savefig(result_dir_generation_bar + id + '_generation_bar.png', bbox_inches='tight', pad_inches=0.07)
        plt.close()
        bar_plot_df.index = [id] * 3
        generation_all = pd.concat([generation_all, bar_plot_df.iloc[0:1]])

    generation_all.to_csv(result_dir_generation_bar + '各机组发电情况.csv')

    # 总发电量
    generation_all_sum = generation_all.apply(lambda x: x.sum())
    generation_all_sum = pd.DataFrame(generation_all_sum).T
    generation_all_sum.to_csv(result_dir_generation_bar + '全部机组发电情况.csv')

    df2 = pd.DataFrame([0, 0, 0, 0, 0]).T
    #df2 = pd.DataFrame([0, 0, 0, 0]).T
    df2.columns = generation_all_sum.columns
    generation_all_sum = pd.concat([generation_all_sum, df2], ignore_index=True)
    generation_all_sum.iloc[1, 1] = generation_all_sum.iloc[0, 0] - generation_all_sum.iloc[0, 1]
    #generation_all_sum.iloc[1, 2] = generation_all_sum.iloc[1, 1] - generation_all_sum.iloc[0, 2]
    generation_all_sum.iloc[1, 3] = generation_all_sum.iloc[0, 2] - generation_all_sum.iloc[0, 3]
    generation_all_sum.loc[2] = generation_all_sum.apply(lambda x: x.sum())
    generation_all_sum = round(generation_all_sum, 1)

    xingneng_ratio = '{:.1%}'.format(generation_all_sum.iloc[0, 1] / generation_all_sum.iloc[0, 0])
    yingfa_ratio = '{:.1%}'.format(generation_all_sum.iloc[0, 2] / generation_all_sum.iloc[0, 0])
    other_ratio = '{:.1%}'.format(generation_all_sum.iloc[0, 3] / generation_all_sum.iloc[0, 0])
    shijileiji_ratio = '{:.1%}'.format(generation_all_sum.iloc[0, 4] / generation_all_sum.iloc[0, 0])


    # 画总发电相关柱状图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    plt.figure(figsize=(10, 8), dpi=90)
    plt.bar(np.array(generation_all_sum.columns.tolist()), np.array(generation_all_sum.loc[2].tolist()), width=0.3,
            color=['green', 'red', 'green', 'red','green'])
    plt.bar(np.array(generation_all_sum.columns.tolist()), np.array(generation_all_sum.loc[1].tolist()), width=0.3, color='white')
    plt.grid(ls='-.', axis='y')
    plt.title('全部机组发电情况（MWh）', fontsize=16)
    plt.text(generation_all_sum.columns.tolist()[0], generation_all_sum.iloc[0, 0] + 200, generation_all_sum.iloc[0, 0],
             horizontalalignment='center', weight='bold')
    plt.text(generation_all_sum.columns.tolist()[1], generation_all_sum.iloc[1, 1] - 500, str(generation_all_sum.iloc[0, 1])+' ('+xingneng_ratio+')',
             horizontalalignment='center', weight='bold')
    plt.text(generation_all_sum.columns.tolist()[2], generation_all_sum.iloc[0, 2] + 200, str(generation_all_sum.iloc[0, 2])+' ('+yingfa_ratio+')',
             horizontalalignment='center', weight='bold')
    plt.text(generation_all_sum.columns.tolist()[3], generation_all_sum.iloc[1, 3] - 500, str(generation_all_sum.iloc[0, 3])+' ('+other_ratio+')',
             horizontalalignment='center', weight='bold')
    plt.text(generation_all_sum.columns.tolist()[4], generation_all_sum.iloc[0, 4] + 200, str(generation_all_sum.iloc[0, 4]) + ' (' + shijileiji_ratio + ')',
             horizontalalignment='center', weight='bold')


    # plt.text(generation_all_sum.columns.tolist()[3], generation_all_sum.iloc[1, 3] - 200, generation_all_sum.iloc[0, 3],
    #          horizontalalignment='center', weight='bold')
    # plt.text(generation_all_sum.columns.tolist()[4], generation_all_sum.iloc[0, 4] + 20, generation_all_sum.iloc[0, 4],
    #          horizontalalignment='center', weight='bold')

    result_dir_generation_bar = result_dir + 'generation_bar/'
    if not os.path.exists(result_dir_generation_bar):
        os.makedirs(result_dir_generation_bar)
    plt.savefig(result_dir_generation_bar + 'all_generation_bar.png', bbox_inches='tight', pad_inches=0.07)
    plt.close()


    #generation.to_csv(result_dir + 'generation.csv')
    #generation_sum.to_csv(result_dir + 'generation_sum.csv')

    # 发电量和性能损失柱状图
    # #generation = generation.drop(index=[12,19])
    # plt.rcParams['font.sans-serif']=['SimHei']   # 用黑体显示中文
    # plt.rcParams['axes.unicode_minus']=False     # 正常显示负号
    # plt.figure(figsize=(14, 8), dpi=200)
    # plt.subplots_adjust(wspace=0, hspace=0)
    # plt.bar(generation['坐标轴'],generation['实际应发'], width=0.3,color='blue', label='实际应发')
    # for a,b in zip(generation['坐标轴'],generation['实际应发']):
    #     plt.text(a, b, b)
    # plt.bar(generation['坐标轴'],generation['性能损失'], width=0.3,color='orange', label='性能损失')
    # for c,d in zip(generation['坐标轴'],generation['性能损失']):
    #     plt.text(c, d, d)
    # plt.legend()
    # plt.grid(ls='-.', axis='y')
    # plt.xlabel('ID', fontsize=10)
    # plt.ylabel('Power Generation', fontsize=10)
    # plt.title('Power Generation', fontsize=14)
    # plt.xticks(rotation=30)
    # plt.tight_layout()
    # #plt.savefig(result_dir + 'generation_bar.png')  #先不出了
    #
    # plt.close()

    # 同机型功率曲线

    for type in power_curve_df['wt_type'].unique().tolist():
        plt.figure(figsize=(18, 14), dpi=100)
        for wtid in power_curve_df['wtid'].unique().tolist():
            plot_data = power_curve_df[(power_curve_df['wt_type'] == type) & (power_curve_df['wtid'] == wtid)]
            plot_data.reset_index(inplace=True, drop=True)
            plt.plot(plot_data['windbin'], plot_data['CI_IprRealPower_mean'], label=wtid)
            plt.legend()
            #sns.pointplot(x='windbin', y='CI_IprRealPower_mean', hue='wtid', data=plot_data, linestyles='-', markers='o')
        plt.grid()
        setpic('Wind Speed', 'Power')
        y_major_locator = MultipleLocator(200)
        ax = plt.gca()
        ax.yaxis.set_major_locator(y_major_locator)
        plt.title(type + ' Power Curve', fontsize=18)
        plt.tight_layout()
        #plt.show()
        result_dir_pcp = result_dir + 'power_curve_plot_2/'
        if not os.path.exists(result_dir_pcp):
            os.makedirs(result_dir_pcp)
        plt.savefig(result_dir_pcp + type + '_power_curve_plot.png')
    power_curve_df.to_csv(result_dir_pcp + 'power_curve.csv')


    # 可用占比
    usable_ratio['wtid'] = wtid_list
    usable_ratio['type'] = type_list
    usable_ratio['usable_ratio'] = usable_list
    usable_ratio_mean = usable_ratio.mean()
    usable_ratio.to_csv(result_dir + 'usable_ratio.csv')
    usable_ratio_mean.to_csv(result_dir + 'usable_ratio_mean.csv')



if __name__ == '__main__':
    pdir = r'E:\08-娑婆风电场\05-计算结果\合并10分钟数据-批量\\'
    result_dir = r'E:\08-娑婆风电场\05-计算结果\SCADA结果-全\SCADA结果\\'
    pdir_config = r'E:\08-娑婆风电场\config\\'
    tower_config = r'E:\08-娑婆风电场\05-计算结果\测风塔结果\2022\\'
    #config_density = pd.read_csv(pdir_config + '空气密度.csv', encoding='gbk')
    config_tower_10min = pd.read_csv(tower_config + '10_min_mean_tower.csv', index_col=0)
    config_tower_10min.columns = ['时间', '压强', '风向', '风速', '温度', '湿度']
    # 压强有突变，海拔计算空气密度  2170m

    config_tower_10min['空气密度'] = (353.05 / (config_tower_10min['温度'] + 273.15)) * \
                                       np.exp(-0.034 * (2170 / (config_tower_10min['温度'] + 273.15)))
    #config_density_10min['空气密度'] = 100 * config_density_10min['压强'] / (287.05 * (config_density_10min['温度'] + 273.15))
    # 匹配十分钟空气密度
    config_density_10min = config_tower_10min[['时间', '空气密度']]
    config_density_10min.columns = ['time', 'air_density_10min']
    config_density_10min['time'] = pd.to_datetime(config_density_10min['time'])

    tower_humidity = config_tower_10min[['时间', '湿度']]
    tower_humidity = tower_humidity.rename(columns={'时间': 'time'})
    tower_humidity['time'] = pd.to_datetime(tower_humidity['time'])

    # config_tower = pd.read_csv(tower_config + '10_min_mean_tower.csv', index_col=0)
    # config_tower.columns = ['时间', '压强', '风向', '风速', '温度', '湿度']
    config_id = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='机组号')
    config_gua_power = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='担保功率曲线')
    config_info = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='机组信息表')
    #config_keyan = pd.read_excel(pdir_config + '可研理论发电量.xlsx')
    config_IEC = pd.read_csv(pdir_config + 'IEC.csv', encoding='gbk')
    dataProcess(pdir, result_dir)
    # #
    # pdir = r'D:\重庆回山坪项目\3.合并10分钟结果\\'
    # result_dir = r'D:\重庆回山坪项目\结果4\\'
    # pdir_config = r'D:\重庆回山坪项目\config\\'
    # tower_config = r'E:\重庆回山坪项目\4.测风塔结果\\'
    # config_density = pd.read_excel(pdir_config + '空气密度.xlsx')
    # #config_density = pd.read_csv(tower_config + '10_min_mean_tower.csv', index_col=0)
    # #config_tower = pd.read_csv(tower_config + '10_min_mean_tower.csv', index_col=0)
    # config_id = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='机组号')
    # config_gua_power = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='担保功率曲线')
    # config_info = pd.read_excel(pdir_config + 'config.xlsx', sheet_name='机组信息表')
    # config_keyan = pd.read_excel(pdir_config + '可研理论发电量.xlsx')
    # config_IEC = pd.read_csv(pdir_config + 'IEC.csv', encoding='gbk')
    # dataProcess(pdir, result_dir)