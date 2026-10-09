import numpy as np
from numpy import random as rnd

# num 采样点数量
num = 100
# dt 采样步长，单位：秒(s)
dt = 0.02
# rng 随机数泛围 (-rng, rng)
rng = 10
v = rnd.uniform(-rng,rng,size=(1,num))[0]
t = np.linspace(0,dt*num,num,endpoint=False)

DERIVATIVE_CUTOFF_FREQ = 25
N_EVENTS = 2
WINDOW_MS = 300
MODIFIER_GAIN = 1.5

def constrain_float(v,mi,ma):
    res = v
    if v < mi:
        res = mi
    if v > ma:
        res = ma
    return res

def millis():
    from time import time
    return int(round(time() * 1000))

def fminf(a,b):
    res = a
    if b < a:
        res = b
    return res

class SlewLimiter:
    def __init__(self, slew_rate_max, slew_rate_tau):
        self.slew_rate_max = slew_rate_max
        self.slew_rate_tau = slew_rate_tau
        self.slew_filter = LowPassFilter()
        self.slew_filter.set_cutoff_frequency(DERIVATIVE_CUTOFF_FREQ)
        self.slew_filter.reset(0)
        self.last_sample = 0
        self._pos_event_stored = False
        self._neg_event_stored = False
        self._pos_event_index = 0
        self._neg_event_index = 0
        self._pos_event_ms = []
        self._neg_event_ms = []
        self._max_pos_slew_rate = 0.0
        self._max_neg_slew_rate = 0.0
        self._max_pos_slew_event_ms = 0
        self._max_neg_slew_event_ms = 0
        self._modifier_slew_rate = 0.0
        self._output_slew_rate = 0.0
    
    def get_slew_rate(self):
        return self._output_slew_rate
        
    def modifier(self,sample,dt):
        if self.slew_rate_max <= 0:
            return 1.0
        slew_rate = self.slew_filter.apply((sample - self.last_sample) / dt, dt)
        self.last_sample = sample
        
        now_ms = millis()
        decay_alpha = fminf(dt, self.slew_rate_tau) / self.slew_rate_tau
        
        if not self._pos_event_stored and slew_rate > self.slew_rate_max:
            if self._pos_event_index >= N_EVENTS:
                self._pos_event_index = 0
                if len(self._pos_event_ms) >= N_EVENTS:
                    self._pos_event_ms[self._pos_event_index] = now_ms
                else:
                    self._pos_event_ms.append(now_ms)
                self._pos_event_index += 1
                self._pos_event_stored = True
                self._neg_event_stored = False
                
        if not self._neg_event_stored and slew_rate < - self.slew_rate_max:
            if self._neg_event_index >= N_EVENTS:
                self._neg_event_index = 0
                if len(self._neg_event_ms) >= N_EVENTS:
                    self._neg_event_ms[self._neg_event_index] = now_ms
                else:
                    self._neg_event_ms.append(now_ms)    
                self._neg_event_ms += 1
                self._neg_event_stored = True
                self._pos_event_stored = False
        
        oldest_ms = now_ms
        for index in range(N_EVENTS):
            if index <= len(self._pos_event_ms) - 1:
                if self._pos_event_ms[index] < oldest_ms:
                    oldest_ms = self._pos_event_ms[index]
            if index <= len(self._neg_event_ms) - 1:
                if self._neg_event_ms[index] < oldest_ms:
                    oldest_ms = self._neg_event_ms[index]
                    
        if slew_rate > self._max_pos_slew_rate:
            self._max_pos_slew_rate = fminf(slew_rate, 10.0 * self.slew_rate_max)
            self._max_pos_slew_event_ms = now_ms
        elif now_ms - self._max_pos_slew_event_ms > WINDOW_MS:
            self._max_pos_slew_rate *= (1.0 - decay_alpha)

        if slew_rate < -self._max_neg_slew_rate:
            self._max_neg_slew_rate = fminf(-slew_rate, 10.0 * self.slew_rate_max)
            self._max_neg_slew_event_ms = now_ms
        elif now_ms - self._max_neg_slew_event_ms > WINDOW_MS:
            self._max_neg_slew_rate *= (1.0 - decay_alpha)
            
        raw_slew_rate = 0.5*(self._max_pos_slew_rate + self._max_neg_slew_rate)
        
        from math import exp
        modifier_input = raw_slew_rate
        if now_ms - oldest_ms > (N_EVENTS + 1) * WINDOW_MS:
            oldest_time_from_window = 0.001*(now_ms - oldest_ms - (N_EVENTS + 1) * WINDOW_MS)
            modifier_input *= exp(-oldest_time_from_window / self.slew_rate_tau)
            
        attack_alpha = fminf(2.0 * decay_alpha, 1.0)
        
        self._modifier_slew_rate = (1.0 - attack_alpha) * self._modifier_slew_rate + attack_alpha * modifier_input
        self._modifier_slew_rate = fminf(self._modifier_slew_rate, modifier_input)
        
        self._output_slew_rate = (1.0 - attack_alpha) * self._output_slew_rate + attack_alpha * raw_slew_rate
        self._output_slew_rate = fminf(self._output_slew_rate, raw_slew_rate)
        
        mod = 0.0
        if self._modifier_slew_rate > self.slew_rate_max:
            mod = self.slew_rate_max / (self.slew_rate_max + MODIFIER_GAIN * (self._modifier_slew_rate - self.slew_rate_max))
        else:
            mod = 1.0
            
        return mod
    
