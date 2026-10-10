#!/usr/bin/python3
# -*- coding:utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from utilities.LogDBParser import LogDBParser
import platform
import matplotlib

# Check if running on Linux
if platform.system() == 'Linux':
    try:
        matplotlib.use('TkAgg')
    except ImportError:
        print("sudo apt-get install python3-tk")
        # Fallback to default backend
        pass

# Handle command line arguments
if len(sys.argv) > 1:
    db_name = sys.argv[1]
else:
    db_name = "D:/Log/00000009.db"

# Cross-platform path handling
db_path = os.path.join('..', db_name)

# Check if file exists
if not os.path.exists(db_path):
    print(f"Error: Database file not found: {db_path}")
    sys.exit(1)

log = LogDBParser(db_path)

try:
    data = log.getData("ANG","TimeUS","DesRoll","Roll","DesPitch","Pitch","DesYaw","Yaw","Dt")
    ang_timeus = data[0]
    ang_desroll = data[1]
    ang_roll = data[2]
    ang_despitch = data[3]
    ang_pitch = data[4]
    ang_desyaw = data[5]
    ang_yaw = data[6]
    ang_dt = data[7]

    data = log.getData("PARM","TimeUS","Name","Value","Default")
    parm_timeus = data[0]
    parm_name = data[1]
    parm_value = data[2]
    parm_default = data[3]

    data = log.getData("PIDP","TimeUS","Tar","Act","Err","P","I","D","FF","DFF","Dmod","SRate","Flags")
    pidp_timeus = data[0]
    pidp_tar = data[1]
    pidp_act = data[2]
    pidp_err = data[3]
    pidp_p = data[4]
    pidp_i = data[5]
    pidp_d = data[6]
    pidp_ff = data[7]
    pidp_dff = data[8]
    pidp_dmod = data[9]
    pidp_srate = data[10]
    pidp_flags = data[11]

    data = log.getData("PIDR","TimeUS","Tar","Act","Err","P","I","D","FF","DFF","Dmod","SRate","Flags")
    pidr_timeus = data[0]
    pidr_tar = data[1]
    pidr_act = data[2]
    pidr_err = data[3]
    pidr_p = data[4]
    pidr_i = data[5]
    pidr_d = data[6]
    pidr_ff = data[7]
    pidr_dff = data[8]
    pidr_dmod = data[9]
    pidr_srate = data[10]
    pidr_flags = data[11]

    data = log.getData("PIDY","TimeUS","Tar","Act","Err","P","I","D","FF","DFF","Dmod","SRate","Flags")
    pidy_timeus = data[0]
    pidy_tar = data[1]
    pidy_act = data[2]
    pidy_err = data[3]
    pidy_p = data[4]
    pidy_i = data[5]
    pidy_d = data[6]
    pidy_ff = data[7]
    pidy_dff = data[8]
    pidy_dmod = data[9]
    pidy_srate = data[10]
    pidy_flags = data[11]

except Exception as e:
    print(f"Error: Problem reading data - {e}")
    sys.exit(1)

# 建立参数字典，字典形举例如下：
# {'Q_M_THST_HOVER'：[{3035145: 0.408207}, {51787417: 0.408207}, {271065946: 0.421976}]}
parms = {}
for i in range(len(parm_timeus)):
    if parms.get(parm_name[i]) == None:
        parms[parm_name[i]]=[{parm_timeus[i]:parm_value[i]}]
    else:
        parms.get(parm_name[i]).append({parm_timeus[i]:parm_value[i]})

# 查找一个参数
# 例：get_parm('Q_M_THST_HOVER')
def get_parm(name):
    if parms.get(name) is not None:
        t = [] # 时间 TimeUS
        v = [] # 值
        for i in range(len(parms.get(name))):
            element = parms.get(name)[i]
            t.append(int(list(element.keys())[0]))
            v.append(float(list(element.values())[0]))
        return (t,v)

