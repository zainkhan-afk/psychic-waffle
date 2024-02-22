import cv2
import numpy as np


class DiskRotation:
	def __init__(self, width, height, disk_radius = 400, rpm = 60, fps = 30):
		self.Reset(width, height, disk_radius, rpm, fps)
		self.logo_watermark_path = "grid_landscape_qkmazx.png"
		self.created_at_watermark_path = "grid_landscape_axkq4b.png"
		self.logo_text_watermark_path = "grid_landscape_in6hqq.png"

		self.logo_watermark_image = cv2.imread(self.logo_watermark_path, cv2.IMREAD_UNCHANGED)
		self.created_at_watermark_image = cv2.imread(self.created_at_watermark_path, cv2.IMREAD_UNCHANGED)
		self.logo_text_watermark_image = cv2.imread(self.logo_text_watermark_path, cv2.IMREAD_UNCHANGED)

		R, C, _ = self.logo_watermark_image.shape
		self.logo_watermark_image = cv2.resize(self.logo_watermark_image, (int(1.6 * C), int(1.6 * R)))

		# R, C, _ = self.created_at_watermark_image.shape
		# self.created_at_watermark_image = cv2.resize(self.created_at_watermark_image, (int(0.75 * C), int(0.75 * R)))

		self.created_at_watermark_image = self.created_at_watermark_image[:-10, :-10]

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

		self.disk_mask = np.zeros((self.height, self.width, 3)).astype("uint8")
		cv2.circle(self.disk_mask, (self.width // 2, self.height // 2), self.disk_radius, (255, 255, 255), -1)

		self.disk_mask = self.disk_mask.astype("float32") / 255


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


	def DrawDisk(self, disk_image, background_image, t):
		angle = -t*self.radians_per_second
		disk = self.RotateImage(disk_image.copy(), angle)

		h, w, _ = self.frame.shape
		disk_h, disk_w, _ = disk.shape

		disk_x1 = w // 2 - disk_w // 2
		disk_y1 = h // 2 - disk_h // 2

		disk_x2 = w // 2 + disk_w // 2
		disk_y2 = h // 2 + disk_h // 2


		disk_frame = np.zeros((self.height, self.width, 3)).astype("uint8")
		disk_frame[disk_y1:disk_y2, disk_x1:disk_x2] = disk
		disk_frame = disk_frame.astype("float32") / 255

		background_frame = background_image.copy().astype("float32") / 255



		self.frame = ((background_frame*(1 - self.disk_mask) + disk_frame*self.disk_mask)*255).astype("uint8")

	def RotateImage(self, image, angle):
	    row, col = image.shape[:2]
	    center = tuple(np.array([row,col])/2)
	    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
	    new_image = cv2.warpAffine(image, rot_mat, (col, row))
	    return new_image

	def Clear(self):
		self.frame = np.zeros((self.height, self.width, 3))


	def CreateVideoFrames(self, time, use_watermark = True, background_mode = 0, background_image_data = None, disk_image_data = None,  temp_video_filename = "video_temp.avi"):
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


		elif background_mode == "image":
			bg_image = cv2.imread(background_image_data)
			bg_image = self.FormatImage(bg_image, new_width = self.width, clip_height_to = self.height)

			if self.use_watermark:
				bg_image = self.DrawWatermark(bg_image, "bg")


		elif background_mode == "video":
			bg_video_cap = cv2.VideoCapture(background_image_data)
			total_frames = bg_video_cap.get(cv2.CAP_PROP_FRAME_COUNT)


		disk_image = cv2.imread(disk_image_data)
		disk_image = self.FormatImage(disk_image, new_width = self.disk_radius*2, clip_height_to = self.disk_radius*2)

		if self.use_watermark:
			disk_image = self.DrawWatermark(disk_image, "disk")



		num_frames = int(time*self.fps)
		delta_t = 1 / self.fps


		size = (self.width, self.height)
		writer = cv2.VideoWriter(temp_video_filename,  cv2.VideoWriter_fourcc(*'MJPG'), self.fps, size) 



		bg_img_idx = 0
		t = 0
		for i in range(num_frames):
			if i % 1000 == 0:
				print(f"{i} / {num_frames} completed")

			self.Clear()


			if background_mode == "video":
				ret, bg_image = bg_video_cap.read()
				if not ret:
					bg_video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
					ret, bg_image = bg_video_cap.read()

				bg_image = self.FormatImage(bg_image, new_width = self.width, clip_height_to = self.height)
				if self.use_watermark:
					bg_image = self.DrawWatermark(bg_image, "bg")

			self.DrawDisk(disk_image, bg_image, t)
			writer.write(self.frame.astype("uint8"))

			# cv2.imshow("F", self.frame)
			# k = cv2.waitKey(1)

			# if k == ord("q"):
			# 	break

			t += delta_t


		writer.release()
		return True

if __name__ == "__main__":
	DR = DiskRotation(1080, 1080, disk_radius = int((1080/2)*0.8), rpm = 200, fps = 30)
	DR.Clear()
	DR.ShowWatermarks()

	# cv2.imshow("frame", DR.frame)
	# cv2.waitKey(0)

	cv2.imwrite("test.png", DR.frame)