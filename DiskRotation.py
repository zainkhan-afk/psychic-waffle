import cv2
import soundfile as sf
import numpy as np
import time
class DiskRotation:
	def __init__(self, width, height, disk_radius = 400, rpm = 60, fps = 30):
		self.Reset(width, height, disk_radius, rpm, fps)
		
		self.logo_watermark_path = "grid_landscape_qkmazx.png"
		self.created_at_watermark_path = "grid_landscape_axkq4b.png"
		self.logo_text_watermark_path = "grid_landscape_in6hqq.png"

		self.MakeBGWatermarkStensil()
		self.MakeDiskWatermarkStensil()

		self.logo_watermark_image = cv2.imread(self.logo_watermark_path, cv2.IMREAD_UNCHANGED)
		self.created_at_watermark_image = cv2.imread(self.created_at_watermark_path, cv2.IMREAD_UNCHANGED)
		self.logo_text_watermark_image = cv2.imread(self.logo_text_watermark_path, cv2.IMREAD_UNCHANGED)


		R, C, _ = self.logo_watermark_image.shape
		self.logo_watermark_image = cv2.resize(self.logo_watermark_image, (int(1.6 * C), int(1.6 * R)))

		# self.created_at_watermark_image = cv2.resize(self.created_at_watermark_image, (int(1.6 * C), int(1.6 * R)))

		self.created_at_watermark_image = self.created_at_watermark_image[:-10, :-10]


	def MakeBGWatermarkStensil(self):
		self.BG_watermark_stensil = np.zeros((self.height, self.width, 3)).astype("uint8")
		self.BG_watermark_stensil_alpha = np.zeros((self.height, self.width)).astype("uint8")


		im1 = cv2.imread(self.logo_watermark_path, cv2.IMREAD_UNCHANGED)
		R, C, _ = im1.shape
		im1 = cv2.resize(im1, (int(1.6 * C), int(1.6 * R)))
		
		x1 = 25
		x2 = x1 + im1.shape[1]

		y1 = 25
		y2 = y1 + im1.shape[0]

		self.BG_watermark_stensil_alpha[y1:y2, x1:x2] = im1[:, :, -1]
		self.BG_watermark_stensil[y1:y2, x1:x2] = im1[:, :, :-1]




		im2 = cv2.imread(self.created_at_watermark_path, cv2.IMREAD_UNCHANGED)
		im2 = im2[:-10, :-10,]



		x2 = self.width
		x1 = x2 - im2.shape[1]

		y2 = self.height
		y1 = y2 - im2.shape[0]

		self.BG_watermark_stensil_alpha[y1:y2, x1:x2] = im2[:, :, -1]
		self.BG_watermark_stensil[y1:y2, x1:x2] = im2[:, :, :-1]


		self.BG_watermark_stensil = cv2.bitwise_and(self.BG_watermark_stensil, self.BG_watermark_stensil, mask = self.BG_watermark_stensil_alpha)
		self.BG_watermark_stensil_alpha_inv = cv2.bitwise_not(self.BG_watermark_stensil_alpha)




		# self.BG_watermark_stensil = ((self.BG_watermark_stensil.astype("float32") * cv2.cvtColor(self.BG_watermark_stensil_alpha, cv2.COLOR_GRAY2BGR))*255).astype("uint8")


		# self.BG_watermark_stensil_alpha_inv = ((1 - cv2.cvtColor(self.BG_watermark_stensil_alpha, cv2.COLOR_GRAY2BGR))*255).astype("uint8")
		# self.BG_watermark_stensil_alpha_inv = cv2.cvtColor(self.BG_watermark_stensil_alpha_inv, cv2.COLOR_BGR2GRAY)
		
		# self.BG_watermark_stensil_alpha = (self.BG_watermark_stensil_alpha*255).astype("uint8")
		# self.BG_watermark_stensil_alpha = cv2.cvtColor(self.BG_watermark_stensil_alpha, cv2.COLOR_BGR2GRAY)
		
		# t = cv2.resize(self.BG_watermark_stensil_alpha, (int(self.BG_watermark_stensil_alpha.shape[1]*0.7), int(self.BG_watermark_stensil_alpha_inv.shape[0]*0.7)))

		# cv2.imshow("bg_sten", t)
		# cv2.waitKey(0)

	def MakeDiskWatermarkStensil(self):
		self.disk_watermark_stensil = np.zeros((self.height, self.width, 3)).astype("uint8")
		self.disk_watermark_stensil_alpha = np.zeros((self.height, self.width)).astype("uint8")

		im = cv2.imread(self.logo_text_watermark_path, cv2.IMREAD_UNCHANGED)


		x1 = self.width // 2 - im.shape[1] // 2
		x2 = x1 + im.shape[1]

		y1 = self.height // 2 - im.shape[0] // 2
		y2 = y1 + im.shape[0]

		self.disk_watermark_stensil[y1:y2, x1:x2] = im[:, :, :-1]
		self.disk_watermark_stensil_alpha[y1:y2, x1:x2] = im[:, :, -1]

		self.disk_watermark_stensil = cv2.bitwise_and(self.disk_watermark_stensil, self.disk_watermark_stensil, mask = self.disk_watermark_stensil_alpha)
		self.disk_watermark_stensil_alpha_inv = cv2.bitwise_not(self.disk_watermark_stensil_alpha)



	def ShowWatermarks(self):
		self.frame[:, :, 2] = 255
		disk = self.frame.copy()
		disk[:, :, 1] = 255
		self.frame = self.DrawWatermark(self.frame)
		self.frame = self.DrawWatermark(self.frame)

		self.DrawDisk(disk, self.frame, 0)


	def SetSize(self, width, height):
		self.width = width
		self.height = height
		self.Reset(self.width, self.height, self.disk_radius, self.rpm, self.fps)

	def Reset(self, width, height, disk_radius = 400, rpm = 60, fps = 30):
		self.width = width
		self.height = height
		self.disk_radius = disk_radius
		self.rpm = rpm
		self.fps = fps

		self.radians_per_second = self.rpm*2*np.pi / 60

		self.frame = np.zeros((self.height, self.width, 3))
		self.disk_mask = np.zeros((self.height, self.width)).astype("uint8")
		cv2.circle(self.disk_mask, (self.width // 2, self.height // 2), self.disk_radius, 255, -1)
		self.disk_mask_inv = cv2.bitwise_not(self.disk_mask)

		# self.disk_mask = self.disk_mask.astype("float32") / 255

		self.Clear()

	def FormatImage(self, image, new_width, clip_height_to):
		H, W, _ = image.shape
		new_W = new_width
		new_H = int(new_W * H / W)

		image = cv2.resize(image, (new_W, new_H))

		if new_H > clip_height_to:
			diff = new_H - clip_height_to
			crop_x1 = 0
			crop_x2 = new_W
			crop_y1 = diff // 2
			crop_y2 = diff // 2 + clip_height_to

			image = image[crop_y1:crop_y2, crop_x1:crop_x2]

		if new_H < clip_height_to:
				diff = clip_height_to - new_H

				crop_x1 = 0
				crop_x2 = new_W
				crop_y1 = diff // 2
				crop_y2 = diff // 2 + new_H

				new_image = np.zeros((new_width, clip_height_to, 3)).astype("uint8")
				new_image[crop_y1:crop_y2, crop_x1:crop_x2] = image
				image = new_image.copy()

		return image

	def LoadVideoImages(self, video_path):
		cap = cv2.VideoCapture(video_path)
		all_video_frames = []
		while True:
			ret, img = cap.read()
			if not ret:
				break
			img = self.FormatImage(img, new_width = self.width, clip_height_to = self.height)
			if self.use_watermark:
				img = self.DrawWatermark(img, "bg")
			all_video_frames.append(img)

		return all_video_frames

	def DrawWatermark(self, image, image_type = "bg"):
		if image_type == "bg":
			# image = cv2.bitwise_and(image, image, mask = self.BG_watermark_stensil_alpha_inv)
			# image = image + self.BG_watermark_stensil


			# t = cv2.resize(self.BG_watermark_stensil, (int(self.BG_watermark_stensil_alpha.shape[1]*0.7), int(self.BG_watermark_stensil_alpha_inv.shape[0]*0.7)))

			# cv2.imshow("t", t)
			# cv2.waitKey(0)


			im1 = self.logo_watermark_image.copy()
			im2 = self.created_at_watermark_image.copy()

			im1_alpha = cv2.cvtColor(im1[:, :, -1], cv2.COLOR_GRAY2BGR).astype("float32") / 255
			im1 = im1[:, :, :-1].astype("float32")

			im2_alpha = cv2.cvtColor(im2[:, :, -1], cv2.COLOR_GRAY2BGR).astype("float32") / 255
			im2 = im2[:, :, :-1].astype("float32")

			H, W, _ = image.shape

			x1 = 25
			x2 = x1 + im1.shape[1]

			y1 = 25
			y2 = y1 + im1.shape[0]

			image[y1:y2, x1:x2] = (im1*im1_alpha + image[y1:y2, x1:x2]*(1 - im1_alpha)).astype("uint8")

			x2 = W
			x1 = x2 - im2.shape[1]

			y2 = H
			y1 = y2 - im2.shape[0]

			image[y1:y2, x1:x2] = (im2*im2_alpha + image[y1:y2, x1:x2]*(1 - im2_alpha)).astype("uint8")


		elif image_type == "disk":
			# image = cv2.bitwise_and(image, image, mask = self.disk_watermark_stensil_alpha_inv)
			# image = image + self.disk_watermark_stensil

			im = self.logo_text_watermark_image.copy()

			im_alpha = cv2.cvtColor(im[:, :, -1], cv2.COLOR_GRAY2BGR).astype("float32") / 255
			im = im[:, :, :-1].astype("float32")

			H, W, _ = image.shape

			x1 = W // 2 - im.shape[1] // 2
			x2 = x1 + im.shape[1]

			y1 = H // 2 - im.shape[0] // 2
			y2 = y1 + im.shape[0]

			image[y1:y2, x1:x2] = (im*im_alpha + image[y1:y2, x1:x2]*(1 - im_alpha)).astype("uint8")

		return image

	def PadImage(self, img, new_img_size):
		w, h = new_img_size[0], new_img_size[1]
		img_h, img_w, _ = img.shape

		img_x1 = w // 2 - img_w // 2
		img_y1 = h // 2 - img_h // 2

		img_x2 = w // 2 + img_w // 2
		img_y2 = h // 2 + img_h // 2


		padded_img = np.zeros((h, w, 3)).astype("uint8")
		padded_img[img_y1:img_y2, img_x1:img_x2] = img

		return padded_img

	def DrawDisk(self, disk_image, background_image, t):
		angle = -t*self.radians_per_second
		disk = self.RotateImage(disk_image.copy(), angle)

		disk_frame = disk.copy()

		disk_frame = cv2.bitwise_and(disk_frame, disk_frame, mask = self.disk_mask)

		# background_image[self.disk_mask == 0] = disk_frame[self.disk_mask == 0]

		return disk_frame + background_image

	def RotateImage(self, image, angle):
		row, col = image.shape[:2]
		center = tuple(np.array([row,col])/2)
		rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
		new_image = cv2.warpAffine(image, rot_mat, (col, row))
		return new_image

	def Clear(self):
		self.frame = np.zeros((self.height, self.width, 3))
		# self.frame.fill(0)

	def CreateVideoFrames(self, video_time, use_watermark = True, background_mode = 0, background_image_data = None, disk_image_data = None,  temp_video_filename = "video_temp.avi"):
		self.use_watermark = use_watermark
		total_frames = None
		bg_video_cap = None

		if background_mode not in ["color","image","video"]:
			print("Background mode is invalid. Must be color, image or video.")
			return False

		all_background_frames = None
		bg_image = None
		disk_image = None
		if background_mode == "color":
			bg_image = np.zeros((self.height, self.width, 3)).astype("uint8")
			bg_image[:, :, 0] = background_image_data[0]
			bg_image[:, :, 1] = background_image_data[1]
			bg_image[:, :, 2] = background_image_data[2]

			if self.use_watermark:
				bg_image = self.DrawWatermark(bg_image, "bg")

			bg_image = cv2.bitwise_and(bg_image, bg_image, mask = self.disk_mask_inv)


		elif background_mode == "image":
			bg_image = cv2.imread(background_image_data)
			bg_image = self.FormatImage(bg_image, new_width = self.width, clip_height_to = self.height)

			if self.use_watermark:
				bg_image = self.DrawWatermark(bg_image, "bg")

			bg_image = cv2.bitwise_and(bg_image, bg_image, mask = self.disk_mask_inv)



		elif background_mode == "video":
			bg_video_cap = cv2.VideoCapture(background_image_data)
			total_frames = bg_video_cap.get(cv2.CAP_PROP_FRAME_COUNT)


		disk_image = cv2.imread(disk_image_data)
		disk_image = self.FormatImage(disk_image, new_width = self.disk_radius*2, clip_height_to = self.disk_radius*2)
		disk_image = self.PadImage(disk_image, (self.width, self.height))

		if self.use_watermark:
			disk_image = self.DrawWatermark(disk_image, "disk")



		num_frames = int(video_time*self.fps)
		delta_t = 1 / self.fps


		size = (self.width, self.height)
		writer = cv2.VideoWriter(temp_video_filename,  cv2.VideoWriter_fourcc(*'MJPG'), self.fps, size) 


		tick = time.time()
		bg_img_idx = 0
		t = 0
		for i in range(num_frames):
			# if i % 1000 == 0:
			# 	print(f"{i} / {num_frames} completed")
			# self.Clear()


			if background_mode == "video":
				ret, bg_image = bg_video_cap.read()
				if not ret:
					bg_video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
					ret, bg_image = bg_video_cap.read()

				bg_image = self.FormatImage(bg_image, new_width = self.width, clip_height_to = self.height)
				if self.use_watermark:
					bg_image = self.DrawWatermark(bg_image, "bg")

				bg_image = cv2.bitwise_and(bg_image, bg_image, mask = self.disk_mask_inv)


			self.frame = self.DrawDisk(disk_image, bg_image, t)
			writer.write(self.frame)


			t += delta_t

		tock = time.time()

		print(f"Time taken in generative video frames: {tock - tick}")

		writer.release()
		return True

if __name__ == "__main__":
	background_mode = "video"
	audio_file_url = "D:/zain_dev/python_dev/rotating_disk/data/audio_1.5_min.mp3"
	# audio_file_url = "D:/zain_dev/python_dev/rotating_disk/data/audio.mp3"
	disk_image_data = "D:/zain_dev/python_dev/rotating_disk/data/disk.jpg"
	temp_video_filename = "../temp.avi"


	if background_mode == "image":
		background_image_data = "D:/zain_dev/python_dev/rotating_disk/data/BG.jpeg"
	if background_mode == "video":	
		background_image_data = "D:/zain_dev/python_dev/rotating_disk/data/BG_Vid.mp4"
	else:
		background_image_data = '#ff0000'
		background_image_data = (0, 255, 0)
	DR = DiskRotation(1080, 1080, disk_radius = int((1080/2)*0.8), rpm = 200, fps = 30)

	sound_data, fs = sf.read(audio_file_url, dtype='float32')

	video_time = sound_data.shape[0] / fs

	t1 = time.time()
	DR.CreateVideoFrames(video_time, use_watermark = True, background_mode = background_mode, background_image_data = background_image_data, 
						disk_image_data = disk_image_data, temp_video_filename = temp_video_filename)
	t2 = time.time()

	print(f"Total Time taken: {t2 -t1} s")
