import math


class LowPassFilter:
    def __init__(self, alpha=0.8):
        self.alpha = alpha
        self.last = None

    def apply(self, value):
        if self.last is None:
            self.last = value
        self.last = (
            self.alpha * self.last[0] + (1 - self.alpha) * value[0],
            self.alpha * self.last[1] + (1 - self.alpha) * value[1]
        )
        return self.last


class AdaptiveFilter:
    def __init__(self, slow_alpha=0.7, fast_alpha=0.3, speed_threshold=15):
        self.slow_alpha = slow_alpha
        self.fast_alpha = fast_alpha
        self.speed_threshold = speed_threshold
        self.last = None

    def apply(self, value):
        if self.last is None:
            self.last = value
            return value

        dx = value[0] - self.last[0]
        dy = value[1] - self.last[1]
        speed = math.hypot(dx, dy)

        # 根据速度选择不同平滑强度
        alpha = self.fast_alpha if speed > self.speed_threshold else self.slow_alpha

        self.last = (
            alpha * self.last[0] + (1 - alpha) * value[0],
            alpha * self.last[1] + (1 - alpha) * value[1]
        )
        return self.last
