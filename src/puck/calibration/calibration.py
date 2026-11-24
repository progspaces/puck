import numpy as np
import tkinter as tk
import cv2 as cv
from PIL import ImageTk, Image

CHESSBOARD_ROWS = 6
CHESSBOARD_COLS = 9
CHESSBOARD_FILE = "data/chessboard9by6.png"
CHESSBOARD_IMG = ImageTk.PhotoImage(Image.open(CHESSBOARD_FILE).resize((1000,700)))

class Calibration:
    camera_to_real: np.ndarray
    camera_to_proj: np.ndarray 
    real_to_proj: np.ndarray 

    def __init__(self, camera_to_real: np.ndarray, camera_to_proj: np.ndarray):
        self.camera_to_real = camera_to_real
        self.camera_to_proj = camera_to_proj
        self.real_to_proj = np.linalg.inv(self.camera_to_real) @ self.camera_to_proj


    def save(self, file_path: str) -> None:
        np.savez(file_path, camera_to_real = self.camera_to_real, camera_to_proj = self.camera_to_proj)

    @classmethod
    def load(cls, file_path: str) -> Calibration:
        zfile = np.load(file_path)
        return cls(zfile.camera_to_real,zfile.camera_to_proj)

def chessboard_matrix(gray_photos:list[np.ndarray], cam_view_canvas:tk.Canvas| None) -> np.ndarray:
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((CHESSBOARD_ROWS*CHESSBOARD_COLS,3), np.float32)
    objp[:,:2] = np.mgrid[0:CHESSBOARD_COLS,0:CHESSBOARD_ROWS].T.reshape(-1,2)

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    for gray_frame in gray_photos:
        #Use the generate_pattern.py Python script (Create Calibration Pattern) to create the desired checkerboard pattern.
        ret, corners = cv.findChessboardCorners(gray_frame, (CHESSBOARD_COLS, CHESSBOARD_ROWS), None)
        if ret == False:
            raise(BaseException("No Chessboard Found :("))
        
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray_frame,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        # If found, add object points, image points (after refining them)
        if cam_view_canvas is not None:
            img = cv.cvtColor(gray_frame, cv.COLOR_GRAY2BGR)
            cv.drawChessboardCorners(img , (CHESSBOARD_COLS,CHESSBOARD_ROWS), corners2, ret)
            # TODO: use cam_view_canvas instead
            cv.imshow('img', img)
            cv.waitKey(500)

    _, mtx, _, _, _ = cv.calibrateCamera(objpoints, imgpoints, gray_frame.shape[::-1], None, None)
    return mtx

def get_photos(cam:cv.VideoCapture, n: int) -> list[np.ndarray]:
    cal_photos = []
    if not cam.isOpened():
        raise OSError("Camera is not open")
    rval, frame = cam.read() 
    # TODO: refactor into tkinter
    # cv.imshow("preview", frame)
    # for c in range(n):
    #     while True:
    #         print(f"This is photo {c+1}")
    #         # key = cv.waitKey(0)
    #         rval, frame = cam.read() 
    #         if not rval:
    #             print("Something is wrong with the camera, rval is false, press a key when fixed")
    #         elif key == 112:  ##  press p
    #             ## refactor into tkinter
    #             # cv.imshow("preview", frame)
    #             pass
    #         elif key == 32: #space to capture
    #             break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cal_photos.append(gray)
    # TODO: refactor into tkinter
    # cv.destroyWindow("preview")
    cam.release()
    return cal_photos
    

def combo(cam: cv.VideoCapture, count: int, canvas: tk.Canvas | None) -> None:
    print(chessboard_matrix(get_photos(cam, count), canvas))


def project_chessboard(canvas:tk.Canvas) -> None:
    canvas.create_image(400, 100, image=CHESSBOARD_IMG, anchor = tk.NW)
    print("hello")


def make_camera_to_real():
    ## open camera
    ## show paper chessboard
    ## take a photo
    ## run finding 
    pass



def make_camera_to_proj():
    ## open camera
    ## project chessboard
    ## take a photo
    ## run finding 
    pass

