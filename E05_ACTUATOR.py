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
    db_name = "D:/Log/00000002.db"

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

    data = log.getData("RATE","TimeUS","RDes","R","ROut","PDes","P","POut","YDes","Y","YOut","ADes","A","AOut","AOutSlew")
    rate_timeus = data[0]
    rate_rdes = data[1]
    rate_r = data[2]
    rate_rout = data[3]
    rate_pdes = data[4]
    rate_p = data[5]
    rate_pout = data[6]
    rate_ydes = data[7]
    rate_y = data[8]
    rate_yout = data[9]
    rate_ades = data[10]
    rate_a = data[11]
    rate_aout = data[12]
    rate_aoutslew = data[13]

    data = log.getData("RCOU","TimeUS","C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12","C13","C14")
    rcou_timeus = data[0]
    rcou_c1 = data[1]
    rcou_c2 = data[2]
    rcou_c3 = data[3]
    rcou_c4 = data[4]
    rcou_c5 = data[5]
    rcou_c6 = data[6]
    rcou_c7 = data[7]
    rcou_c8 = data[8]
    rcou_c9 = data[9]
    rcou_c10 = data[10]
    rcou_c11 = data[11]
    rcou_c12 = data[12]
    rcou_c13 = data[13]
    rcou_c14 = data[14]

except Exception as e:
    print(f"Error: Problem reading data - {e}")
    sys.exit(1)

# 依上面取得的数据通过 matplotlib 绘图
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 绘图布局
fig  = plt.figure(figsize=(16, 9), dpi=1920/16)
gs   = gridspec.GridSpec(nrows=2, ncols=3, left=0.03, right=0.97, wspace=0.12)
# 左上图
ax1  = fig.add_subplot(gs[0,0])
ax1.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax1.grid(ls="--",lw=0.3)
# 中上图
ax2  = fig.add_subplot(gs[0,1])
ax2.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax2.grid(ls="--",lw=0.3)
# 右上图
ax3  = fig.add_subplot(gs[0,2])
ax3.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax3.grid(ls="--",lw=0.3)
# 左下图
ax4  = fig.add_subplot(gs[1,0])
ax4.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax4.grid(ls="--",lw=0.3)
# 中下图
ax5  = fig.add_subplot(gs[1,1])
ax5.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax5.grid(ls="--",lw=0.3)
# 右下图
ax6  = fig.add_subplot(gs[1,2])
ax6.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
ax6.grid(ls="--",lw=0.3)

ax2.plot(pidr_timeus,
         pidr_tar,
         label="PIDR.Tar",
         marker = '',
         markersize = 1.5,
         linestyle="--",
         linewidth=0.6)
ax2.plot(pidr_timeus,
         pidr_act,
         label="PIDR.Act",
         marker = '',
         markersize = 1.5,
         linestyle="--",
         linewidth=0.6)
ax2.plot(pidp_timeus,
         pidp_tar,
         label="PIDP.Tar",
         marker = '.',
         markersize = 1.5,
         linestyle=":",
         linewidth=0.6)
ax2.plot(pidp_timeus,
         pidp_act,
         label="PIDP.Act",
         marker = '.',
         markersize = 1.5,
         linestyle=":",
         linewidth=0.6)
ax2.legend()

ax3.plot(rate_timeus,
         rate_rout,
         label="RATE.ROut",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax3.plot(rate_timeus,
         rate_pout,
         label="RATE.POut",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax3.plot(rate_timeus,
         rate_yout,
         label="RATE.YOut",
         marker = '.',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax3.plot(rate_timeus,
         rate_aout,
         label="RATE.AOut",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax3.legend()

ax1.plot(ang_timeus,
         ang_desroll,
         label="ANG.DesRoll",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax1.plot(ang_timeus,
         ang_roll,
         label="ANG.Roll",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax1.plot(ang_timeus,
         ang_despitch,
         label="ANG.DesPitch",
         marker = '',
         markersize = 1.5,
         linestyle="--",
         linewidth=0.6)
ax1.plot(ang_timeus,
         ang_pitch,
         label="ANG.Pitch",
         marker = '.',
         markersize = 1.5,
         linestyle="--",
         linewidth=0.6)
ax1.legend()

ax5.plot(pidy_timeus,
         pidy_tar,
         label="PIDY.Tar",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax5.plot(pidy_timeus,
         pidy_act,
         label="PIDY.Act",
         marker = '.',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax5.legend()

ax6.plot(rcou_timeus,
         rcou_c1,
         label="RCOU.C1",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax6.plot(rcou_timeus,
         rcou_c2,
         label="RCOU.C2",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax6.plot(rcou_timeus,
         rcou_c3,
         label="RCOU.C3",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax6.plot(rcou_timeus,
         rcou_c4,
         label="RCOU.C4",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax6.legend()

ax4.plot(ang_timeus,
         ang_desyaw,
         label="ANG.DesYaw",
         marker = '',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax4.plot(ang_timeus,
         ang_yaw,
         label="ANG.Yaw",
         marker = '.',
         markersize = 1.5,
         linestyle="-",
         linewidth=0.6)
ax4.legend()

# 图形交互
PT_X    = ang_timeus
axd     = ax1

# 找最近值的索引
from utilities.utilities import find_closest_idx,find_closest_value

def on_press(event):
    global PT_X
    global axd, ax1, ax2, ax3, ax4, ax5, ax6

    if event.button==3: #鼠标右键点击
        idx = find_closest_idx(PT_X,event.xdata)
        xmin,xmax = axd.get_xlim()
        ymin,ymax = axd.get_ylim()
        axd.tick_params(axis='x',colors='red')
        axd.tick_params(axis='y',colors='red')
        axd.set_title("TimeUS: %d\n(Zoom this one.)"%(PT_X[idx]))
        axd.set_xlim(xmin,xmax)
        axd.set_ylim(ymin,ymax)

        ax = [ax1,ax2,ax3,ax4,ax5,ax6]
        for i in range(0,6):
            ymin,ymax = ax[i].get_ylim()
            ax[i].plot([PT_X[idx],PT_X[idx]],[ymin,ymax],
                       linestyle="--",
                       linewidth=0.5,
                       color="r")
            ax[i].set_ylim(ymin,ymax)
        plt.draw()

def button_release(event):
    global axd,ax1,ax2,ax3,ax4,ax5,ax6

    ax = [ax1,ax2,ax3,ax4,ax5,ax6]
    if event.button == 1:
        xmin, xmax = axd.get_xlim()
        for i in range(0,6):
            if axd != ax[i]:
                ax[i].set_xlim(xmin,xmax)

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', button_release)

plt.show()