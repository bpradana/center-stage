import cv2
import mediapipe as mp
import sys
import argparse


def detect_face(image, detector):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = detector.process(image)

    if results.detections:
        bounding_boxes = [
            detection.location_data.relative_bounding_box for detection in results.detections]
    else:
        bounding_boxes = []

    return bounding_boxes


def draw_bounding_boxes(image, bounding_boxes, image_width, image_height):
    h, w, = image_height, image_width

    for box in bounding_boxes:
        bbox = int(box.xmin * w), int(box.ymin *
                                      h), int(box.width * w), int(box.height * h)
        cv2.rectangle(image, bbox, (0, 255, 0), 2)


def average_coordinate(bounding_boxes, image_width, image_height):
    x_sum = 0
    y_sum = 0
    for box in bounding_boxes:
        x_sum += (box.xmin + box.width/2) * image_width
        y_sum += (box.ymin + box.height/2) * image_height
    x_avg = x_sum / len(bounding_boxes)
    y_avg = y_sum / len(bounding_boxes)
    return x_avg, y_avg


def max_size(bounding_boxes, image_width, image_height):
    x_min = 100000
    y_min = 100000
    x_max = -100000
    y_max = -100000
    for box in bounding_boxes:
        x_min = min(x_min, box.xmin * image_width)
        y_min = min(y_min, box.ymin * image_height)
        x_max = max(x_max, (box.xmin + box.width) * image_width)
        y_max = max(y_max, (box.ymin + box.height) * image_height)
    return max(x_max-x_min, y_max-y_min)


def track_camera(image, target, position=(0, 0, 100), easing=0.05, size=100, padding=25):
    target_x, target_y, target_z = target
    x, y, z = position

    dx = target_x - x
    x += dx * easing / 3
    dy = target_y - y
    y += dy * easing / 3
    dz = target_z - z
    z += dz * easing

    z = z + padding

    cv2.circle(image, (int(x), int(y)), 10, (0, 0, 255), -1)
    cv2.rectangle(frame, (int(x - z), int(y - z)),
                  (int(x + z), int(y + z)), (255, 0, 0), 2)
    return x, y, z


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detect faces in a video stream.')
    parser.add_argument('--camera', help='Index of camera to be used')
    parser.add_argument('--height', help='Height of video frame')
    parser.add_argument('--width', help='Width of video frame')
    args = parser.parse_args(sys.argv[1:])

    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(int(args.camera) if args.camera else 0)

    width, height = int(args.width) if args.width else 960, int(
        args.height) if args.height else 540
    output_width, output_height = 540, 540
    pos_x, pos_y, pos_z = width//2, height//2, 100
    target_x, target_y, target_z = width//2, height//2, 100
    padding = 25
    easing = 0.25

    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7) as detector:
        while cap.isOpened():
            ret, frame = cap.read()
            frame = cv2.resize(frame, (width, height))
            output_frame = frame.copy()

            # Get Bounding Boxes
            bounding_boxes = detect_face(frame, detector)

            # Draw Bounding Boxes
            draw_bounding_boxes(frame, bounding_boxes, width, height)

            # Get Average Coordinate
            if bounding_boxes:
                target_x, target_y = average_coordinate(
                    bounding_boxes, width, height)

            # Track Camera Coordinate
            if bounding_boxes:
                target_z = max_size(bounding_boxes, width, height) // 2
            pos_x, pos_y, pos_z = track_camera(
                frame, (target_x, target_y, target_z), (pos_x, pos_y, pos_z), easing, target_z, padding)

            # Draw Camera
            a = int(pos_y - pos_z)
            b = int(pos_y + pos_z)
            c = int(pos_x - pos_z)
            d = int(pos_x + pos_z)
            if a < 0:
                a = 0
                b = int(0 + pos_z * 2)
            if b > height:
                b = height
                a = int(height - pos_z * 2)
            if c < 0:
                c = 0
                d = int(0 + pos_z * 2)
            if d > width:
                d = width
                c = int(width - pos_z * 2)

            output_frame = output_frame[a:b, c:d]
            output_frame = cv2.resize(
                output_frame, (output_width, output_height))

            cv2.imshow('Debug Screen', cv2.flip(frame, 1))
            cv2.imshow('Output', cv2.flip(output_frame, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                cap.release()
                break

    cap.release()
