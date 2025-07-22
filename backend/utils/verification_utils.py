#backend/utils/verification_utils.py
import cv2
import dlib
import numpy as np
import face_recognition
from scipy.spatial import distance as dist
from utils.performance_utils import timeit

predictor_path = "../assets/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
LEFT_EYE, RIGHT_EYE = list(range(36, 42)), list(range(42, 48))
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

def get_eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

@timeit
def run_face_verification(doc_path, video_path, max_frames=150):
    try:
        doc_img = face_recognition.load_image_file(doc_path)
        doc_encs = face_recognition.face_encodings(doc_img)
        if not doc_encs:
            return {"face_result": "No face in document", "score": 0, "liveness": "Failed", "blinks": 0, "max_angle": 0, "smile": "No"}

        doc_enc = doc_encs[0]
        cap, blink_count, max_angle, smile_found, best_score = cv2.VideoCapture(str(video_path)), 0, 0, False, 0
        blink_state, frame_num = "open", 0

        while frame_num < max_frames:
            ret, frame = cap.read()
            if not ret: break
            gray, rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if len(smile_cascade.detectMultiScale(gray, 1.8, 20)) > 0:
                smile_found = True

            encs = face_recognition.face_encodings(rgb)
            if encs:
                score = 1 - face_recognition.face_distance([doc_enc], encs[0])[0]
                best_score = max(best_score, round(score, 3))

            rects = detector(gray)
            for rect in rects:
                shape = predictor(gray, rect)
                points = np.array([[p.x, p.y] for p in shape.parts()])
                ear = (get_eye_aspect_ratio(points[LEFT_EYE]) + get_eye_aspect_ratio(points[RIGHT_EYE])) / 2.0
                if ear < 0.21 and blink_state == "open":
                    blink_count += 1
                    blink_state = "closed"
                elif ear >= 0.21 and blink_state == "closed":
                    blink_state = "open"
                left, right = np.mean(points[LEFT_EYE], axis=0), np.mean(points[RIGHT_EYE], axis=0)
                angle = np.degrees(np.arctan2(right[1]-left[1], right[0]-left[0]))
                max_angle = max(max_angle, abs(round(angle, 2)))

            frame_num += 1
        cap.release()

        return {
            "face_result": "Match" if best_score >= 0.5 else "No Match",
            "score": best_score,
            "liveness": f"Passed ({blink_count} blinks)" if blink_count >= 1 else f"Failed ({blink_count} blinks)",
            "blinks": blink_count,
            "max_angle": max_angle,
            "smile": "Yes" if smile_found else "No",
        }
    except Exception as e:
        return {"face_result": "Error", "score": 0, "liveness": "Error", "blinks": 0, "max_angle": 0, "smile": "No", "error": str(e)}
