import cv2
from hand_tracker import HandTracker
from controller import GestureController
from config import Config
from UIcontrol import ConfigEditor
from UIcontrol import run_ui


def main():
    should_start=run_ui()
    if not should_start:
        print("用户未保存配置，程序退出")
        return
    print("配置已保存，启动摄像头")

    cap = cv2.VideoCapture(Config.camera_index)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    tracker = HandTracker()
    controller = GestureController(Config)

    print("按 Q 键启用 / 关闭手势控制，ESC 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        #frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        results = tracker.process(frame)

        #tracker.draw(frame, results)
        controller.update(results)

        cv2.putText(
            frame,
            f"Control: {'ON' if Config.enable_control else 'OFF'}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0) if Config.enable_control else (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Keyboard: {'Arrow Keys' if not Config.fjkeys else 'F / J'}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Mouse: {'Hold' if not Config.select_click else 'Click'}"if not Config.fjkeys else"",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 0) ,#if not Config.fjkeys else (0, 0, 0)
            2
        )

        cv2.imshow("Gesture Control", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            Config.enable_control = not Config.enable_control

        if Config.enable_control:
            if key == ord('w'):
                Config.fjkeys = not Config.fjkeys
            if key == ord('e'):
                Config.select_click = not Config.select_click

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
