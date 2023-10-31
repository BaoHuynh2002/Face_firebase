# import cv2
#
# # Đường dẫn của hình ảnh ban đầu
# input_image_path = "application_data/verification_images/OIP.jpg"
#
# # Đọc hình ảnh gốc
# img = cv2.imread(input_image_path)
#
# # Kiểm tra xem hình ảnh đã được đọc thành công chưa
# if img is not None:
#     # Resize hình ảnh thành kích thước 100x100
#     img_resized = cv2.resize(img, (100, 100))
#
#     # Đường dẫn lưu hình ảnh đã thay đổi kích thước
#     output_image_path = "application_data/verification_images/OIP_resized.jpg"
#
#     # Lưu hình ảnh đã thay đổi kích thước
#     cv2.imwrite(output_image_path, img_resized)
#     print(f"Resized image saved to {output_image_path}")
# else:
#     print("Failed to read the input image.")
