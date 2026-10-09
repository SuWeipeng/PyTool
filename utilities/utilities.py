def get_bit_val(byte, index):
    """
    得到某个字节中某一位（Bit）的值

    :param byte: 待取值的字节值
    :param index: 待读取位的序号，从右向左0开始，0-7为一个完整字节的8个位
    :returns: 返回读取该位的值，0或1
    """
    if byte & (1 << index):
        return 1
    else:
        return 0

def filter_parm(start_us,end_us,parm_us):
    if parm_us >= start_us and parm_us <= end_us:
        return True
    else:
        return False

def get_same_elem(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    iset = set1.intersection(set2)
    return iset

def get_v_by_us(list_us, us, list_v):
    idx = list_us.index(us)
    return list_v[idx]

def linear_interpolation1(tb,tt,vt):
    tb_tt_same = list(get_same_elem(tb,tt))
    v_pick = {}
    for us in tb:
        if us in tb_tt_same:
            v_pick[us] = get_v_by_us(tt, us, vt) 
        else:
            import copy
            temp_us = copy.deepcopy(tt)
            temp_us.append(us)
            temp_us.sort()
            vt_idx_prev = temp_us.index(us)-1 if temp_us.index(us)-1 > 0 else 0
            if vt_idx_prev < len(tt)-1:
                pct = (us - tt[vt_idx_prev]) / (tt[vt_idx_prev+1] - tt[vt_idx_prev])
                v_pick[us] = vt[vt_idx_prev] + (vt[vt_idx_prev+1] - vt[vt_idx_prev]) * pct
            else:
                v_pick[us] = vt[vt_idx_prev]
    return v_pick

# 找最近值的索引
def find_closest_idx(lst, value):
    import numpy as np
    array = np.asarray(lst)
    idx = (np.abs(array - value)).argmin()
    return idx

# 找最近的值
def find_closest_value(lst, value):
    import numpy as np
    array = np.asarray(lst)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

# 计算时间差
def calt_delta_t(ms1, ms2):
    delta_str = ""
    delta_m   = 0
    delta_us = ms2-ms1
    delta_s  = delta_us * 1e-6
    delta_str = "%.2f s"%(delta_s)
    if delta_s > 60:
        delta_m = delta_s // 60
        delta_s = delta_s % 60
        delta_str = "%d min %.2f s"%(delta_m,delta_s)
    if delta_m > 60:
        delta_h = delta_m // 60
        delta_m = delta_m % 60
        delta_str = "%d h %d min %.2f s"%(delta_h,delta_m,delta_s)
    return delta_str
