#!/usr/bin/python3
parm_file = "vt11_01"
parm_file_name = parm_file+".param"

ignore_list = ["compass","acc_cal"]

import os
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("New Folder OK")
    else:
        print("Folder already exists")

mkdir(parm_file)

serial      = ['SERIAL0_BAUD','SERIAL0_PROTOCOL',
               'SERIAL1_BAUD','SERIAL1_PROTOCOL',
               'SERIAL2_BAUD','SERIAL2_PROTOCOL',
               'SERIAL3_BAUD','SERIAL3_PROTOCOL',
               'SERIAL4_BAUD','SERIAL4_PROTOCOL',
               'SERIAL5_BAUD','SERIAL5_PROTOCOL']

battery     = ['BATT_MONITOR','BATT_FS_VOLTSRC',
               'BATT_VOLT_PIN','BATT_VOLT_MULT',
               'BATT_CURR_PIN','BATT_AMP_PERVLT',
               'BATT_AMP_OFFSET','BATT_LOW_TIMER',
               'BATT_LOW_VOLT','BATT_FS_LOW_ACT',
               'BATT_CRT_VOLT','BATT_FS_CRT_ACT',
               'BATT_CAPACITY','BATT_OPTIONS',
               'BATT_LOW_MAH','BATT_CRT_MAH',
               'BATT_FS_LOW_ACT','BATT_FS_CRT_ACT']

airspeed    = ['ARSPD_USE','ARSPD_TYPE',
               'ARSPD_AUTOCAL','ARSPD_RATIO']

ahrs        = ['AHRS_ORIENTATION','AHRS_EKF_TYPE']
compass     = ['COMPASS_USE','COMPASS_USE2',
               'COMPASS_USE3','COMPASS_DEV_ID',
               'COMPASS_DEV_ID2','COMPASS_DIA_X',
               'COMPASS_DIA_Y','COMPASS_DIA_Z',
               'COMPASS_DIA2_X','COMPASS_DIA2_Y',
               'COMPASS_DIA2_Z','COMPASS_EXTERN2',
               'COMPASS_EXTERNAL','COMPASS_ODI_X',
               'COMPASS_ODI_Y','COMPASS_ODI_Z',
               'COMPASS_ODI2_X','COMPASS_ODI2_Y',
               'COMPASS_ODI2_Z','COMPASS_OFS_X',
               'COMPASS_OFS_Y','COMPASS_OFS_Z',
               'COMPASS_OFS2_X','COMPASS_OFS2_Y',
               'COMPASS_OFS2_Z','COMPASS_ORIENT',
               'COMPASS_ORIENT2','COMPASS_PRIO1_ID',
               'COMPASS_PRIO2_ID']

rangefinder = ['RNGFND1_TYPE','RNGFND1_FUNCTION',
               'RNGFND1_MIN_CM','RNGFND1_MAX_CM',
               'RNGFND1_ORIENT','RNGFND1_MIN_CM',
               'RNGFND1_MAX_CM','RNGFND1_ORIENT',]

