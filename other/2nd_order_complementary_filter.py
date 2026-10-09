#!/usr/bin/python3
# -*- coding:utf-8 -*-
import numpy as np
from scipy.misc import derivative
from SecondOrderComplementaryFilter import SecondOrderComplementaryFilter

def f(x):
    return np.sin(x)

loop = 5
n = loop*100

t = np.linspace(0,loop*2*np.pi,n)
y=f(t)

dy = np.empty(n)
for i in range(n):
    dy[i] = derivative(f,t[i],dx=loop*2*np.pi/(n-1))

# 给输入加入噪声
# 使用 numpy.random.uniform(下界, 上界, size=(行数, 列数))
A = 0.3
noise = np.random.uniform(-A,A,size=(len(t)))
y_noise = y + noise

# 给 dy 加噪声
A2 = 0.5
noise2 = np.random.uniform(-A2,A2,size=(len(t)))
dy_noise = dy + noise2

SPD_OMEGA = 2
# 在这里设置不同的 dt，以了解采样频率对滤波效果的影响
dt = 0.1

# 对噪声信号施以二阶互补滤波
filter = SecondOrderComplementaryFilter(SPD_OMEGA)
filter.set_dt(dt)
y_flt = np.empty(len(t))
for i in range(len(t)):
    y_flt[i] = filter.apply(y_noise[i],dy[i])

# 如果 dy 有噪声
filter2 = SecondOrderComplementaryFilter(SPD_OMEGA)
filter2.set_dt(dt)
y_flt2 = np.empty(len(t))
for i in range(len(t)):
    y_flt2[i] = filter2.apply(y[i],dy_noise[i])

rate_hp_out       = []
_last_rate_hp_out = y_noise[0]
_last_rate_hp_in  = y_noise[0]
omega             = 8
for i in range(len(t)):
    rate_hp_out.append((1 - omega * dt) * _last_rate_hp_out + y_noise[i] - _last_rate_hp_in)
    _last_rate_hp_out = rate_hp_out[-1]
    _last_rate_hp_in  = y_noise[i]

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

ax1.plot(t,
         y,
         label="f(x)",
         marker = '.',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax1.plot(t,
         dy,
         label="f'(x)",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax1.legend()

ax2.plot(t,
         y_noise,
         label="f(x) with noise",
         marker = '',
         markersize = 2,
         linestyle=":",
         linewidth=0.6)
ax2.plot(t,
         y_flt,
         label="f(x) filtered 1",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax2.legend()

ax3.plot(t,
         dy_noise,
         label="f'(x) with noise",
         marker = '',
         markersize = 2,
         linestyle=":",
         linewidth=0.6)
ax3.plot(t,
         y_flt2,
         label="f(x) filtered 2",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax3.legend()

ax4.plot(t,
         y,
         label="f(x)",
         marker = '.',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax4.plot(t,
         y_flt,
         label="f(x) filtered 1",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax4.plot(t,
         y_flt2,
         label="f(x) filtered 2",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax4.legend()

ax5.plot(t,
         y_noise,
         label="f(x) with noise",
         marker = '',
         markersize = 2,
         linestyle=":",
         linewidth=0.6)
ax5.plot(t,
         rate_hp_out,
         label="high pass f(x) with noise",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax5.plot(t,
         noise,
         label="noise",
         marker = '',
         markersize = 2,
         linestyle="-",
         linewidth=0.6)
ax5.legend()

plt.show()