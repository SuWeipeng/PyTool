import numpy as np
from numpy import random as rnd

# alpha in [0,1]
Q_THROTTLE_EXPO = 0.2   # Range: [0,1]
Q_M_THST_HOVER  = 0.35  # Range: [0,1]

AP_MOTORS_THST_HOVER_MIN       = 0.125  # minimum possible hover throttle
AP_MOTORS_THST_HOVER_MAX       = 0.6875 # maximum possible hover throttle

def constrain_float(v,mi,ma):
    res = v
    if v < mi:
        res = mi
    if v > ma:
        res = ma
    return res

def swap_float(f1, f2):
    tmp = f1
    f1 = f2
    f2 =tmp
    return (f1,f2)

def expo_curve(alpha, x):
    return (1.0 - alpha) * x + alpha * x * x * x;

def linear_interpolate(low_output, high_output, var_value, var_low, var_high):
    '''
    var_value 是在 [var_low, var_high] 之间某位置的值，此函数返回在 [low_output, high_output] 之间同一位置的值。
    
    有考虑到一些输入异常：
    1、var_value 超限时用 [low_output, high_output] 限幅；
    2、var_low 可以大于 var_high，但要注意此时 low_output 也要大于 high_output 才能正确插值
    '''
    if (var_low > var_high):
        # support either polarity
        var_low, var_high       = swap_float(var_low, var_high);
        low_output, high_output = swap_float(low_output, high_output);

    if (var_value <= var_low):
        return low_output;

    if (var_value >= var_high):
        return high_output;

    p = (var_value - var_low) / (var_high - var_low);
    return low_output + p * (high_output - low_output);

def throttle_curve(thr_mid, alpha, thr_in):
    alpha2 = alpha + 1.25 * (1.0 - alpha) * (0.5 - thr_mid) / 0.5;
    alpha2 = constrain_float(alpha2, 0.0, 1.0);
    thr_out = 0.0;
    if (thr_in < 0.5):
        t = linear_interpolate(-1.0, 0.0, thr_in, 0.0, 0.5);
        thr_out = linear_interpolate(0.0, thr_mid, expo_curve(alpha, t), -1.0, 0.0);
    else:
        t = linear_interpolate(0.0, 1.0, thr_in, 0.5, 1.0);
        thr_out = linear_interpolate(thr_mid, 1.0, expo_curve(alpha2, t), 0.0, 1.0);

    return thr_out;

input_list = np.linspace(0,1,101)
input_list = np.around(input_list,3)
input_list = list(input_list)
out        = []
for i in input_list:
    Q_M_THST_HOVER  = constrain_float(Q_M_THST_HOVER,AP_MOTORS_THST_HOVER_MIN,AP_MOTORS_THST_HOVER_MAX)
    Q_THROTTLE_EXPO = constrain_float(Q_THROTTLE_EXPO,0.0,1.0)
    tmp = throttle_curve(Q_M_THST_HOVER, Q_THROTTLE_EXPO, i)
    out.append(tmp)
    
import matplotlib.pyplot as plt
ax = plt.gca()
ax.plot(input_list,out,
        marker = '.',
        linestyle = ':')
ax.set_title('Q_THROTTLE_EXPO = %.3f\nQ_M_THST_HOVER  = %.3f'%(Q_THROTTLE_EXPO,Q_M_THST_HOVER))
miloc = plt.MultipleLocator(0.1)
ax.xaxis.set_minor_locator(miloc)
ax.yaxis.set_minor_locator(miloc)
ax.grid(linestyle='--',which='both')
ax.set_aspect('equal', adjustable='box')
plt.xlabel("throttle in")
plt.ylabel("curve")
plt.show()