
import cv2
import depthai as dai
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class CameraInput(QObject):
	frame_updated = pyqtSignal(np.ndarray)

	disparityQueue = 0
	disparityMultiplier = 0
	referenceFrame = 0

	MEASURED_AVERAGE = 255/771.665 #(max_dist-min_dist)/2+min_dist then converted to 0->255 range

	ESTIMATED_SAFE_VALUE = 140 # Camera pointed about 30 degrees down 14 inches from the ground reads this pretty consistently
	WARNING_THRESHOLD = 5
	DANGER_THRESHOLD =  10

	CAM_WIDTH = 640
	CAM_HEIGHT = 400

	# At the moment, the camera is 45 cm from the ground, pointed 30 degrees downward
	MOUNT_ELEVATION = 45
	MOUNT_ANGLE = -30

	HFOV = 71.9 # Horizontal field of view
	VFOV = 50.0 # Vertical field of view
	BASELINE = 7.5 # Distance between stereo cameras in cm
	FOCAL = 883.15 # Magic number needed for disparity -> depth calculation

	WINDOW = "Indoor Navigation Depth Map (Collision Detection)"

	def get_frame(self, queue):
		# Get frame from queue
		frame = queue.get()
		# Convert frame to OpenCV format
		return frame.getCvFrame()

	def get_mono_camera(self, pipeline, isLeft):
		mono = pipeline.createMonoCamera()

		mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

		if isLeft:
			mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
		else:
			mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
		return mono

	def get_stereo_pair(self, pipeline, monoLeft, monoRight):
		stereo = pipeline.createStereoDepth()

		# Turn on occlusion check (small performance hit, but output is less noisy)
		stereo.setLeftRightCheck(True)
		# Link mono cameras to the stereo pair
		monoLeft.out.link(stereo.left)
		monoRight.out.link(stereo.right)

		return stereo

	def get_reference(self,):
		referenceFrame = np.zeros((self.CAM_HEIGHT, self.CAM_WIDTH)) # same dimensions as images from the camera

		# Iterating in interpreted python instead of numpy
		# This is slow, but we only do this once at startup
		# for y in range(0, CAM_HEIGHT):
		# 	# Angle of the current pixel
		# 	theta = ((1.0-(y / CAM_HEIGHT)) * VFOV) - (VFOV / 2) + MOUNT_ANGLE

		# 	brightness = depthToBrightness(MOUNT_ELEVATION / (abs(math.tan(math.radians(theta)))))

		# 	for x in range(0, CAM_WIDTH):
		# 		referenceFrame[y][x] = brightness

		# generate an array of theta values based on VFOV and MOUNT_ANGLE
		theta = np.linspace(-(self.VFOV / 2) + self.MOUNT_ANGLE, self.VFOV / 2 + self.MOUNT_ANGLE, self.CAM_HEIGHT)
		# calculate elevation factor
		elevation_factor = self.MOUNT_ELEVATION / np.tan(np.radians(theta))
		# get an array of brightness values
		brightness = self.depth_to_brightness(elevation_factor)
		# tile brightness array along the second axis CAM_WIDTH times and create the referenceFrame array
		reference_frame = np.tile(brightness[:, np.newaxis], (1, self.CAM_WIDTH))

		return reference_frame.astype(np.uint8)

	# Image brightness (0 to 255) to depth (cm)
	# Ideally we'd use disparity to depth, but our test cases already map disparity from
	# 0 to 255, while the raw disparity value is 0 to 95, so we convert brightness to
	# disparity first, then disparity to depth.
	def brightness_to_depth(self, b):
		disparity = (95 * b) / 255

		return self.BASELINE * self.FOCAL / disparity

	def depth_to_brightness(self, d):
		disparity = self.BASELINE * self.FOCAL / d

		return disparity

	'''
		Analyzes a given frame compared to what is considered a safe reference image
		returns the danger value, and a new frame which highlights dangerous areas in white
	'''
	def analyze_frame(frame, referenceFrame):
		frame = np.where(frame!=0, frame, referenceFrame) # replace unknown values with whatever value is expected

		# we then find the difference between the expected depth and actual depth

		# terrible no-good bad hacky workaround for underflow during subtraction:
		# frame = np.clip( np.abs(np.subtract(frame.astype(np.int16), referenceFrame.astype(np.int16))), 0, 255 ).astype(np.uint8)
		# essentially, cast both operands to int16, subtract, get absolute value, clamp to [0,255], cast back to uint8

		# determine the sign of the subtraction result
		mask = frame >= referenceFrame
		# if frame >= referenceFrame, positive result so do frame - referenceFrame
		# if frame < referenceFrame, negative result so do referenceFrame - frame
		frame = np.where(mask, frame - referenceFrame, referenceFrame - frame)
		# clip to between 0 and 255, and cast to uint8
		frame = np.minimum(frame, 255).astype(np.uint8)

		# we're now left with an image where black means expected, white means unexpected.
		# therefore, looking for white in the image gives an estimate of danger

		# experimentally, an average value of 50 is extreme danger
		# so we just divide by 5 to get a decent 0-10 danger value
		# there's some issues with the math so an empty room gives danger of like, 2? but that's fine for now
		danger = np.clip(int(np.mean(frame) / 5), 0, 10)
		return danger, frame

	# UI helper functions to workaround lambda arguments
	def make_slider(self, name, window, a_min, a_max):
		cv2.createTrackbar(name, window, a_min, a_max, (lambda x: x))
		cv2.setTrackbarPos(name, window, int((a_min+a_max)/2))

	def set_slider(self, name, window, val):
		cv2.setTrackbarPos(name,window,val)

	def setup(self):
		pipeline = dai.Pipeline()

		# Get side cameras
		monoLeft = self.get_mono_camera(pipeline, isLeft=True)
		monoRight = self.get_mono_camera(pipeline, isLeft=False)

		stereo = self.get_stereo_pair(pipeline, monoLeft, monoRight)

		xOutDisp = pipeline.createXLinkOut()
		xOutDisp.setStreamName("disparity")

		stereo.disparity.link(xOutDisp.input)

		with dai.Device(pipeline) as device:
			self.disparityQueue = device.getOutputQueue(name="disparity", maxSize=1, blocking=False)

			# map disparity from 0 to 255
			self.disparityMultiplier = 255 / stereo.initialConfig.getMaxDisparity()

			self.referenceFrame = self.get_reference()

			'''
				Disparity: Double array of uint8
					each is in range from 0 -> 255, 0(furthest) 255(closest)
					[0][0] is top left (?)
					[0][X] is top right
					[X][0] is bottom left
					[X][X] is bottom right
			'''

	def get_frame(self):
		self.disparity = self.get_frame(self.disparityQueue)
		self.disparity = (self.disparity * self.disparityMultiplier).astype(np.uint8)

		danger, result_frame = self.analyze_frame(self.disparity, self.referenceFrame)

		self.frame_updated.emit(result_frame)


class FrameUpdaterThread(QThread):
	def __init__(self, camera_input):
		super().__init__()
		# Accesses the frame updater from CameraInput
		self.input = camera_input

	def run(self):
		while True:
			self.input.get_frame()