class LowPassFilter:
    def __init__(self):
        self._cutoff_freq = 0
        self._filter = DigitalLPF()
    def set_cutoff_frequency(self,cutoff_freq):
        self._cutoff_freq = cutoff_freq
    def reset(self,value):
        self._filter.reset(value)
    def apply(self,sample,dt):
        return self._filter.apply(sample, self._cutoff_freq, dt)

class DigitalLPF:
    def __init__(self):
        self._output = 0
        self.initialised = False
        self.alpha = 0
    def reset(self,value):
        self._output = value
        self.initialised = True
    def apply(self,sample,cutoff_freq,dt):
        if cutoff_freq <= 0.0 or dt <= 0.0:
            self._output = sample
            return self._output
        from math import pi
        rc = 1.0 / (2*pi*cutoff_freq)
        self.alpha = constrain_float(dt/(dt+rc),0.0,1.0)
        self._output += (sample - self._output) * self.alpha
        if not self.initialised:
            self.initialised = True
            self._output = sample

        self._output = self._output.astype(type('float',(float,),{}))

        return self._output     

rel_dt = []
last_timestamp = 0
def calc_rel_dt(dt,now):
    global last_timestamp
    if len(rel_dt) == 0:
        rel_dt.append(dt)
    else:
        rel_dt.append(now-last_timestamp)
    last_timestamp = now

Dmod = []
slew_rate = []
vm = []
slew_limiter = SlewLimiter(50,1) 
from time import sleep
for i in range(len(v)):
    mod = slew_limiter.modifier(v[i],dt)
    slr = slew_limiter.get_slew_rate()
    vm.append(v[i]*mod)
    Dmod.append(mod)
    slew_rate.append(slr)
    calc_rel_dt(dt,millis())
    sleep(dt)

#matplotlib widget
import matplotlib.pyplot as plt
f,((ax1,ax2,ax3,ax4)) = plt.subplots(4,1)
ax1.plot(t,v,t,vm);ax1.set_title('Data')
ax2.plot(t,Dmod);ax2.set_title('Dmod')    
ax3.plot(t,slew_rate);ax3.set_title('slew_rate')
ax4.plot(list(range(len(rel_dt))),rel_dt);ax4.set_title('real dt (ms)')
plt.tight_layout()
plt.show()