class SecondOrderComplementaryFilter:
    def __init__(self,K):
        self.output = 0
        self.K = K
        self.y = 0
        self.dt = 0.02
    def set_dt(self,dt):
        self.dt = dt
    def init(self,output):
        self.output = output
    def reset(self):
        self.output = 0
        self.y = 0
    def apply(self,x,dx):
        error = x - self.output
        x = error * self.K * self.K
        # Prevent state from winding up
        if self.output < 3.1:
            x = max(x, 0)
        self.y = self.y + x * self.dt
        i = self.y + dx + error * self.K * 1.4142
        self.output = self.output + i * self.dt
        return self.output