class PARM:
    def __init__(self,name):
        self.name = name
        self.t,self.v = get_parm(name)

# Roll
ATC_ANG_RLL_P     = PARM('ATC_ANG_RLL_P')
ATC_ACC_R_MAX     = PARM('ATC_ACC_R_MAX')
ATC_RAT_RLL_NTF   = PARM('ATC_RAT_RLL_NTF')
ATC_RAT_RLL_FLTT  = PARM('ATC_RAT_RLL_FLTT')
ATC_RAT_RLL_NEF   = PARM('ATC_RAT_RLL_NEF')
ATC_RAT_RLL_FF    = PARM('ATC_RAT_RLL_FF')
ATC_RAT_RLL_D_FF  = PARM('ATC_RAT_RLL_D_FF')
ATC_RAT_RLL_FLTE  = PARM('ATC_RAT_RLL_FLTE')
ATC_RAT_RLL_P     = PARM('ATC_RAT_RLL_P')
ATC_RAT_RLL_I     = PARM('ATC_RAT_RLL_I')
ATC_RAT_RLL_D     = PARM('ATC_RAT_RLL_D')
ATC_RAT_RLL_IMAX  = PARM('ATC_RAT_RLL_IMAX')
ATC_RAT_RLL_FLTD  = PARM('ATC_RAT_RLL_FLTD')
ATC_RAT_RLL_SMAX  = PARM('ATC_RAT_RLL_SMAX')
ATC_RAT_RLL_PDMX  = PARM('ATC_RAT_RLL_PDMX')
#Pitch
ATC_ANG_PIT_P     = PARM('ATC_ANG_PIT_P')
ATC_ACC_P_MAX     = PARM('ATC_ACC_P_MAX')
ATC_RAT_PIT_NTF   = PARM('ATC_RAT_PIT_NTF')
ATC_RAT_PIT_FLTT  = PARM('ATC_RAT_PIT_FLTT')
ATC_RAT_PIT_NEF   = PARM('ATC_RAT_PIT_NEF')
ATC_RAT_PIT_FF    = PARM('ATC_RAT_PIT_FF')
ATC_RAT_PIT_D_FF  = PARM('ATC_RAT_PIT_D_FF')
ATC_RAT_PIT_FLTE  = PARM('ATC_RAT_PIT_FLTE')
ATC_RAT_PIT_P     = PARM('ATC_RAT_PIT_P')
ATC_RAT_PIT_I     = PARM('ATC_RAT_PIT_I')
ATC_RAT_PIT_D     = PARM('ATC_RAT_PIT_D')
ATC_RAT_PIT_IMAX  = PARM('ATC_RAT_PIT_IMAX')
ATC_RAT_PIT_FLTD  = PARM('ATC_RAT_PIT_FLTD')
ATC_RAT_PIT_SMAX  = PARM('ATC_RAT_PIT_SMAX')
ATC_RAT_PIT_PDMX  = PARM('ATC_RAT_PIT_PDMX')

sys.path.append('./utilities')
from MathCommon import *

def annotate_parm(axd, parm):
    print(parm.name)
    print('=====================')
    print("idx\ttimeus\t\tvalue")
    print('---------------------')
    t = parm.t
    v = parm.v
    tl = [0]
    cnt = 0
    for i in range(len(t)):
        xmin,xmax = axd.get_xlim()
        ymin,ymax = axd.get_ylim()
        if t[i] - tl[-1] > 2000:
            tl.append(t[i])
            cnt += 1
            print("%d\t%d\t%.3f"%(cnt,t[i],v[i]))
            c='b'
            off_y     = 0
            offy_step = (ymax-ymin)/30
            offx_step = (xmax-xmin)/250
            dff = parm.name.split('_')[-2]
            if dff == 'D':
                s = 'DFF'
                c='blueviolet'
            else:
                s = parm.name.split('_')[-1]
                if s == 'I':
                    c='sienna'
                    off_y += offy_step * 3
                elif s == 'D':
                    c='magenta'
                    off_y += offy_step * 2
                elif s == 'FF':
                    c='blueviolet'
                    off_y += offy_step * 1
                else:
                    if s == 'P':
                        off_y += offy_step * 4
            axd.plot([t[i],t[i]],[ymin,ymax],
                     marker = '',
                     markersize = 2,
                     linestyle="--",
                     linewidth=0.8,
                     color=c)
            axd.set_ylim(ymin,ymax)

            axd.text(t[i]+offx_step,ymin+off_y, r'%s=%.3f'%(s,v[i]), color=c, fontsize=8)
    print()

