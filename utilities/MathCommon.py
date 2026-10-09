import math
FLT_ESPILON = 1.1920928955078125e-7

def safe_sqrt(v):
    return math.sqrt(v)

def rad2deg(rad):
    import numpy as np
    rad_array = np.array(rad)
    deg_array = rad_array*180/np.pi
    return deg_array

def constrain_float(v,min,max):
    if v < min:
        v = min
    if v > max:
        v = max
    return v

def is_negative(v):
    if v <= -1.0 * FLT_ESPILON:
        return True
    else:
        return False

def is_positive(v):
    if v >= FLT_ESPILON:
        return True
    else:
        return False

def is_zero(v):
    if abs(v) < FLT_ESPILON:
        return True
    else:
        return False

def sq(v):
    return v**2

def MIN(a,b):
    return a if a<b else b

def MAX(a,b):
    return a if a>b else b

def inv_sqrt_controller(output, p, D_max):
    if (is_positive(D_max) and is_zero(p)):
        return (output * output) / (2.0 * D_max);

    if ((is_negative(D_max) or is_zero(D_max)) and not is_zero(p)):
        return output / p;

    if ((is_negative(D_max) or is_zero(D_max)) and is_zero(p)):
        return 0.0;

    # calculate the velocity at which we switch from calculating the stopping point using a linear function to a sqrt function.
    linear_velocity = D_max / p;

    if (abs(output) < linear_velocity):
        # if our current velocity is below the cross-over point we use a linear function
        return output / p;

    linear_dist = D_max / sq(p);
    stopping_dist = (linear_dist * 0.5) + sq(output) / (2.0 * D_max);
    return stopping_dist if is_positive(output) else -stopping_dist

def sqrt_controller(error, p, second_ord_lim, dt):
    correction_rate = 0.0;
    if (is_negative(second_ord_lim) or is_zero(second_ord_lim)):
        # second order limit is zero or negative.
        correction_rate = error * p;
    elif (is_zero(p)):
        # P term is zero but we have a second order limit.
        if (is_positive(error)):
            correction_rate = safe_sqrt(2.0 * second_ord_lim * (error));
        elif (is_negative(error)):
            correction_rate = -safe_sqrt(2.0 * second_ord_lim * (-error));
        else:
            correction_rate = 0.0;
    else:
        # Both the P and second order limit have been defined.
        linear_dist = second_ord_lim / sq(p);
        if (error > linear_dist):
            correction_rate = safe_sqrt(2.0 * second_ord_lim * (error - (linear_dist / 2.0)));
        elif (error < -linear_dist):
            correction_rate = -safe_sqrt(2.0 * second_ord_lim * (-error - (linear_dist / 2.0)));
        else:
            correction_rate = error * p;

    if (not is_zero(dt)):
        # this ensures we do not get small oscillations by over shooting the error correction in the last time step.
        return constrain_float(correction_rate, -abs(error) / dt, abs(error) / dt);
    else:
        return correction_rate;


def LowPassFilter(sample, cutoff_freq, dt):
    if (cutoff_freq <= 0.0 or dt <= 0.0):
        return sample

    import numpy as np
    rc = 1/(2*np.pi*cutoff_freq);
    alpha = constrain_float(dt/(dt+rc), 0.0, 1.0);
    output = []
    output.append(sample[0]);
    for i in range(1,len(sample)):
        output.append(output[i-1] + (sample[i] - output[i-1]) * alpha)
    return alpha,output