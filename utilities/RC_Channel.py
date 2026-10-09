from enum import Enum

class CH_TYPE(Enum):
    RC_CHANNEL_TYPE_ANGLE = 0
    RC_CHANNEL_TYPE_RANGE = 1

class RC_Channel():
    def __init__(self):
        self.type_in    = CH_TYPE.RC_CHANNEL_TYPE_ANGLE
        self.high_in    = 0
        self.dead_zone  = 0
        self.reversed   = 0
        self.radio_min  = 1100
        self.radio_trim = 1500
        self.radio_max  = 1900
        self.radio_in   = 0
        self.control_in = 0

    def get_control_in(self, rc_in):
        self.update(rc_in)
        return self.control_in

    def set_range(self, high):
        self.type_in = CH_TYPE.RC_CHANNEL_TYPE_RANGE
        self.high_in = high

    def set_angle(self, angle):
        self.type_in = CH_TYPE.RC_CHANNEL_TYPE_ANGLE
        self.high_in = angle

    def set_default_dead_zone(self, dzone):
        self.dead_zone = dzone

    def set_reversed(self, rev):
        self.reversed = rev

    def update(self, rc_in):
        self.radio_in = rc_in
        if self.type_in == CH_TYPE.RC_CHANNEL_TYPE_RANGE:
            self.control_in = self.pwm_to_range()
        else:
            self.control_in = self.pwm_to_angle()

    def pwm_to_range(self):
        return self.pwm_to_range_dz(self.dead_zone)

    def pwm_to_angle(self):
        return self.pwm_to_angle_dz(self.dead_zone)

    def pwm_to_range_dz(self, _dead_zone):
        r_in = self.radio_in
        if self.reversed:
            r_in = self.radio_max - (r_in - self.radio_min)
        radio_trim_low = self.radio_min + _dead_zone
        if r_in > radio_trim_low:
            return self.high_in * (r_in - radio_trim_low) / (self.radio_max - radio_trim_low)
        return 0

    def pwm_to_angle_dz(self, _dead_zone):
        return self.pwm_to_angle_dz_trim(_dead_zone, self.radio_trim)

    def pwm_to_angle_dz_trim(self, _dead_zone, _trim):
        radio_trim_high = _trim + _dead_zone
        radio_trim_low  = _trim - _dead_zone

        reverse_mul = -1 if self.reversed else 1

        r_in = self.radio_in

        if r_in > radio_trim_high and self.radio_max != radio_trim_high:
            return reverse_mul * (self.high_in * (r_in - radio_trim_high)) / (self.radio_max - radio_trim_high)
        elif r_in < radio_trim_low and self.radio_min != radio_trim_low:
            return reverse_mul * (self.high_in * (r_in - radio_trim_low)) / (radio_trim_low - self.radio_min)
        else:
            return 0

SERVO_MAX = 4500
def main():
    ch = RC_Channel()
    ch.set_angle(SERVO_MAX)
    print(ch.get_control_in())

if __name__ == '__main__':
    main()