servos      = ['SERVO1_FUNCTION','SERVO1_REVERSED','SERVO1_MIN','SERVO1_MAX','SERVO1_TRIM','SERVO1_CAN_IDH','SERVO1_CAN_IDL',
               'SERVO2_FUNCTION','SERVO2_REVERSED','SERVO2_MIN','SERVO2_MAX','SERVO2_TRIM','SERVO2_CAN_IDH','SERVO2_CAN_IDL',
               'SERVO3_FUNCTION','SERVO3_REVERSED','SERVO3_MIN','SERVO3_MAX','SERVO3_TRIM','SERVO3_CAN_IDH','SERVO3_CAN_IDL',
               'SERVO4_FUNCTION','SERVO4_REVERSED','SERVO4_MIN','SERVO4_MAX','SERVO4_TRIM','SERVO4_CAN_IDH','SERVO4_CAN_IDL',
               'SERVO5_FUNCTION','SERVO5_REVERSED','SERVO5_MIN','SERVO5_MAX','SERVO5_TRIM','SERVO5_CAN_IDH','SERVO5_CAN_IDL',
               'SERVO6_FUNCTION','SERVO6_REVERSED','SERVO6_MIN','SERVO6_MAX','SERVO6_TRIM','SERVO6_CAN_IDH','SERVO6_CAN_IDL',
               'SERVO7_FUNCTION','SERVO7_REVERSED','SERVO7_MIN','SERVO7_MAX','SERVO7_TRIM','SERVO7_CAN_IDH','SERVO7_CAN_IDL',
               'SERVO8_FUNCTION','SERVO8_REVERSED','SERVO8_MIN','SERVO8_MAX','SERVO8_TRIM','SERVO8_CAN_IDH','SERVO8_CAN_IDL',
               'SERVO9_FUNCTION','SERVO9_REVERSED','SERVO9_MIN','SERVO9_MAX','SERVO9_TRIM','SERVO9_CAN_IDH','SERVO9_CAN_IDL',
               'SERVO10_FUNCTION','SERVO10_REVERSED','SERVO10_MIN','SERVO10_MAX','SERVO10_TRIM','SERVO10_CAN_IDH','SERVO10_CAN_IDL',
               'SERVO11_FUNCTION','SERVO11_REVERSED','SERVO11_MIN','SERVO11_MAX','SERVO11_TRIM','SERVO11_CAN_IDH','SERVO11_CAN_IDL',
               'SERVO12_FUNCTION','SERVO12_REVERSED','SERVO12_MIN','SERVO12_MAX','SERVO12_TRIM','SERVO12_CAN_IDH','SERVO12_CAN_IDL',
               'SERVO13_FUNCTION','SERVO13_REVERSED','SERVO13_MIN','SERVO13_MAX','SERVO13_TRIM','SERVO13_CAN_IDH','SERVO13_CAN_IDL',
               'SERVO14_FUNCTION','SERVO14_REVERSED','SERVO14_MIN','SERVO14_MAX','SERVO14_TRIM','SERVO14_CAN_IDH','SERVO14_CAN_IDL',
               'SERVO15_FUNCTION','SERVO15_REVERSED','SERVO15_MIN','SERVO15_MAX','SERVO15_TRIM','SERVO15_CAN_IDH','SERVO15_CAN_IDL',
               'SERVO16_FUNCTION','SERVO16_REVERSED','SERVO16_MIN','SERVO16_MAX','SERVO16_TRIM','SERVO16_CAN_IDH','SERVO16_CAN_IDL']

can         = ['CAN_P1_DRIVER','CAN_P2_DRIVER',
               'CAN_P1_BITRATE','CAN_P2_BITRATE',
               'CAN_D1_PROTOCOL','CAN_D2_PROTOCOL']

board       = ['BRD_SAFETY_DEFLT']

rc          = ['RC1_OPTION','RC2_OPTION',
               'RC3_OPTION','RC4_OPTION',
               'RC5_OPTION','RC6_OPTION',
               'RC7_OPTION','RC8_OPTION',
               'RC9_OPTION','RC10_OPTION',
               'RC11_OPTION','RC12_OPTION',
               'RC13_OPTION','RC14_OPTION',
               'RC15_OPTION','RC16_OPTION']

gps         = ['GPS_TYPE','GPS_TYPE2',
               'GPS_AUTO_CONFIG','GPS_POS1_X',
               'GPS_POS1_Y','GPS_POS1_Z',
               'GPS_POS2_X','GPS_POS2_Y',
               'GPS_POS2_Z']

arming      = ['ARMING_CHECK','ARMING_RUDDER']

EKF3        = ['EK3_MAG_CAL','EK3_SRC1_YAW',
               'EK3_IMU_MASK','EK3_PRIMARY',
               'EK3_AFFINITY','EK3_ERR_THRESH']

log         = ['LOG_DISARMED','Q_M_LOG_MOTS']

flight_mode = ['FLTMODE1','FLTMODE2',
               'FLTMODE3','FLTMODE4',
               'FLTMODE5','FLTMODE6']

vehicle     = ['WHO']

plane       = ['TRIM_ARSPD_CM','ALT_HOLD_RTL',
               'WP_LOITER_RAD','RTL_RADIUS',
               'ARSPD_FBW_MIN','ARSPD_FBW_MAX',
               'LIM_PITCH_MIN','LIM_PITCH_MAX',
               'STICK_MIXING','LAND_FLARE_ALT',
               'LIM_ROLL_CD','RTL_AUTOLAND',
               'LAND_PF_ARSPD','LAND_PITCH_CD',
               'LAND_FINAL_ALT','LAND_FINAL_PTCH',
               'LAND_FINAL_SEC','LAND_FLARE_ALT',
               'HOME_RESET_ALT','LAND_TSHD',
               'TKOFF_ROTATE_SPD','TKOFF_THR_MINSPD',
               'TKOFF_THR_ENABLE']

