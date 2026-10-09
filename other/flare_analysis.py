import numpy as np

ae = 5 # angle_error
de_threshold = 0.1e0

with open("cessna182_flare.txt","r",encoding="utf-8") as file:
    lines = file.readlines()

class Flare:
    def __init__(self,wind,aoa,ele,srv,thr,alt):
        self.wind   = wind
        self.aoa    = aoa
        self.ele    = ele
        self.srv    = srv
        self.thr    = thr
        self.alt    = alt

wind   = []
aoa    = []
ele    = []
srv    = []
thr    = []
alt    = []
for line in lines:
    wind.append(float(line.split('\t')[1]))
    aoa.append(float(line.split('\t')[3]))
    ele.append(float(line.split('\t')[5]))
    srv.append(float(line.split('\t')[7]))
    thr.append(float(line.split('\t')[9]))
    alt.append(float(line.split('\t')[11][:-1]))

from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

fig  = plt.figure(figsize=(16, 9), dpi=1920/16)
gsc  = gridspec.GridSpec(nrows=2, ncols=2, left=0.03, right=0.98, wspace=0.12)
ax1  = fig.add_subplot(gsc[0,0])
ax1.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
ax1.grid(ls="--")
ax2  = fig.add_subplot(gsc[0,1])
ax2.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
ax2.grid(ls="--")
ax3  = fig.add_subplot(gsc[1,0])
ax3.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
ax3.grid(ls="--")
ax4  = fig.add_subplot(gsc[1,1])
ax4.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
ax4.grid(ls="--")

def data_fit(x,y,n):
    f1 = np.polyfit(x, y, n)
    p1 = np.poly1d(f1)
    print('y = \n',p1)
    fit_value = p1(x)
    return fit_value

ax1.plot(wind,
         aoa,
         label="aoa",
         marker = '.',
         linestyle=":")
ax1.plot(wind,
         data_fit(wind,aoa,3),
         label="aoa_fit3",
         marker = '.',
         linestyle=":")
ax1.legend()

ax2.plot(aoa,
         srv,
         label="FLARE_SRVDEC_SEC",
         marker = '.',
         linestyle=":")
ax2.plot(aoa,
         data_fit(aoa,srv,3),
         label="fit3",
         marker = '.',
         linestyle=":")
ax2.legend()

ax3.plot(aoa,
         thr,
         label="THR_SUPP_SEC",
         marker = '.',
         linestyle=":")
ax3.plot(aoa,
         data_fit(aoa,thr,3),
         label="fit3",
         marker = '.',
         linestyle=":")
ax3.legend()

ax4.plot(aoa,
         alt,
         label="LAND_FLARE_ALT",
         marker = '.',
         linestyle=":")
ax4.plot(aoa,
         data_fit(aoa,alt,3),
         label="fit3",
         marker = '.',
         linestyle=":")
ax4.legend()

plt.show()