# Import kivy dependencies first
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

# Import kivy UX components
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label

# Import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger

# Import other dependencies
import cv2
import os
import numpy as np
import face_recognition

import firebase_admin
from firebase_admin import credentials, db
import time

# Build app and layout
class CamApp(App):

    def build(self):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://faceproject-b3c27-default-rtdb.firebaseio.com'})
        # Main layout components
        self.web_cam = Image(size_hint=(1, .8))
        self.button = Button(text="Verify", on_press=self.verify, size_hint=(1, .1))
        self.verification_label = Label(text="Verification Uninitiated", size_hint=(1, .1))
        self.notification_label = Label(text="<notification>", size_hint=(1, .1))

        # Add items to layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.web_cam)
        layout.add_widget(self.button)
        layout.add_widget(self.verification_label)
        layout.add_widget(self.notification_label)


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

    def reset_labels(self, dt):
        self.verification_label.text = 'Verification Uninitiated'
        self.notification_label.text = '<notification>'

    # Verification function to verify person
    def verify(self, *args):
        # Specify thresholds
        detection_threshold = 0.99
        verification_threshold = 0.8

        # Capture input image from our webcam
        SAVE_PATH = os.path.join('application_data', 'input_image', 'input_image.jpg')
        ret, frame = self.capture.read()
        frame = frame[120:120 + 350, 200:200 + 350, :]
        cv2.imwrite(SAVE_PATH, frame)

        results = []
        facedists = []
        user_id = 0
        for image in os.listdir(os.path.join('application_data', 'verification_images')):
            print(image)
            try:
                # input_img = self.preprocess(os.path.join('application_data', 'input_image', 'input_image.jpg'))
                # validation_img = self.preprocess(os.path.join('application_data', 'verification_images', image))

                input_img = face_recognition.load_image_file("application_data/input_image/input_image.jpg")
                validation_img = face_recognition.load_image_file("application_data/verification_images/"+image)

                input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
                validation_img = cv2.cvtColor(validation_img, cv2.COLOR_BGR2RGB)

                try:
                    encode_input = face_recognition.face_encodings(input_img)[0]
                    encode_valid = face_recognition.face_encodings(validation_img)[0]
                    result = face_recognition.compare_faces([encode_input], encode_valid)
                    facedist = face_recognition.face_distance([encode_input], encode_valid)
                    results.append(result)
                    facedists.append(facedist)
                except:
                    pass


            except:
                print("error")
        indexs = []
        for i in range(len(results)):
            print(f"{results[i]} \t {facedists[i]}")
            if results[i] and facedists[i]<0.5:
                indexs.append(i)
        if (len(indexs)!=0):
            user_id = indexs.index(min(indexs))+1
            self.verification_label.text = f'Verified number {user_id}'
        else:
            user_id = 0
            self.verification_label.text = f'Unverified/ Your face must be in frame'

        # Check firebase
        if (user_id<=8 and user_id>0):

            handle = db.reference('User')
            times = handle.get()
            slot = int(times[user_id]['time'])
            # update times
            # Construct the path to the specific user's 'time' key
            user_path = f'{user_id}/time'
            # Update the 'time' value for the specific user
            if slot>0:
                handle.update({user_path: slot-1})
                self.notification_label.text = f'You have {slot-1} slot(s) left.'
                Clock.schedule_once(self.reset_labels, 5)
                user_id=0
            else:
                self.notification_label.text = f'You have no slot left.'
                Clock.schedule_once(self.reset_labels, 5)
                user_id = 0


        # Log out details
        Logger.info(results)

        return results


if __name__ == '__main__':
    CamApp().run()