# 找最近值的索引
def find_closest_idx(lst, value):
    array = np.asarray(lst)
    idx = (np.abs(array - value)).argmin()
    return idx

# 依上面取得的数据通过 matplotlib 绘图
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 绘制一个通道(Roll/Pitch)的角度 P 与角速率 PID 图
def plot_ang_p_pr(pid_label, chan,
                  pid_timeus, pid_tar, pid_act, pid_p, pid_i, pid_d, pid_ff, pid_dff, pid_dmod,
                  ang_timeus, ang_des, ang_act,
                  P, I, D, FF, DFF, ANG_P, ACC_MAX):
    # sqrt_controller 输入输出曲线
    tar = np.array(ang_des)
    act = np.array(ang_act)
    err = list(tar-act)
    max_err_in_deg = max(abs(max(err)),abs(min(err)))

    ATC_ACC_MAX     = np.deg2rad(ACC_MAX.v[-1])
    Q_A_ANG_XXX_P   = ANG_P.v[-1]
    max_err_in_rad  = np.deg2rad(max_err_in_deg)
    RP_MIN_RADSS    = np.deg2rad(40)
    RP_MAX_RADSS    = np.deg2rad(720)

    input_list = np.linspace(-max_err_in_rad,max_err_in_rad,int(np.ceil(max_err_in_rad))*50+1)
    input_list = np.around(input_list,5)
    input_list = list(input_list)
    results    = []
    for i in input_list:
        second_ord_lim = constrain_float(ATC_ACC_MAX/2,RP_MIN_RADSS,RP_MAX_RADSS)
        res = sqrt_controller(i, Q_A_ANG_XXX_P, second_ord_lim, 0.0025)
        results.append(res)

    input_list = np.rad2deg(input_list)
    results    = np.rad2deg(results)

    # 绘图布局
    fig  = plt.figure(figsize=(16, 9), dpi=1920/16)
    gs   = gridspec.GridSpec(nrows=2, ncols=3, left=0.03, right=0.98, wspace=0.12)
    # 左图
    axc  = fig.add_subplot(gs[:,:-1])
    axc.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
    axc.grid(ls="--",lw=0.3)
    # 右下图
    axp  = fig.add_subplot(gs[1,-1])
    axp.ticklabel_format(style='plain', scilimits=(0,1), axis='both')
    axp.grid(ls="--",lw=0.3)
    # 右上图
    axu  = fig.add_subplot(gs[0,-1])
    axu.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
    axu.grid(ls="--",lw=0.3)

    axc.plot(pid_timeus,
             pid_tar,
             label="%s.Tar"%(pid_label),
             marker = '',
             linestyle="-")
    axc.plot(pid_timeus,
             pid_act,
             label="%s.Act"%(pid_label),
             marker = '',
             linestyle="-")
    axc.plot(pid_timeus,
             pid_dmod,
             label="%s.Dmod"%(pid_label),
             marker = '.',
             linestyle=":")
    axc.legend()
    title_str  = "%s = %.3f"%(P.name,P.v[-1])
    title_str += "    "
    title_str += "%s = %.3f"%(I.name,I.v[-1])
    title_str += "\n"
    title_str += "%s = %.3f"%(D.name,D.v[-1])
    title_str += "    "
    title_str += "%s = %.3f"%(FF.name,FF.v[-1])
    title_str += "\n"
    title_str += "%s = %.3f"%(DFF.name,DFF.v[-1])
    axc.set_title(title_str)

    axu.plot(ang_timeus,
             ang_des,
             label="ANG.Des%s"%(chan),
             marker = '',
             linestyle="-")
    axu.plot(ang_timeus,
             ang_act,
             label="ANG.%s"%(chan),
             marker = '',
             linestyle="-")
    axu.legend()
    axu.set_title('%s = %.2f'%(ANG_P.name,Q_A_ANG_XXX_P))

    axp.plot(input_list,input_list,
             marker = '',
             linestyle = '--')
    axp.plot(input_list,results,
             marker = '.',
             linestyle = ':')
    axp.set_title('%s = %d'%(ACC_MAX.name,ACC_MAX.v[-1]))
    miloc = plt.MultipleLocator(2.5)
    axp.xaxis.set_minor_locator(miloc)
    axp.yaxis.set_minor_locator(miloc)
    axp.grid(linestyle='--',which='minor',lw=0.3)
    axp.set_aspect('equal', adjustable='box')
    xylim = max(max(axp.get_xlim()),max(axp.get_ylim()))
    axp.set_xlim(-xylim,xylim)

    annotate_parm(axc, P)
    annotate_parm(axc, I)
    annotate_parm(axc, D)
    annotate_parm(axc, FF)
    annotate_parm(axc, DFF)

    # 图形交互
    PT_X    = ang_timeus
    axd     = axc
    Main_ax = axu
    Main_X  = ang_timeus

    def on_press(event):
        if event.button==3: #鼠标右键点击
            idx = find_closest_idx(PT_X,event.xdata)
            xmin,xmax = axd.get_xlim()
            ymin,ymax = axd.get_ylim()
            axd.plot([PT_X[idx],PT_X[idx]],[ymin,ymax],
                     linestyle="--",
                     linewidth=0.5,
                     color="r")
            axd.tick_params(axis='x',colors='red')
            axd.tick_params(axis='y',colors='red')
            axd.set_xlim(xmin,xmax)
            axd.set_ylim(ymin,ymax)

            idx = find_closest_idx(Main_X,event.xdata)
            xmin,xmax = Main_ax.get_xlim()
            ymin,ymax = Main_ax.get_ylim()
            Main_ax.plot([Main_X[idx],Main_X[idx]],[ymin,ymax],
                          linestyle="--",
                          linewidth=0.5,
                          color="r")
            Main_ax.set_xlim(xmin,xmax)
            Main_ax.set_ylim(ymin,ymax)

            plt.draw()

    def button_release(event):
        if event.button == 1:
            xmin, xmax = axd.get_xlim()
            ax = [axu,axc]
            for i in range(0,2):
                if axd != ax[i]:
                    ax[i].set_xlim(xmin,xmax)

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', button_release)

# Roll
plot_ang_p_pr("PIDR","Roll",
              pidr_timeus, pidr_tar, pidr_act, pidr_p, pidr_i, pidr_d, pidr_ff, pidr_dff, pidr_dmod,
              ang_timeus, ang_desroll, ang_roll,
              ATC_RAT_RLL_P, ATC_RAT_RLL_I, ATC_RAT_RLL_D, ATC_RAT_RLL_FF, ATC_RAT_RLL_D_FF,
              ATC_ANG_RLL_P, ATC_ACC_R_MAX)

# Pitch
plot_ang_p_pr("PIDP","Pitch",
              pidp_timeus, pidp_tar, pidp_act, pidp_p, pidp_i, pidp_d, pidp_ff, pidp_dff, pidp_dmod,
              ang_timeus, ang_despitch, ang_pitch,
              ATC_RAT_PIT_P, ATC_RAT_PIT_I, ATC_RAT_PIT_D, ATC_RAT_PIT_FF, ATC_RAT_PIT_D_FF,
              ATC_ANG_PIT_P, ATC_ACC_P_MAX)

plt.show()