mission     = ['MIS_RESTART']

tecs        = ['TECS_SINK_MIN','TECS_SINK_MAX',
               'TECS_LAND_ARSPD','TECS_LAND_SPDWGT',
               'TECS_APPR_SMAX',
               'TECS_LAND_ARSPD','TECS_LAND_SPDWGT',]

navl1      = ['NAVL1_LIM_BANK','NAVL1_DAMPING',
              'NAVL1_PERIOD','NAVL1_XTRACK_I']

acc_cal    = ['AHRS_TRIM_X','AHRS_TRIM_Y',
              'INS_ACC1_CALTEMP','INS_ACC2_CALTEMP',
              'INS_ACC2OFFS_X','INS_ACC2OFFS_Y',
              'INS_ACC2OFFS_Z','INS_ACC2SCAL_X',
              'INS_ACC2SCAL_Y','INS_ACC2SCAL_Z',
              'INS_ACCOFFS_X','INS_ACCOFFS_Y',
              'INS_ACCOFFS_Z','INS_ACCSCAL_X',
              'INS_ACCSCAL_Y','INS_ACCSCAL_Z']

rc_failsafe = ['THR_FAILSAFE','THR_FS_VALUE',
               'FS_SHORT_ACTN','FS_SHORT_TIMEOUT',
               'FS_LONG_ACTN','FS_LONG_TIMEOUT',
               'FS_GCS_ENABL']

pidp_plane  = ['KFF_THR2PTCH','TRIM_PITCH_CD',
               'PTCH2SRV_TCONST','PTCH2SRV_RMAX_DN',
               'PTCH2SRV_RMAX_UP','LIM_ROLL_CD',
               'PTCH2SRV_RLL','PTCH_RATE_FLTT',
               'PTCH_RATE_FLTE','PTCH_RATE_FF',
               'PTCH_RATE_P','PTCH_RATE_I',
               'PTCH_RATE_D','PTCH_RATE_FLTD',
               'PTCH_RATE_IMAX','PTCH_RATE_SMAX']

pidr_plane  = ['RLL2SRV_TCONST','RLL2SRV_RMAX',
               'RLL_RATE_FLTT','RLL_RATE_FLTE',
               'RLL_RATE_FF','RLL_RATE_P',
               'RLL_RATE_I','RLL_RATE_D',
               'RLL_RATE_FLTD','RLL_FATE_IMAX',
               'RLL_RATE_SMAX']

rpm         = ['SERVO_GPIO_MASK','RPM1_TYPE',
               'RPM1_PIN','RPM1_SCALING',
               'RPM1_MIN_QUAL']

piqh_quadplane = ['Q_P_POSZ_P','Q_ACCEL_Z',
                  'Q_VELZ_MAX','Q_VELZ_MAX_DN',
                  'Q_P_VELZ_P','Q_P_VELZ_I',
                  'Q_P_VELZ_D','Q_P_VELZ_FF',
                  'Q_P_VELZ_FLTE','Q_P_VELZ_FLTD',
                  'Q_P_VELZ_IMAX','Q_M_THST_HOVER',
                  'Q_P_ACCZ_P','Q_P_ACCZ_I',
                  'Q_P_ACCZ_IMAX','Q_P_ACCZ_D',
                  'Q_P_ACCZ_FF','Q_P_ACCZ_FLTT',
                  'Q_P_ACCZ_FLTE','Q_P_ACCZ_FLTD',
                  'Q_P_ACCZ_SMAX']

piqr_quadplane = ['Q_A_ANG_RLL_P','Q_A_ACCEL_R_MAX',
                  'Q_A_RAT_RLL_FLTT','Q_A_RAT_RLL_FLTE',
                  'Q_A_RAT_RLL_FLTD','Q_A_RAT_RLL_P',
                  'Q_A_RAT_RLL_I','Q_A_RAT_RLL_D',
                  'Q_A_RAT_RLL_FF','Q_A_RAT_RLL_IMAX',
                  'Q_A_RAT_RLL_SMAX']

piqp_quadplane = ['Q_A_ANG_PIT_P','Q_A_ACCEL_P_MAX',
                  'Q_A_RAT_PIT_FLTT','Q_A_RAT_PIT_FLTE',
                  'Q_A_RAT_PIT_FLTD','Q_A_RAT_PIT_P',
                  'Q_A_RAT_PIT_I','Q_A_RAT_PIT_D',
                  'Q_A_RAT_PIT_FF','Q_A_RAT_PIT_IMAX',
                  'Q_A_RAT_PIT_SMAX']

