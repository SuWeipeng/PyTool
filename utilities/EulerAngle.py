import numpy as np
import math
from sympy import *

class EulerAngle:
    M_PI            = 3.141592653589793
    DEG_TO_RAD      = M_PI / 180
    RAD_TO_DEG      = 180  / M_PI
    FLT_EPSILON     = 1e-7

    def __init__(self):
        self.ang_rad = []
        self.ssr = symbols('sr')
        self.ssp = symbols('sp')
        self.ssy = symbols('sy')
        self.scr = symbols('cr')
        self.scp = symbols('cp')
        self.scy = symbols('cy')

    def SymRX(self):
        sr = self.ssr
        sp = self.ssp
        sy = self.ssy
        cr = self.scr
        cp = self.scp
        cy = self.scy
        self.RX = Matrix([[ 1,  0,   0],
                          [ 0, cr, -sr],
                          [ 0, sr,  cr]])
        return self.RX

    def SymRY(self):
        sr = self.ssr
        sp = self.ssp
        sy = self.ssy
        cr = self.scr
        cp = self.scp
        cy = self.scy
        self.RY = Matrix([[  cp, 0, sp],
                          [   0, 1,  0],
                          [ -sp, 0, cp]])
        return self.RY

    def SymRZ(self):
        sr = self.ssr
        sp = self.ssp
        sy = self.ssy
        cr = self.scr
        cp = self.scp
        cy = self.scy
        self.RZ = Matrix([[ cy, -sy, 0],
                          [ sy,  cy, 0],
                          [  0,   0, 1]])
        return self.RZ

    def _calc_factors(self):
        [self.sr,self.sp,self.sy] = np.sin(self.ang_rad)
        [self.cr,self.cp,self.cy] = np.cos(self.ang_rad)
        replace = [self.sr,self.sp,self.sy] + [self.cr,self.cp,self.cy]
        res = []
        for i in replace:
            if abs(i) < self.FLT_EPSILON:
                res.append(0)
            elif len(str(i))>7:
                tmp = float("%.3f"%i)
                if abs(tmp-i) < self.FLT_EPSILON:
                    res.append(tmp)
                else:
                    res.append(i)
            else:
                res.append(i)
        [self.sr,self.sp,self.sy] = res[:3]
        [self.cr,self.cp,self.cy] = res[3:6]

    def rot_xyz(self,list_deg):
        self.ang_rad = np.array(list_deg) * self.DEG_TO_RAD
        self._calc_factors()
        sr = self.sr
        sp = self.sp
        sy = self.sy
        cr = self.cr
        cp = self.cp
        cy = self.cy
        return np.mat([[cp*cy, cy*sp*sr - cr*sy, sr*sy + cr*cy*sp],
                       [cp*sy, cr*cy + sp*sr*sy, cr*sp*sy - cy*sr],
                       [  -sp,            cp*sr,            cp*cr]])

    def rot_xyz2(self,r_deg,p_deg,y_deg):
        self.ang_rad = np.array([r_deg,p_deg,y_deg]) * self.DEG_TO_RAD
        self._calc_factors()
        sr = self.sr
        sp = self.sp
        sy = self.sy
        cr = self.cr
        cp = self.cp
        cy = self.cy
        return np.mat([[cp*cy, cy*sp*sr - cr*sy, sr*sy + cr*cy*sp],
                       [cp*sy, cr*cy + sp*sr*sy, cr*sp*sy - cy*sr],
                       [  -sp,            cp*sr,            cp*cr]])

def main():
    euler = EulerAngle()
    print(euler.rot_xyz2(0,-30,0))

if __name__ == '__main__':
    main()