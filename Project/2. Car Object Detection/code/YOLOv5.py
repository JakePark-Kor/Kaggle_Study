#from lib2to3.pytree import _Results
import torch
import numpy as np
import cv2
import pafy
from time import time

class ObjectDetection:
    """
    Class implements YOLOv5 model to make inferences 
    on a youtube video using OpenCV                                                 
    """

    def __init__(self, url, out_file):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL, on which prediction is made.
        :param out_file: A valid output file name.

        """
        self._URL = url
        self.model = self.load_model()
        self.classes = self.model.names
        self.out_file = out_file
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    
    def get_video_from_url(self):
        """
        Create a new video streaming object to extract video frame by frame 
        to make prediction on.
        return: OpenCV2 video capture object, with lowest quality frame abailable for video.
        """

        play = pafy.new(self._URL).stream[-1]
        assert play is not None
        return cv2.VideoCapture(play.url)

    def load_model(self):
        """
        Loads YOLO5 model for pytorch hub.
        return: Trained Pytorch model.
        """

        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained = True)

        return model

    def score_frame(self, frame):
        """
        Tales a single frame as input, and scores the frame using yolov5 model.
        :parameter frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordnates of objects detected by model in the frame
            """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)

        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, : -1]
            
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        Param x: Numeric label
        Return : Corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        Param results: contains labels and coordinates predicted by model on the given frame.
        Param frame : Frame which has been scored.
        Return: frame with bounding boxes and labels ploted on it.
        """

        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0]*x_shape, int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape), int(row[4]*x_shape))
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0 , 0) )

        return frame


    def __call__(self):
        """
        This function is called when class is executed, it runs the loop the loop to read the video frame by frame,
        and write the output into a new file.
        return: void
        """

        player = self.get_video_from_url()
        assert player.isOpened()
        x_shape = int(player.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_shape = int(player.get(cv2.CAP_PROP_FRAME_HEIGHT))
        four_cc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWirter(self.out_file, four_cc, 20, (x_shape, y_shape))

        while True:
            start_time = time()
            ret, frame = player.read()
            if not ret:
                break
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)
            end_time = time()  
            fps = 1/np.round(end_time - start_time, 3)
            print(f"Frames Per Second : {fps}")
            out.write(frame)



# Create a new object and execute.
detection = ObjectDetection("https://youtu.be/1_XzrxXnwMM", "video2.avi")
detection()