piqy_quadplane = ['Q_A_ANG_YAW_P','Q_A_ACCEL_Y_MAX',
                  'Q_A_RAT_YAW_FLTT','Q_A_RAT_YAW_FLTE',
                  'Q_A_RAT_YAW_FLTD','Q_A_RAT_YAW_P',
                  'Q_A_RAT_YAW_I','Q_A_RAT_YAW_D',
                  'Q_A_RAT_YAW_FF','Q_A_RAT_YAW_IMAX',
                  'Q_A_RAT_YAW_SMAX']

serial_file            = open(parm_file+"/serial_"+parm_file+".param",'w',encoding='utf-8')
battery_file           = open(parm_file+"/battery_"+parm_file+".param",'w',encoding='utf-8')
airspeed_file          = open(parm_file+"/airspeed_"+parm_file+".param",'w',encoding='utf-8')
ahrs_file              = open(parm_file+"/ahrs_"+parm_file+".param",'w',encoding='utf-8')
compass_file           = open(parm_file+"/compass_"+parm_file+".param",'w',encoding='utf-8')
rangefinder_file       = open(parm_file+"/rangefinder_"+parm_file+".param",'w',encoding='utf-8')
servos_file            = open(parm_file+"/servos_"+parm_file+".param",'w',encoding='utf-8')
can_file               = open(parm_file+"/can_"+parm_file+".param",'w',encoding='utf-8')
board_file             = open(parm_file+"/board_"+parm_file+".param",'w',encoding='utf-8')
rc_file                = open(parm_file+"/rc_"+parm_file+".param",'w',encoding='utf-8')
gps_file               = open(parm_file+"/gps_"+parm_file+".param",'w',encoding='utf-8')
arming_file            = open(parm_file+"/arming_"+parm_file+".param",'w',encoding='utf-8')
EKF3_file              = open(parm_file+"/EKF3_"+parm_file+".param",'w',encoding='utf-8')
log_file               = open(parm_file+"/log_"+parm_file+".param",'w',encoding='utf-8')
flight_mode_file       = open(parm_file+"/flight_mode_"+parm_file+".param",'w',encoding='utf-8')
vehicle_file           = open(parm_file+"/vehicle_"+parm_file+".param",'w',encoding='utf-8')
plane_file             = open(parm_file+"/plane_"+parm_file+".param",'w',encoding='utf-8')
mission_file           = open(parm_file+"/mission_"+parm_file+".param",'w',encoding='utf-8')
tecs_file              = open(parm_file+"/tecs_"+parm_file+".param",'w',encoding='utf-8')
navl1_file             = open(parm_file+"/navl1_"+parm_file+".param",'w',encoding='utf-8')
acc_cal_file           = open(parm_file+"/acc_cal_"+parm_file+".param",'w',encoding='utf-8')
rc_failsafe_file       = open(parm_file+"/rc_failsafe_"+parm_file+".param",'w',encoding='utf-8')
pidp_plane_file        = open(parm_file+"/pidp_plane_"+parm_file+".param",'w',encoding='utf-8')
pidr_plane_file        = open(parm_file+"/pidr_plane_"+parm_file+".param",'w',encoding='utf-8')
rpm_file               = open(parm_file+"/rpm_"+parm_file+".param",'w',encoding='utf-8')
piqh_quadplane_file    = open(parm_file+"/piqh_quadplane_"+parm_file+".param",'w',encoding='utf-8')
piqr_quadplane_file    = open(parm_file+"/piqr_quadplane_"+parm_file+".param",'w',encoding='utf-8')
piqp_quadplane_file    = open(parm_file+"/piqp_quadplane_"+parm_file+".param",'w',encoding='utf-8')
piqy_quadplane_file    = open(parm_file+"/piqy_quadplane_"+parm_file+".param",'w',encoding='utf-8')


def iter_count(file_name):
    '''
    Python计算大文件行数方法及性能比较
    https://www.cnblogs.com/jhao/p/13488867.html
    '''
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)

line_cnt = iter_count(parm_file_name)

