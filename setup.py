# Import kivy dependencies first
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

# Import kivy UX components
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label

# Import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger

# Import other dependencies
import cv2
import tensorflow as tf
import os
import numpy as np
import face_recognition

# Build app and layout
class CamApp(App):

    def build(self):
        # Main layout components
        self.web_cam = Image(size_hint=(1, .8))
        self.button = Button(text="Take Photo", on_press=self.verify, size_hint=(1, .1))
        self.verification_label = Label(text="Enter a number (1-8) to textbox below", size_hint=(1, .1))

        # Text input for numbers from 1 to 8
        self.number_input = TextInput(multiline=False, input_filter="int", input_type="number", size_hint=(1, .1))

        # Add items to layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.web_cam)
        layout.add_widget(self.button)
        layout.add_widget(self.verification_label)
        layout.add_widget(self.number_input)

        # Setup video capture device
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)


        return layout


    # Run continuously to get webcam feed
    def update(self, *args):
        # Read frame from opencv
        ret, frame = self.capture.read()
        frame = frame[120:120 + 350, 200:200 + 350, :]

        # Flip horizontall and convert image to texture
        buf = cv2.flip(frame, 0).tostring()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    # Load image from file and conver to 100x100px
    def preprocess(self, file_path):
        # Read in image from file path
        byte_img = tf.io.read_file(file_path)
        # Load in the image
        img = tf.io.decode_jpeg(byte_img)

        # Preprocessing steps - resizing the image to be 100x100x3
        img = tf.image.resize(img, (100, 100))
        # Scale image to be between 0 and 1
        img = img / 255.0

        # Return image
        return img

    def save_image(self, file_path, frame):
        # Thực hiện lưu hình ảnh
        cv2.imwrite(file_path, frame)

    def delete_image(self, file_path):
        try:
            os.remove(file_path)
            self.verification_label.text = f'No face in {int(self.number_input.text)}.jpg'
        except Exception as e:
            pass


    # Verification function to verify person
    def verify(self, *args):
        input_value = self.number_input.text
        if input_value:
            number = int(input_value)
            if 1 <= number <= 8:
                # Capture input image from our webcam
                SAVE_PATH = os.path.join('application_data', 'verification_images', f'{int(self.number_input.text)}.jpg')
                ret, frame = self.capture.read()
                frame = frame[120:120 + 350, 200:200 + 350, :]
                self.save_image(SAVE_PATH, frame)

                # check face in picture
                input_img = face_recognition.load_image_file(f"application_data/verification_images/{int(self.number_input.text)}.jpg")
                input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
                try:
                    encode_input = face_recognition.face_encodings(input_img)[0]
                    self.verification_label.text = f'Save as {int(self.number_input.text)}.jpg'
                except:
                    self.delete_image(SAVE_PATH)




                # Rest of your verification logic here
            else:
                self.verification_label.text = "Invalid input. Enter a number between 1 and 8."

if __name__ == '__main__':
    CamApp().run()