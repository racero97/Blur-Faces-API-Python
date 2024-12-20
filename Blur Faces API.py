#construir una api para preservar la privacidad en imágenes de forma que reciba la URL de una imagen y si hay personas en ella la devuelva pero con las caras borrosas (blur) con un factor de borrosidad por defecto de 3. El único endpont será /?url=url_de_la_imagen&factor=3
import io

import face_recognition
import numpy as np
import requests
from fastapi import FastAPI
from PIL import Image
from skimage.filters import gaussian
from starlette.responses import StreamingResponse

app = FastAPI()


def blur(image_arr, factor=3):
    """Difumina una imagen dada como una array 3D (RGB) NumPy usando factor"""
    try:
        # Según la versión, puede ser necesario el parámetro multichannel=True 
        return gaussian(image_arr, sigma=factor, multichannel=True, preserve_range=True)
    except:
        return gaussian(image_arr, sigma=factor, preserve_range=True)


@app.get("/")
def blur_faces(url: str, factor: int = 3):
    try:
        response = requests.get(url)
        image_arr = np.array(Image.open(io.BytesIO(response.content)).convert("RGB"))
    except:
        return {"error": "Image not valid"}
    
    #Funcion face_locations que devuelve una lista de tuplas con la ubicacion de las caras
    face_locations = face_recognition.api.face_locations(image_arr, number_of_times_to_upsample=1, model='hog')
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face = image_arr[top:bottom, left:right]
        blurred_face = blur(face, factor)
        image_arr[top:bottom, left:right] = blurred_face
    
    out = Image.fromarray(np.uint8(image_arr))
    bytes_arr = io.BytesIO()
    out.save(bytes_arr, format='PNG')
    bytes_arr.seek(0)
    return StreamingResponse(bytes_arr, media_type="image/png") 