with open(parm_file_name,'r',encoding='utf-8') as file:
    for i in range(line_cnt):
        content = file.readline()
        param_name = content.split(',')[0]
        if param_name in serial:
            serial_file.write(content)
        if param_name in battery:
            battery_file.write(content)
        if param_name in airspeed:
            airspeed_file.write(content)
        if param_name in ahrs:
            ahrs_file.write(content)
        if param_name in compass:
            compass_file.write(content)
        if param_name in rangefinder:
            rangefinder_file.write(content)
        if param_name in servos:
            servos_file.write(content)
        if param_name in can:
            can_file.write(content)
        if param_name in board:
            board_file.write(content)
        if param_name in rc:
            rc_file.write(content)
        if param_name in gps:
            gps_file.write(content)
        if param_name in arming:
            arming_file.write(content)
        if param_name in EKF3:
            EKF3_file.write(content)
        if param_name in log:
            log_file.write(content)
        if param_name in flight_mode:
            flight_mode_file.write(content)
        if param_name in vehicle:
            vehicle_file.write(content)
        if param_name in plane:
            plane_file.write(content)
        if param_name in mission:
            mission_file.write(content)
        if param_name in tecs:
            tecs_file.write(content)
        if param_name in navl1:
            navl1_file.write(content)
        if param_name in acc_cal:
            acc_cal_file.write(content)
        if param_name in rc_failsafe:
            rc_failsafe_file.write(content)
        if param_name in pidp_plane:
            pidp_plane_file.write(content)
        if param_name in pidr_plane:
            pidr_plane_file.write(content)
        if param_name in rpm:
            rpm_file.write(content)
        if param_name in piqh_quadplane:
            piqh_quadplane_file.write(content)
        if param_name in piqr_quadplane:
            piqr_quadplane_file.write(content)
        if param_name in piqp_quadplane:
            piqp_quadplane_file.write(content)
        if param_name in piqy_quadplane:
            piqy_quadplane_file.write(content)

'''
filtered       = serial         + battery        \
               + airspeed       + ahrs           \
               + rangefinder                     \
               + servos         + can            \
               + board          + rc             \
               + gps            + arming         \
               + EKF3           + log            \
               + flight_mode    + vehicle        \
               + plane          + mission        \
               + tecs           + navl1          \
               + rc_failsafe    + pidp_plane     \
               + pidr_plane     + rpm            \
               + piqh_quadplane + piqy_quadplane \
               + piqr_quadplane + piqp_quadplane

filtered_file = open(parm_file+"/00_filtered_"+parm_file+".param","w",encoding='utf-8')

with open(parm_file_name,'r',encoding='utf-8') as file:
    for i in range(line_cnt):
        content = file.readline()
        param_name = content.split(',')[0]
        if param_name in filtered:
            filtered_file.write(content)

filtered_file.close()
'''

ignore_str = ""
for item in ignore_list:
    ignore_str += "\""
    ignore_str += item
    ignore_str += "\","
ignore_str = ignore_str[0:-1]

synthesis_file = open(parm_file+"/synthesis_param"+".py","w",encoding='utf-8')
synthesis_file.write('''#!/usr/bin/python3
import os
from sys import platform

ignore_list = [%s]

PATH_DELIMITER = None
if platform == 'win32':
    PATH_DELIMITER = '\\\\'
elif platform == "linux" or platform == "linux2":
    PATH_DELIMITER = '/'

def iter_count(file_name):
    \'\'\'
    Python计算大文件行数方法及性能比较
    https://www.cnblogs.com/jhao/p/13488867.html
    \'\'\'
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\\n') for buf in buf_gen)

# get path of current py file and directory
cur_file  = os.path.abspath(__file__)
cur_dir = cur_file.rsplit(PATH_DELIMITER, 1)[0]
cur_dir = cur_dir.rsplit(PATH_DELIMITER, 1)[-1]
del_str = "_"+cur_dir
del_len = -len(del_str)

file_names_list = os.listdir(".")

synthesis_file = open("00_synthesis_param"+".param","w",encoding='utf-8')

for file_name in file_names_list:
    if os.path.splitext(file_name)[-2][0:del_len] in ignore_list:
        continue
    if os.path.splitext(file_name)[-1] == ".py":
        continue

    with open(file_name,'r',encoding='utf-8') as file:
        line_cnt = iter_count(file_name)
        for i in range(line_cnt):
            content = file.readline()
            param_name = content.split(',')[0]
            synthesis_file.write(content)

synthesis_file.close()

'''%(ignore_str))