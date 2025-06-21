import numpy as np 
import cv2

STAGE_FIRST_FRAME = 0
STAGE_SECOND_FRAME = 1
STAGE_DEFAULT_FRAME = 2
kMinNumFeature = 1000 #900 #1500

# Shi-Tomasi parameters
feature_params = dict(
    maxCorners= 2000, #1200, #1600
    qualityLevel= 0.1, 
    minDistance= 10,
    blockSize= 7
)

lk_params = dict(winSize  = (21, 21), 
				#maxLevel = 3,
             	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

def featureTracking(image_ref, image_cur, px_ref):
	kp2, st, err = cv2.calcOpticalFlowPyrLK(image_ref, image_cur, px_ref, None, **lk_params)  #shape: [k,2] [k,1] [k,1]

	st = st.reshape(st.shape[0])
	kp1 = px_ref[st == 1]
	kp2 = kp2[st == 1]

	return kp1, kp2


class PinholeCamera:
	def __init__(self, width, height, fx, fy, cx, cy, 
				k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0):
		self.width = width
		self.height = height
		self.fx = fx
		self.fy = fy
		self.cx = cx
		self.cy = cy
		self.distortion = (abs(k1) > 0.0000001)
		self.d = [k1, k2, p1, p2, k3]
		self.P = np.array([[fx, 0, cx, 0],
						 [0, fy, cy, 0],
						 [0, 0, 1, 0]], dtype=np.float64)
		self.K = np.array([[fx, 0, cx],
						 [0, fy, cy],
						 [0, 0, 1]], dtype=np.float64)
		


class VisualOdometry:
	def __init__(self, cam):
		self.frame_stage = 0
		self.cam = cam
		self.new_frame = None
		self.last_frame = None
		self.cur_R = None
		self.cur_t = None
		self.px_ref = None
		self.px_cur = None
		self.focal = cam.fx
		self.pp = (cam.cx, cam.cy)
		self.trueX, self.trueY, self.trueZ = 0, 0, 0
		# with open(annotations) as f:
		# 	self.annotations = f.readlines()

	# def getAbsoluteScale(self, frame_id):  #specialized for KITTI odometry dataset
	# 	ss = self.annotations[frame_id-1].strip().split()
	# 	x_prev = float(ss[3])
	# 	y_prev = float(ss[7])
	# 	z_prev = float(ss[11])
	# 	ss = self.annotations[frame_id].strip().split()
	# 	x = float(ss[3])
	# 	y = float(ss[7])
	# 	z = float(ss[11])
	# 	self.trueX, self.trueY, self.trueZ = x, y, z
	# 	return np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))
	
	@staticmethod
	def _form_transf(R, t):
		T = np.eye(4, dtype=np.float64)
		T[:3, :3] = R
		T[:3, 3] = t
		return T

	def decomp_essential_mat(self, E, q1, q2):
		def sum_z_cal_relative_scale(R, t):
			# Get the transformation matrix
			T = self._form_transf(R, t)
            # Make the projection matrix
			P = np.matmul(np.concatenate((self.cam.K, np.zeros((3, 1))), axis=1), T)
            # Triangulate the 3D points
			hom_Q1 = cv2.triangulatePoints(np.float32(self.cam.P), np.float32(P), np.float32(q1), np.float32(q2))
            # Also seen from cam 2
			hom_Q2 = np.matmul(T, hom_Q1)
            # Un-homogenize
			uhom_Q1 = hom_Q1[:3, :] / hom_Q1[3, :]
			uhom_Q2 = hom_Q2[:3, :] / hom_Q2[3, :]

            # Find the number of points there has positive z coordinate in both cameras
			sum_of_pos_z_Q1 = sum(uhom_Q1[2, :] > 0)
			sum_of_pos_z_Q2 = sum(uhom_Q2[2, :] > 0)
			
			return sum_of_pos_z_Q1 + sum_of_pos_z_Q2

        # Decompose the essential matrix
		R1, R2, t = cv2.decomposeEssentialMat(E)
		t = np.squeeze(t)
        #t = t*z_c
        
        # Make a list of the different possible pairs
		pairs = [[R1, -t], [R1, t], [R2, t], [R2, -t]]

        # Check which solution there is the right one
		z_sums = []
		for R, t in pairs:
			z_sum = sum_z_cal_relative_scale(R, t)
			z_sums.append(z_sum)

        # Select the pair there has the most points with positive z coordinate
		right_pair_idx = np.argmax(z_sums)
        #print(right_pair_idx)
		right_pair = pairs[right_pair_idx]
		R1, t = right_pair
		
		return R1, t
	
	def processFirstFrame(self):
		self.px_ref = cv2.goodFeaturesToTrack(self.new_frame, mask=None, **feature_params)
		self.cur_R = np.eye(3, dtype=np.float64)  
		self.cur_t = np.zeros((3,), dtype=np.float64)  
		self.frame_stage = STAGE_SECOND_FRAME

	def processSecondFrame(self, absolute_scale):
		self.px_ref, self.px_cur = featureTracking(self.last_frame, self.new_frame, self.px_ref)
		E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC, prob=0.9999, threshold=1.0)
		# _, self.cur_R, self.cur_t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp = self.pp)
		self.cur_R, self.cur_t = self.decomp_essential_mat(E, self.px_cur, self.px_ref)
		self.cur_t = absolute_scale*self.cur_R.dot(self.cur_t)
		self.frame_stage = STAGE_DEFAULT_FRAME 
		self.px_ref = self.px_cur

	def processFrame(self, absolute_scale):
		self.px_ref, self.px_cur = featureTracking(self.last_frame, self.new_frame, self.px_ref)
		E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC, prob=0.9999, threshold=1.0)
		# _, R, t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp = self.pp)
		R, t = self.decomp_essential_mat(E, self.px_cur, self.px_ref)
		
		# absolute_scale = self.getAbsoluteScale(frame_id)
		# absolute_scale = 1
		# if(absolute_scale > 0.1):
		t = t / np.linalg.norm(t)  
		self.cur_t = self.cur_t + absolute_scale*self.cur_R.dot(t)  
		self.cur_R = R.dot(self.cur_R)
		if(self.px_ref.shape[0] < kMinNumFeature):
			self.px_cur = cv2.goodFeaturesToTrack(self.new_frame, mask=None, **feature_params)
			
		self.px_ref = self.px_cur

	def update(self, img, absolute_scale): 
		assert(img.ndim==2 and img.shape[0]==self.cam.height and img.shape[1]==self.cam.width), "Frame: provided image has not the same size as the camera model or image is not grayscale"
		self.new_frame = img 
		if(self.frame_stage == STAGE_DEFAULT_FRAME):
			self.processFrame(absolute_scale)
		elif(self.frame_stage == STAGE_SECOND_FRAME):
			self.processSecondFrame(absolute_scale)
		elif(self.frame_stage == STAGE_FIRST_FRAME):
			self.processFirstFrame()
		self.last_frame = self.new_frame








