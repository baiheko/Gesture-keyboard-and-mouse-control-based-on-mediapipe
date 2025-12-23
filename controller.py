import pyautogui
import math
import time
import threading
from filters import LowPassFilter
from filters import AdaptiveFilter


class GestureController:
    def __init__(self, config):
        self.config = config
        #self.mouse_filter = LowPassFilter(config.smoothing)
        self.mouse_filter = AdaptiveFilter(
            slow_alpha=0.8,  # 静止时强平滑
            fast_alpha=0.2,  # 快速移动时弱平滑
            speed_threshold=25
        )
        self.key_state = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.mouse_down = False

        # # ====== 鼠标性能优化 ======
        # self.last_mouse_time = 0
        # self.mouse_interval = 0.03

        # ===== 输入插帧状态 =====
        self.last_real_pos = None
        self.last_real_time = None

        self.pred_pos = None
        self.velocity = (0.0, 0.0)

        self.running = True

        self.hand_present = False
        self.hand_lost_time = None
        self.hand_timeout = 0.15

        # 插帧参数
        # self.interp_hz = 120
        # self.interp_dt = 1.0 / self.interp_hz

        # 启动插帧线程
        self.thread = threading.Thread(
            target=self._interpolation_loop,
            daemon=True
        )
        self.thread.start()

        self.f_pressed = False
        self.j_pressed = False

        pyautogui.FAILSAFE = False

    def _interpolation_loop(self):
        while self.running:
            time.sleep(self.config.interp_dt)

            if not self.config.enable_control:
                continue
            if self.pred_pos is None:
                continue

            # 预测一步
            # px, py = self.pred_pos
            # vx, vy = self.velocity
            #
            # px += vx * self.interp_dt
            # py += vy * self.interp_dt
            #
            # self.pred_pos = (px, py)

            # 如果手已经消失一段时间，停止预测
            if not self.hand_present:
                if self.hand_lost_time and time.time() - self.hand_lost_time > self.hand_timeout:
                    self.velocity = (0.0, 0.0)
                    self.pred_pos = None
                    continue

            #follow_gain = 0.8  # 0~1，越大越跟手

            dx = self.target_pos[0] - self.pred_pos[0]
            dy = self.target_pos[1] - self.pred_pos[1]

            self.pred_pos = (
                self.pred_pos[0] + dx * self.config.follow_gain,
                self.pred_pos[1] + dy * self.config.follow_gain
            )
            speed = math.hypot(self.velocity[0], self.velocity[1])
            if speed > 15:
                pyautogui.moveTo(*self.pred_pos)
            else:
                real_pos1 = (self.pred_pos[0], self.pred_pos[1])
                real_pos1 = self.mouse_filter.apply(real_pos1)
                pyautogui.moveTo(real_pos1)

    def update(self, results):
        if not self.config.enable_control:
            return

        if not results.multi_hand_landmarks:
            # 标记手消失
            if self.hand_present:
                self.hand_lost_time = time.time()
                self.hand_present = False
            return

        for hand, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
        ):
            label = handedness.classification[0].label

            if not self.config.fjkeys:
                if label == "Right":
                    self._handle_mouse(hand)
                elif label == "Left":
                    self._handle_keyboard(hand)
            else:
                if label == "Right":
                    self._handle_keyboardj(hand)
                elif label == "Left":
                    self._handle_keyboardf(hand)

    def _handle_mouse(self, hand):
        # wrist = hand.landmark[0]
        # x, y = wrist.x, wrist.y
        #
        # screen_w, screen_h = pyautogui.size()
        # target = (
        #     x * screen_w * self.config.mouse_speed,
        #     y * screen_h * self.config.mouse_speed
        # )
        #
        # smooth_x, smooth_y = self.mouse_filter.apply(target)
        # # now = time.time()
        # # if now - self.last_mouse_time > self.mouse_interval:
        # #     pyautogui.moveTo(smooth_x, smooth_y)
        # #     self.last_mouse_time = now
        # pyautogui.moveTo(smooth_x, smooth_y)
        self.hand_present = True
        wrist = hand.landmark[self.config.mouse_finger_index]
        x, y = wrist.x, wrist.y

        screen_w, screen_h = pyautogui.size()
        real_pos = (
            x * screen_w * self.config.mouse_speed,
            y * screen_h * self.config.mouse_speed
        )
        self.target_pos = real_pos
        real_pos = self.mouse_filter.apply(real_pos)

        now = time.time()

        if self.last_real_pos is not None:
            dt = now - self.last_real_time
            if dt > 0:
                vx = (real_pos[0] - self.last_real_pos[0]) / dt
                vy = (real_pos[1] - self.last_real_pos[1]) / dt
                self.velocity = (vx, vy)

        # 强制重对齐
        self.pred_pos = real_pos
        self.last_real_pos = real_pos
        self.last_real_time = now

        # 简单握拳检测
        #fingertips = [8]
        # avg_dist = sum(
        #     math.hypot(
        #         hand.landmark[i].x - wrist.x,
        #         hand.landmark[i].y - wrist.y
        #     )
        #     for i in fingertips
        # )

        dx = hand.landmark[8].x - hand.landmark[4].x
        dy = hand.landmark[8].y - hand.landmark[4].y

        is_fistmouse = dx * dx + dy * dy < self.config.fist_threshold

        if is_fistmouse and not self.mouse_down:
            if not self.config.select_click:
                pyautogui.mouseDown()
            else:
                pyautogui.click()
            self.mouse_down = True
        elif not is_fistmouse and self.mouse_down:
            if not self.config.select_click:
                pyautogui.mouseUp()
            self.mouse_down = False

    def _handle_keyboard(self, hand):
        base = hand.landmark[5]
        tip = hand.landmark[8]

        dx = tip.x - base.x
        dy = tip.y - base.y

        new_state = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        if abs(dx) > abs(dy):
            if dx > self.config.direction_threshold:
                new_state["right"] = True
            elif dx < -self.config.direction_threshold:
                new_state["left"] = True
        else:
            if dy > self.config.direction_threshold:
                new_state["down"] = True
            elif dy < -self.config.direction_threshold:
                new_state["up"] = True

        for key in new_state:
            if new_state[key] and not self.key_state[key]:
                pyautogui.keyDown(key)
                self.key_state[key] = True
            elif not new_state[key] and self.key_state[key]:
                pyautogui.keyUp(key)
                self.key_state[key] = False

    def _handle_keyboardf(self, hand):
        base = hand.landmark[4]
        tip = hand.landmark[8]

        dx = tip.x - base.x
        dy = tip.y - base.y

        is_fist = dx * dx + dy * dy < self.config.fj_fist_threshold

        # ===== 边沿触发 =====
        if is_fist and not self.f_pressed:
            pyautogui.press("f")
            self.f_pressed = True

        if not is_fist:
            self.f_pressed = False

    def _handle_keyboardj(self, hand):
        base = hand.landmark[4]
        tip = hand.landmark[8]

        dx = tip.x - base.x
        dy = tip.y - base.y

        is_fist = dx * dx + dy * dy < self.config.fj_fist_threshold

        if is_fist and not self.j_pressed:
            pyautogui.press("j")
            self.j_pressed = True

        if not is_fist:
            self.j_pressed = False
