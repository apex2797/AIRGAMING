#Developed by SIRAJ

import tensorflow as tf
import cv2
import multiprocessing as _mp
from utils import load_graph, detect_hands, predict
from utils import ORANGE, RED, GREEN
from pyKey import pressKey, releaseKey, press

width = 640
height = 480
threshold = 0.6
alpha = 0.3
pre_trained_model_path = "model/pretrained_model.pb"


def main():
    
    graph, sess = load_graph(pre_trained_model_path)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    mp = _mp.get_context("spawn")
    v = mp.Value('i', 0)
    lock = mp.Lock()
    
    while True:
        key = cv2.waitKey(10)
        if key == ord("q"):
            break
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, scores, classes = detect_hands(frame, graph, sess)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        results = predict(boxes, scores, classes, threshold, width, height)

        if len(results) == 1:
            x_min, x_max, y_min, y_max, category = results[0]
            x = int((x_min + x_max) / 2)
            y = int((y_min + y_max) / 2)
            cv2.circle(frame, (x, y), 5, RED, -1)

            if category == "Open" and x <= width / 3:
                action = 7  # Left
                text = "Left move"
                releaseKey("LEFT")
                press('LEFT', 0.15)
                pressKey("UP")
            
            elif category == "Open" and width / 3 < x <= 2 * width / 3:
                action = 5  # Straight
                releaseKey('LEFT')
                releaseKey("RIGHT")
                releaseKey("DOWN")
                pressKey("UP")
                text = "Straight"
            
            elif category == "Open" and x > 2 * width / 3:
                action = 2  # Right
                text = "Right move"
                releaseKey("RIGHT")
                press("RIGHT", 0.15)
                pressKey('UP')
                
            else:
                action = 0 #break and backward
                text = "Break and Back"
                releaseKey('LEFT')
                releaseKey("RIGHT")
                releaseKey("UP")
                pressKey("DOWN")

            
            with lock:
                v.value = action
            cv2.putText(frame, "{}".format(text), (x_min, y_min - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 2)
            
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (int(width / 3), height), ORANGE, -1)
        cv2.rectangle(overlay, (int(2 * width / 3), 0), (width, height), ORANGE, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.imshow('Detection', frame)
        
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