# import numpy as np 
# import cv2

# STAGE_FIRST_FRAME = 0
# STAGE_SECOND_FRAME = 1
# STAGE_DEFAULT_FRAME = 2
# kMinNumFeature = 800 #1500

# # Shi-Tomasi parameters
# feature_params = dict(
#     maxCorners= 1200, #1600
#     qualityLevel=0.01,
#     minDistance=5,
#     blockSize=7
# )

# lk_params = dict(winSize  = (21, 21), 
# 				#maxLevel = 3,
#              	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

# def featureTracking(image_ref, image_cur, px_ref):
# 	kp2, st, err = cv2.calcOpticalFlowPyrLK(image_ref, image_cur, px_ref, None, **lk_params)  #shape: [k,2] [k,1] [k,1]

# 	st = st.reshape(st.shape[0])
# 	kp1 = px_ref[st == 1]
# 	kp2 = kp2[st == 1]

# 	return kp1, kp2


# class PinholeCamera:
# 	def __init__(self, width, height, fx, fy, cx, cy, 
# 				k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0):
# 		self.width = width
# 		self.height = height
# 		self.fx = fx
# 		self.fy = fy
# 		self.cx = cx
# 		self.cy = cy
# 		self.distortion = (abs(k1) > 0.0000001)
# 		self.d = [k1, k2, p1, p2, k3]


