import os
import cv2

class Frame:
    def __init__(self, class_id, x1, x2, y1, y2, confidence, quality, timestamp, opencv_frame):
        self.class_id = class_id
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.opencv_frame = opencv_frame
        self.timestamp = timestamp
        self.quality = quality
        self.confidence = confidence
        self.area = self.calculate_area()

    def calculate_area(self):
        return abs(self.x2 - self.x1) * abs(self.y2 - self.y1)

    def get_class_id(self):
        return self.class_id

    def get_position(self):
        return self.x1, self.x2, self.y1, self.y2

    def get_opencv_frame(self):
        return self.opencv_frame

    def get_timestamp(self):
        return self.timestamp

    def get_quality(self):
        return self.quality

    def get_confidence(self):
        return self.confidence

    def get_area(self):
        return self.area

    def get_center(self) -> [float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def save_to_file(self, output_dir="./"):
        class_id = self.class_id
        time = self.timestamp
        frame_path = os.path.join(output_dir, f'fruit_{class_id}_id_{time}.jpg')
        cv2.imwrite(frame_path, self.opencv_frame)
        return

    def expand_to_square(self, img_width, img_height):
        width  = self.x2 - self.x1
        height = self.y2 - self.y1

        side_length = max(width, height)

        center_x, center_y = self.get_center()

        new_x1 = int(center_x - side_length / 2)
        new_y1 = int(center_y - side_length / 2)
        new_x2 = int(center_x + side_length / 2)
        new_y2 = int(center_y + side_length / 2)

        new_x1 = max(0, new_x1)
        new_y1 = max(0, new_y1)
        new_x2 = min(img_width, new_x2)
        new_y2 = min(img_height, new_y2)

        if new_x2 - new_x1 < side_length:
            if new_x1 > 0:
                new_x1 -= (side_length - (new_x2 - new_x1))
            else:
                new_x2 += (side_length - (new_x2 - new_x1))

        if new_y2 - new_y1 < side_length:
            if new_y1 > 0:
                new_y1 -= (side_length - (new_y2 - new_y1))
            else:
                new_y2 += (side_length - (new_y2 - new_y1))

        self.x1 = max(0, new_x1)
        self.y1 = max(0, new_y1)
        self.x2 = min(img_width, new_x2)
        self.y2 = min(img_height, new_y2)

        return new_x1, new_y1, new_x2, new_y2



## 示▒~K使▒~T▒
#if __name__ == "__main__":
#    # ▒~H~[建▒~@个示▒~K帧
#    example_frame = cv2.imread("example.jpg")  # ▒~A~G设▒~\~I▒~@个▒~[▒▒~I~G▒~V~G件
#    frame = Frame(
#        class_id=1,
#        x1=100,
#        x2=300,
#        y1=150,
#        y2=450,
#        opencv_frame=example_frame,
#        timestamp=10.5,
#        quality=0.9,
#        confidence=0.85
#    )
#
#    # ▒~N▒▒~O~V并▒~I~S▒~M▒▒~H~P▒~Q~X▒~O~X▒~G~O
#    print("Class ID:", frame.get_class_id())
#    print("Position:", frame.get_position())
#    print("Timestamp:", frame.get_timestamp())
#    print("Quality:", frame.get_quality())
#    print("Confidence:", frame.get_confidence())
#    print("Area:", frame.get_area())
