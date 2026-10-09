care_params = []

def append_to_care_params(params):
    for p in params:
        care_params.append(p)
'''
gcs_failsafe_params = ['FS_LONG_TIMEOUT','FS_GCS_ENABLE','FS_LONG_ACTN']
append_to_care_params(gcs_failsafe_params)
takeoff_params = ['TKOFF_THR_DELAY','TKOFF_THR_MINACC','FLIGHT_OPTIONS','TKOFF_THR_MINSPD','TKOFF_LVL_ALT',
                  'TKOFF_LVL_PITCH','TKOFF_DIST']
append_to_care_params(takeoff_params)

flare_params = ['FLARE_FLMOUT_AZ','THR_SUPP_SEC','FLARE_ELEVATOR','FLARE_SRVDEC_SEC','FLARE_STABLE',
                'LAND_FLARE_ALT','LAND_FLARE_SEC','LAND_PF_ARSPD','LAND_FINAL_ALT','LAND_FINAL_PTCH',
                'LAND_FINAL_SEC']
append_to_care_params(flare_params)

tec6_params = ['TECS_THR_DAMP','TECS_LAND_TDAMP','TECS_INTEG_GAIN','TECS_TKOFF_IGAIN','TECS_LAND_IGAIN',
               'THR_SLEWRATE','LAND_THR_SLEW','TRIM_THROTTLE']
append_to_care_params(tec6_params)

tec7_tec8_params = ['TECS_SPDWEIGHT','TECS_LAND_SPDWGT','TECS_INTEG_GAIN','TECS_TKOFF_IGAIN','TECS_LAND_IGAIN',
                    'TECS_TIME_CONST','TECS_LAND_TCONST','TECS_PTCH_DAMP','TECS_LAND_DAMP','TECS_LAND_PDAMP',
                    'TECS_PTCH_FF_V0','TECS_PTCH_FF_K','TECS_VERT_ACC','TECS_LAND_PMAX']
append_to_care_params(tec7_tec8_params)

# Pitch 角速度环 PID 参数
params = ['PTCH_RATE_P','PTCH_RATE_I','PTCH_RATE_D','PTCH_RATE_IMAX','PTCH_RATE_FF',
          'PTCH_RATE_FLTD','PTCH_RATE_FLTE','PTCH_RATE_FLTT','PTCH_RATE_SMAX']
append_to_care_params(params)

# Roll 角速度环 PID 参数
params = ['RLL_RATE_P','RLL_RATE_I','RLL_RATE_D','RLL_RATE_IMAX','RLL_RATE_FF',
          'RLL_RATE_FLTD','RLL_RATE_FLTE','RLL_RATE_FLTT','RLL_RATE_SMAX']
append_to_care_params(params)

params = ['TECS_SPD_OMEGA','TECS_LAND_TCONST','TECS_TIME_CONST',
          'TECS_LAND_SINK','TECS_LAND_SRC','TECS_SINK_MAX',
          'TECS_APPR_SMAX','TECS_CLMB_MAX','TECS_SINK_MIN',
          'TECS_LAND_PCONST','FLARE_ELEVATOR','ARSPD_FBW_MIN',
          'ARSPD_RATIO','TECS_LAND_GCONST','LAND_PF_ARSPD',
          'LAND_PITCH_CD','RNGFND_LANDING','LAND_FLARE_SEC',
          'LAND_FLARE_ALT']
append_to_care_params(params)

params = ['LIM_PITCH_MAX','LIM_PITCH_MIN','TECS_PITCH_MAX','TECS_PITCH_MIN',
          'TECS_THR_DAMP','TECS_LAND_TDAMP','TECS_INTEG_GAIN','TECS_TKOFF_IGAIN',
          'TECS_LAND_IGAIN','THR_SLEWRATE','LAND_THR_SLEW','TRIM_THROTTLE',
          'TRIM_PITCH_CD','KFF_THR2PTCH','TRIM_ARSPD_CM']
append_to_care_params(params)

params = ['TECS_SPDWEIGHT','TECS_LAND_SPDWGT','TECS_PTCH_DAMP','TECS_LAND_DAMP',
          'TECS_LAND_PDAMP','TECS_PTCH_FF_V0','TECS_PTCH_FF_K','TECS_VERT_ACC',
          'TECS_LAND_PMAX','LAND_PITCH_CD','LAND_TYPE']
append_to_care_params(params)

params = ['WP_MAX_RADIUS','WP_RADIUS','NAVL1_DAMPING','NAVL1_PERIOD','NAVL1_XTRACK_I']
append_to_care_params(params)
'''
'''
params = ['NAVL1_DAMPING','NAVL1_PERIOD']
append_to_care_params(params)
'''