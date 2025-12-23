class Config:
    # 摄像头
    camera_index = 1

    # 鼠标移动
    mouse_speed = 1.200000  # 鼠标灵敏度
    smoothing = 0.700000  # 0~1，越大越平滑

    mouse_finger_index = 0 

    # click or hold
    select_click = False 

    # 捏指判定
    fist_threshold = 0.002500  # 越小越容易判定为捏指

    # 方向键触发
    direction_threshold = 0.100000

    # 插帧参数
    interp_hz = 120
    interp_dt = 1.0 / 120

    follow_gain = 1.000000  # 0~1，越大越跟手

    # f,j键控制
    fjkeys = True
    fj_fist_threshold = 0.002500

    # 系统
    enable_control = False  # 是否启用手势控制
