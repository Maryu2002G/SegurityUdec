from django.http import StreamingHttpResponse
from django.shortcuts import render
from keras.models import load_model  
import cv2
import numpy as np

# Cargar el modelo y las etiquetas
model = load_model("C:/Users/maryu/OneDrive/Escritorio/DjangoP/myapp/templates/keras_model.h5", compile=False)
class_names = open("C:/Users/maryu/OneDrive/Escritorio/DjangoP/myapp/templates/labels.txt", "r").readlines()
message = "hi"
def camera_stream(request):
    camera = cv2.VideoCapture(0)

    def stream():
        while True:
            ret, image = camera.read()
            if not ret:
                break

            # Resize the raw image into (224-height,224-width) pixels
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

            # Make the image a numpy array and reshape it to the models input shape.
            image_array = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

            # Normalize the image array
            image_array = (image_array / 127.5) - 1

            # Predicts the model
            prediction = model.predict(image_array)
            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]

            # Print prediction and confidence score
            print("Class:", class_name[2:], end="")
            print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

            message = f"Class: {class_name[2:]} | Confidence Score: {str(np.round(confidence_score * 100))[:-2]} %"
            print(message)

            # Convert the image to JPEG format
            _, buffer = cv2.imencode('.jpg', image)

            # Convert message to bytes
            message_bytes = bytes(message, 'utf-8')

            # Yield both image and message
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n' +
               b'Content-Type: text/plain\r\n\r\n' + message_bytes + b'\r\n')

    response = StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
