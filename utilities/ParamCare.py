care_params = []

def append_to_care_params(params):
    for p in params:
        care_params.append(p)

# Roll Attitude
params = ['ATC_ANG_RLL_P','ATC_ACC_R_MAX','ATC_RAT_RLL_NTF','ATC_RAT_RLL_FLTT','ATC_RAT_RLL_NEF',
          'ATC_RAT_RLL_FF','ATC_RAT_RLL_D_FF','ATC_RAT_RLL_FLTE','ATC_RAT_RLL_P','ATC_RAT_RLL_I',
          'ATC_RAT_RLL_D','ATC_RAT_RLL_IMAX','ATC_RAT_RLL_FLTD','ATC_RAT_RLL_SMAX','ATC_RAT_RLL_PDMX']
append_to_care_params(params)

# Pitch Attitude
params = ['ATC_ANG_PIT_P','ATC_ACC_P_MAX','ATC_RAT_PIT_NTF','ATC_RAT_PIT_FLTT','ATC_RAT_PIT_NEF',
          'ATC_RAT_PIT_FF','ATC_RAT_PIT_D_FF','ATC_RAT_PIT_FLTE','ATC_RAT_PIT_P','ATC_RAT_PIT_I',
          'ATC_RAT_PIT_D','ATC_RAT_PIT_IMAX','ATC_RAT_PIT_FLTD','ATC_RAT_PIT_SMAX','ATC_RAT_PIT_PDMX']
append_to_care_params(params)