# class VisualOdometry:
# 	def __init__(self, cam, annotations):
# 		self.frame_stage = 0
# 		self.cam = cam
# 		self.new_frame = None
# 		self.last_frame = None
# 		self.cur_R = None
# 		self.cur_t = None
# 		self.px_ref = None
# 		self.px_cur = None
# 		self.focal = cam.fx
# 		self.pp = (cam.cx, cam.cy)
# 		self.trueX, self.trueY, self.trueZ = 0, 0, 0
# 		self.detector = cv2.FastFeatureDetector_create(threshold=25, nonmaxSuppression=True)
# 		self.kfdetector = orb = cv2.ORB_create(
# 		    nfeatures=800,                          
# 		    scoreType=cv2.ORB_FAST_SCORE  # FAST_SCORE       
# 		)
# 		with open(annotations) as f:
# 			self.annotations = f.readlines()

# 	def getAbsoluteScale(self, frame_id):  #specialized for KITTI odometry dataset
# 		ss = self.annotations[frame_id-1].strip().split()
# 		x_prev = float(ss[3])
# 		y_prev = float(ss[7])
# 		z_prev = float(ss[11])
# 		ss = self.annotations[frame_id].strip().split()
# 		x = float(ss[3])
# 		y = float(ss[7])
# 		z = float(ss[11])
# 		self.trueX, self.trueY, self.trueZ = x, y, z
# 		return np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))

# 	def processFirstFrame(self):
# 		# self.px_ref = self.detector.detect(self.new_frame)
# 		self.px_ref = cv2.goodFeaturesToTrack(self.new_frame, mask=None, **feature_params)
# 		# self.px_ref = np.array([x.pt for x in self.px_ref], dtype=np.float32)
# 		self.frame_stage = STAGE_SECOND_FRAME

# 	def processSecondFrame(self):
# 		self.px_ref, self.px_cur = featureTracking(self.last_frame, self.new_frame, self.px_ref)
# 		E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC, prob=0.999, threshold=1.0)
# 		_, self.cur_R, self.cur_t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp = self.pp)
# 		self.frame_stage = STAGE_DEFAULT_FRAME 
# 		self.px_ref = self.px_cur

# 	def processFrame(self, frame_id):
# 		self.px_ref, self.px_cur = featureTracking(self.last_frame, self.new_frame, self.px_ref)
# 		E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC, prob=0.999, threshold=1.0)
# 		_, R, t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp = self.pp)
# 		absolute_scale = 0.2 #self.getAbsoluteScale(frame_id)
# 		if(absolute_scale > 0.1):
# 			self.cur_t = self.cur_t + absolute_scale*self.cur_R.dot(t) 
# 			self.cur_R = R.dot(self.cur_R)
# 		if(self.px_ref.shape[0] < kMinNumFeature):
# 			# self.px_cur = self.detector.detect(self.new_frame)
# 			# self.px_cur = np.array([x.pt for x in self.px_cur], dtype=np.float32)
# 			self.px_cur = cv2.goodFeaturesToTrack(self.new_frame, mask=None, **feature_params)
			
# 			a = self.kfdetector.detectAndCompute(self.new_frame, None)
# 		self.px_ref = self.px_cur

# 	def update(self, img, frame_id):
# 		assert(img.ndim==2 and img.shape[0]==self.cam.height and img.shape[1]==self.cam.width), "Frame: provided image has not the same size as the camera model or image is not grayscale"
# 		self.new_frame = img
# 		if(self.frame_stage == STAGE_DEFAULT_FRAME):
# 			self.processFrame(frame_id)
# 		elif(self.frame_stage == STAGE_SECOND_FRAME):
# 			self.processSecondFrame()
# 		elif(self.frame_stage == STAGE_FIRST_FRAME):
# 			self.processFirstFrame()
# 		self.last_frame = self.new_frame