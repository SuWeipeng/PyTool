import sys
sys.path.append('.')
from MathCommon import *

class AC_P_1D:
    def __init__(self, initial_p, dt):
        self._dt = dt
        self._kp = initial_p

    def set_limits(self, output_min, output_max, D_Out_max, D2_Out_max):
        self._D1_max = 0.0
        self._error_min = 0.0
        self._error_max = 0.0

        if is_positive(D_Out_max):
            self._D1_max = D_Out_max

        if is_positive(D2_Out_max) and is_positive(self._kp):
            self._D1_max = MIN(self._D1_max, D2_Out_max / self._kp)

        if is_negative(output_min) and is_positive(self._kp):
            self._error_min = inv_sqrt_controller(output_min, self._kp, self._D1_max)

        if is_positive(output_max) and is_positive(self._kp):
            self._error_max = inv_sqrt_controller(output_max, self._kp, self._D1_max)

    def set_error_limits(self, error_min, error_max):
        if is_negative(error_min):
            if not is_zero(self._error_min):
                self._error_min = MAX(self._error_min, error_min)
            else:
                self._error_min = error_min
        if is_positive(error_max):
            if not is_zero(error_max):
                self._error_max = MIN(self._error_max, error_max)
            else:
                self._error_max = error_max

    def update_all(self, target, measurement):
        self._error = target - measurement

        if is_negative(self._error_min) and (self._error < self._error_min):
            self._error = self._error_min
            target = measurement + self._error
        elif is_positive(self._error_max) and (self._error > self._error_max):
            self._error = self._error_max
            target = measurement + self._error

        return target,sqrt_controller(self._error, self._kp, self._D1_max, self._dt)

    def kP(self,v):
        self._kp = v

    def print(self):
        print("_dt       :%.5f"%(self._dt))
        print("_kp       :%.5f"%(self._kp))
        print("_D1_max   :%.5f"%(self._D1_max))
        print("_error_min:%.5f"%(self._error_min))
        print("_error_max:%.5f"%(self._error_max))
        print("_error    :%.5f"%(self._error))

def main():
    p_1d = AC_P_1D(1,0.0025)
    p_1d.set_limits(-250,250,250,0)
    p_1d.update_all(0,0)
    p_1d.print()

if __name__ == '__main__':
    main()