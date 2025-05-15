import os
import cv2
import numpy as np
from ultralytics import YOLO
from sort import Sort
from frame import Frame


model = YOLO('yolo11s.pt')

tracker = Sort()

video_path = 'fruits.mp4'

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.", video_path)
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_dir = 'extracted_frames'
os.makedirs(output_dir, exist_ok=True)

fruit_classes = [
        49,
        46,
        47]

best_frames = {}

loop_target_frames = {}

beginning_of_new_target = True
cur_min_confd = 1.0
timestamp = 0

def select_and_cache(obj, cur_frame, time, first):
   class_id, x1, y1, x2, y2, obj_id, confd = map(int, obj)
   #print(class_id, x1, y1, x2, y2, obj_id, confd)
   content = cur_frame[y1:y2, x1:x2]

   quality = np.mean(cv2.Laplacian(content, cv2.CV_64F).var())

   #if first frame of class_id, save it
   if first:
       loop_target_frames["area"] = Frame(class_id, x1,x2,y1,y2, confd, quality, time, cur_frame)
       loop_target_frames["conf"] = Frame(class_id, x1,x2,y1,y2, confd, quality, time, cur_frame)
       loop_target_frames["qual"] = Frame(class_id, x1,x2,y1,y2, confd, quality, time, cur_frame)
       return

   #compare region area
   area_frame = loop_target_frames["area"]
   area_o = area_frame.get_area()
   area_n = (x2-x1)*(y2-y1)
   if (area_n>area_o):
       loop_target_frames["area"] = Frame(class_id, x1,y1,x2,y2, confd, quality, time, frame)

   #compare confd
   confd_frame = loop_target_frames["conf"]
   confd_o = confd_frame.get_confidence()
   if (confd > confd_o):
       loop_target_frames["conf"] = Frame(class_id, x1,y1,x2,y2, confd, quality, time, frame)

   #compare quality
   qual_frame = loop_target_frames["qual"]
   quality_o = qual_frame.get_quality()
   if quality > quality_o:
       loop_target_frames["qual"] = Frame(class_id, x1,y1,x2,y2, confd, quality, time, frame)

def choose_and_save_as_bestframe():
   loop_target_frames["area"].expand_to_square(frame_width, frame_height)
   loop_target_frames["conf"].expand_to_square(frame_width, frame_height)
   loop_target_frames["qual"].expand_to_square(frame_width, frame_height)

   loop_target_frames["area"].save_to_file("./extracted_frames/")
   loop_target_frames["conf"].save_to_file("./extracted_frames/")
   loop_target_frames["qual"].save_to_file("./extracted_frames/")


while cap.isOpened():
    timestamp = timestamp + 1
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    detections = []
    obj_id = 0
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls)
        confidence = float(box.conf[0])
        cur_min_confd = min(confidence, cur_min_confd)
        if class_id in fruit_classes:
            detections.append([class_id, x1, y1, x2, y2, obj_id, confidence])
            obj_id = obj_id + 1

    #tracked_objects = tracker.update(np.array(detections))
    confd_sorted_detections = sorted(detections, key=lambda x: x[-1], reverse=True)

    #if the max confidence less than 0.5, it means that a nother beginning
    if confd_sorted_detections[0][-1] < 0.5:
        if not beginning_of_new_target:
            beginning_of_new_target = True
            choose_and_save_as_bestframe()
            loop_target_frames={}
        continue

    for obj in confd_sorted_detections:
        #if no target in this frame, it IS the beginning of new target
        if beginning_of_new_target:
            select_and_cache(obj, frame, timestamp, True)
            beginning_of_new_target = False
        else:
            select_and_cache(obj, frame, timestamp, False)


choose_and_save_as_bestframe()

#for class_id, info in best_frames.items():
#    inner_class_id = info['class_id']
#    frame = info['frame']
#    frame_path = os.path.join(output_dir, f'fruit_{class_id}_id_{obj_id}.jpg')
#    cv2.imwrite(frame_path, frame)

cap.release()
cv2.destroyAllWindows()
