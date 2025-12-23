# UIcontrol.py
import tkinter as tk
from tkinter import ttk, messagebox
import config
import config_saved
import os


class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("参数配置调节器")
        self.root.geometry("670x750")
        self.root.resizable(True, True)
        self.saved = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 主框架 + 滚动区
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 存储参数变量
        self.variables = {}

        # 创建控件
        self.create_widgets(self.scrollable_frame)

        # 操作按钮区
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        # self.apply_button = ttk.Button(btn_frame, text="应用（实时生效）", command=self.apply_all)
        # self.apply_button.pack(side=tk.LEFT, padx=(0, 8))

        self.reset_button = ttk.Button(btn_frame, text="恢复默认", command=self.reset_from_config)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 8))

        self.save_button = ttk.Button(btn_frame, text="保存", command=self.save_config)
        self.save_button.pack(side=tk.LEFT, padx=(0, 8))

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 -按 保存 按钮将当前值写入 config")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_widgets(self, parent):
        S = ttk.Style()
        S.configure("TLabel", font=("Arial", 10))
        S.configure("Header.TLabel", font=("SimHei", 12, "bold"))

        # ---------------- 摄像头设置 ----------------
        ttk.Label(parent, text="摄像头设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="摄像头索引:", width=20).pack(side=tk.LEFT)
        # 使用 Spinbox（整数）
        self.variables["camera_index"] = tk.IntVar(value=config.Config.camera_index)
        spin = tk.Spinbox(frame, from_=0, to=10, textvariable=self.variables["camera_index"], width=6)
        spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, text="若画面异常可尝试 0/1/2").pack(side=tk.LEFT, padx=6)

        # ---------------- 鼠标移动设置 ----------------
        ttk.Label(parent, text="鼠标移动设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        # 鼠标灵敏度（Scale + 实时显示）
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="鼠标速度:", width=20).pack(side=tk.LEFT)
        self.variables["mouse_speed"] = tk.DoubleVar(value=config.Config.mouse_speed)
        s = ttk.Scale(frame, from_=0.1, to=5.0, variable=self.variables["mouse_speed"],
                      command=lambda v: self.update_label(v, "mouse_speed"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["mouse_speed_label"] = ttk.Label(frame, text=f"{config.Config.mouse_speed:.2f}", width=8)
        self.variables["mouse_speed_label"].pack(side=tk.LEFT)

        # 平滑度
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="平滑度:", width=20).pack(side=tk.LEFT)
        self.variables["smoothing"] = tk.DoubleVar(value=config.Config.smoothing)
        s = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables["smoothing"],
                      command=lambda v: self.update_label(v, "smoothing"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["smoothing_label"] = ttk.Label(frame, text=f"{config.Config.smoothing:.2f}", width=8)
        self.variables["smoothing_label"].pack(side=tk.LEFT)

        # ---------------- 鼠标判定 ----------------
        ttk.Label(parent, text="鼠标点击判定设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="捏指阈值:", width=20).pack(side=tk.LEFT)
        self.variables["fist_threshold"] = tk.DoubleVar(value=config.Config.fist_threshold)
        s = ttk.Scale(frame, from_=0.0, to=0.01, variable=self.variables["fist_threshold"],
                      command=lambda v: self.update_label(v, "fist_threshold"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["fist_threshold_label"] = ttk.Label(frame, text=f"{config.Config.fist_threshold:.6f}", width=12)
        self.variables["fist_threshold_label"].pack(side=tk.LEFT)

        # 方向键触发阈值
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="方向键触发阈值:", width=20).pack(side=tk.LEFT)
        self.variables["direction_threshold"] = tk.DoubleVar(value=config.Config.direction_threshold)
        s = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables["direction_threshold"],
                      command=lambda v: self.update_label(v, "direction_threshold"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["direction_threshold_label"] = ttk.Label(frame, text=f"{config.Config.direction_threshold:.2f}",
                                                                width=8)
        self.variables["direction_threshold_label"].pack(side=tk.LEFT)

        # ---------------- 插帧参数 ----------------
        ttk.Label(parent, text="插帧参数设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        # 插帧频率
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="插帧频率:", width=20).pack(side=tk.LEFT)
        self.variables["interp_hz"] = tk.IntVar(value=config.Config.interp_hz)
        s = ttk.Scale(frame, from_=30, to=240, variable=self.variables["interp_hz"],
                      command=lambda v: self.update_label(v, "interp_hz"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["interp_hz_label"] = ttk.Label(frame, text=str(config.Config.interp_hz), width=8)
        self.variables["interp_hz_label"].pack(side=tk.LEFT)

        # 跟手度
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="跟手度:", width=20).pack(side=tk.LEFT)
        self.variables["follow_gain"] = tk.DoubleVar(value=config.Config.follow_gain)
        s = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables["follow_gain"],
                      command=lambda v: self.update_label(v, "follow_gain"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["follow_gain_label"] = ttk.Label(frame, text=f"{config.Config.follow_gain:.2f}", width=8)
        self.variables["follow_gain_label"].pack(side=tk.LEFT)

        # ---------------- FJ 键控制 ----------------
        ttk.Label(parent, text="FJ键控制设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        self.variables["fjkeys"] = tk.BooleanVar(value=config.Config.fjkeys)
        # ttk.Checkbutton(frame, text="启用 F/J 键控制 (F=右手/ J=左手)",
        #                 variable=self.variables["fjkeys"],
        #                 command=lambda: self.update_config("fjkeys", self.variables["fjkeys"].get())).pack(anchor=tk.W)

        # FJ 捏指阈值
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="FJ捏指阈值:", width=20).pack(side=tk.LEFT)
        self.variables["fj_fist_threshold"] = tk.DoubleVar(value=config.Config.fj_fist_threshold)
        s = ttk.Scale(frame, from_=0.0, to=0.01, variable=self.variables["fj_fist_threshold"],
                      command=lambda v: self.update_label(v, "fj_fist_threshold"), orient=tk.HORIZONTAL, length=260)
        s.pack(side=tk.LEFT, padx=5)
        self.variables["fj_fist_threshold_label"] = ttk.Label(frame, text=f"{config.Config.fj_fist_threshold:.6f}",
                                                              width=12)
        self.variables["fj_fist_threshold_label"].pack(side=tk.LEFT)

        # ---------------- 系统设置 ----------------
        #ttk.Label(parent, text="系统设置", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        self.variables["enable_control"] = tk.BooleanVar(value=config.Config.enable_control)
        # ttk.Checkbutton(frame, text="启用手势控制 (运行时生效)",
        #                 variable=self.variables["enable_control"],
        #                 command=lambda: self.update_config("enable_control", self.variables["enable_control"].get())).pack(anchor=tk.W)

        # 小提示
        ttk.Label(parent,
                  text="说明：阈值类值设置的越大，越容易触发，可根据手的大小自行调整。\n此外，除了摄像头索引外不建议更改任何值 : )",
                  wraplength=560, foreground="gray").pack(anchor=tk.W, pady=(8, 12))

    def update_label(self, value, param_name):
        """更新 UI 上的数值显示并（立即）更新 config.Config 的对应字段"""
        # 注意：Scale 的 command 返回 str，所以都用 float(...)/int(...)
        if param_name in ["camera_index", "interp_hz"]:
            int_value = int(float(value))
            self.variables[f"{param_name}_label"]["text"] = str(int_value)
            # 直接更新 Var（但不会写文件）
            self.variables[param_name].set(int_value)
            self.update_config(param_name, int_value)
        elif param_name in ["fist_threshold", "fj_fist_threshold"]:
            fv = float(value)
            self.variables[f"{param_name}_label"]["text"] = f"{fv:.6f}"
            self.variables[param_name].set(fv)
            self.update_config(param_name, fv)
        elif param_name in ["mouse_speed", "smoothing", "direction_threshold", "follow_gain"]:
            fv = float(value)
            # 显示不同的小数位
            if param_name == "direction_threshold":
                self.variables[f"{param_name}_label"]["text"] = f"{fv:.2f}"
            else:
                self.variables[f"{param_name}_label"]["text"] = f"{fv:.2f}"
            self.variables[param_name].set(fv)
            self.update_config(param_name, fv)
        elif param_name == "interp_hz":
            iv = int(float(value))
            self.variables["interp_hz_label"]["text"] = str(iv)
            self.variables["interp_hz"].set(iv)
            # 同步 interp_dt
            dt = 1.0 / max(iv, 1)
            self.update_config("interp_hz", iv)
            # 写回 interp_dt 计算值
            setattr(config.Config, "interp_dt", dt)
        else:
            # 兜底行为
            try:
                fv = float(value)
                self.update_config(param_name, fv)
            except Exception:
                self.update_config(param_name, value)

    def update_config(self, param_name, value):
        """把值写回 config.Config（即时生效）"""
        if not hasattr(config.Config, param_name):
            return
        # 强制转换类型
        if isinstance(getattr(config.Config, param_name, None), bool):
            if isinstance(value, str):
                v = value.lower() in ["1", "true", "yes"]
            else:
                v = bool(value)
            setattr(config.Config, param_name, v)
        elif isinstance(getattr(config.Config, param_name, None), int):
            setattr(config.Config, param_name, int(value))
        elif isinstance(getattr(config.Config, param_name, None), float):
            setattr(config.Config, param_name, float(value))
        else:
            setattr(config.Config, param_name, value)

        self.status_var.set(f"设置: {param_name} = {getattr(config.Config, param_name)}")

    def apply_all(self):
        """按下应用：把 UI 中当前值全部写回 config"""
        for k, var in self.variables.items():
            # 只处理参数变量（排除 label）
            if k.endswith("_label"):
                continue
            val = var.get()
            self.update_config(k, val)
        # 重新计算 interp_dt
        try:
            config.Config.interp_dt = 1.0 / max(int(config.Config.interp_hz), 1)
        except Exception:
            pass
        self.status_var.set("已应用当前值到 config（运行时生效）")

    # def reset_from_config(self):
    #     """从当前的 config.Config 读取并刷新 UI"""
    #     for k, var in list(self.variables.items()):
    #         if k.endswith("_label"):
    #             continue
    #         if hasattr(config.Config, k):
    #             val = getattr(config.Config, k)
    #             try:
    #                 var.set(val)
    #             except Exception:
    #                 # 忽略无法 set 的
    #                 pass
    def reset_from_config(self):
        """从 config_saved.Config 读取默认值，覆盖 config.Config 并刷新 UI"""
        # 1. 遍历 UI 变量，从 config_saved 读取默认值
        for k, var in list(self.variables.items()):
            if k.endswith("_label"):
                continue
            # 检查 config_saved 是否有该配置项
            if hasattr(config_saved.Config, k):
                # 读取默认值
                default_val = getattr(config_saved.Config, k)
                try:
                    # 2. 覆盖 config.Config 的值
                    self.update_config(k, default_val)
                    # 3. 刷新 UI 变量的值
                    var.set(default_val)
                except Exception as e:
                    # 打印异常（便于调试）
                    print(f"恢复默认值失败 - {k}: {e}")
                    pass

        # 4. 手动刷新所有 label 显示（确保数值标签同步）
        self.update_label(self.variables["mouse_speed"].get(), "mouse_speed")
        self.update_label(self.variables["smoothing"].get(), "smoothing")
        self.update_label(self.variables["fist_threshold"].get(), "fist_threshold")
        self.update_label(self.variables["direction_threshold"].get(), "direction_threshold")
        self.update_label(self.variables["interp_hz"].get(), "interp_hz")
        self.update_label(self.variables["follow_gain"].get(), "follow_gain")
        self.update_label(self.variables["fj_fist_threshold"].get(), "fj_fist_threshold")

        # 5. 特殊处理 interp_dt（由 interp_hz 计算）
        try:
            config.Config.interp_dt = 1.0 / max(int(config_saved.Config.interp_hz), 1)
        except Exception:
            pass

        # 更新状态栏提示
        self.status_var.set("已恢复默认配置（从 config_saved 读取）")
        # 弹窗提示（可选）
        messagebox.showinfo("成功", "已恢复所有参数为默认值！")

        # 手动刷新 label 显示
        self.update_label(self.variables["mouse_speed"].get(), "mouse_speed")
        self.update_label(self.variables["smoothing"].get(), "smoothing")
        self.update_label(self.variables["fist_threshold"].get(), "fist_threshold")
        self.update_label(self.variables["direction_threshold"].get(), "direction_threshold")
        self.update_label(self.variables["interp_hz"].get(), "interp_hz")
        self.update_label(self.variables["follow_gain"].get(), "follow_gain")
        self.update_label(self.variables["fj_fist_threshold"].get(), "fj_fist_threshold")
        self.status_var.set("已从 config.py 读取当前配置并刷新 UI")

    def save_config(self):
        self.apply_all()
        self.saved = True
        """把当前配置写回 config.py（覆盖）"""
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                f.write("class Config:\n")
                f.write("    # 摄像头\n")
                f.write(f"    camera_index = {config.Config.camera_index}\n\n")

                f.write("    # 鼠标移动\n")
                f.write(f"    mouse_speed = {config.Config.mouse_speed:.6f}  # 鼠标灵敏度\n")
                f.write(f"    smoothing = {config.Config.smoothing:.6f}  # 0~1，越大越平滑\n\n")
                f.write(f"    mouse_finger_index = {config.Config.mouse_finger_index} \n\n")

                f.write("    # click or hold\n")
                f.write(f"    select_click = {str(config.Config.select_click)} \n\n")

                f.write("    # 捏指判定\n")
                f.write(f"    fist_threshold = {config.Config.fist_threshold:.6f}  # 越小越容易判定为捏指\n\n")

                f.write("    # 方向键触发\n")
                f.write(f"    direction_threshold = {config.Config.direction_threshold:.6f}\n\n")

                f.write("    # 插帧参数\n")
                f.write(f"    interp_hz = {config.Config.interp_hz}\n")
                f.write(f"    interp_dt = 1.0 / {config.Config.interp_hz}\n\n")

                f.write(f"    follow_gain = {config.Config.follow_gain:.6f}  # 0~1，越大越跟手\n\n")

                f.write("    # f,j键控制\n")
                f.write(f"    fjkeys = {str(config.Config.fjkeys)}\n")
                f.write(f"    fj_fist_threshold = {config.Config.fj_fist_threshold:.6f}\n\n")

                f.write("    # 系统\n")
                f.write(f"    enable_control = {str(config.Config.enable_control)}  # 是否启用手势控制\n")
            self.status_var.set("配置已保存到 config.py")
            messagebox.showinfo("成功", f"配置已成功保存到 {os.path.abspath('config.py')}")
            self.on_close()
        except Exception as e:
            self.status_var.set(f"保存失败: {str(e)}")
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}")

    def on_close(self):
        self.root.destroy()


def run_ui():
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
    return app.saved
