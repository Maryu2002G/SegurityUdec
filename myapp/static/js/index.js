//crea elemento
const video = document.createElement("video");

//nuestro camvas
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

//div donde llegara nuestro canvas
const btnScanQR = document.getElementById("btn-scan-qr");

//lectura desactivada
let scanning = false;

//funcion para encender la camara
const encenderCamara = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(function (stream) {
      scanning = true;
      btnScanQR.hidden = true;
      canvasElement.hidden = false;
      video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
      video.srcObject = stream;
      video.play();
      tick();
      scan();
    });
};

//funciones para levantar las funiones de encendido de la camara
function tick() {
  canvasElement.height = video.videoHeight;
  canvasElement.width = video.videoWidth;
  canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

  scanning && requestAnimationFrame(tick);
}

function scan() {
  try {
    qrcode.decode();
  } catch (e) {
    setTimeout(scan, 300);
  }
}

//apagara la camara
const cerrarCamara = () => {
  video.srcObject.getTracks().forEach((track) => {
    track.stop();
  });
  canvasElement.hidden = true;
  btnScanQR.hidden = false;
};

const activarSonido = () => {
  var audio = document.getElementById('audioScaner');
  audio.play();
}

qrcode.callback = (respuesta) => {
  if (respuesta) {
    // Obtener el token CSRF de las cookies
    const csrftoken = getCookie('csrftoken');

    Swal.fire(respuesta)
    activarSonido();
    //encenderCamara();    
    cerrarCamara();  

    // Hacer la solicitud POST con el token CSRF
    fetch('/procesar-codigo-qr/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ respuesta: respuesta })
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      throw new Error('Error al procesar la respuesta del código QR');
    })
    .then(data => {
          Object.entries(data).forEach(([key, value]) => {
            console.log(key + ':', value);
        });

      document.getElementById("nombre").innerText = data.nombre_persona;
      document.getElementById("marca").innerText = data.marca_computador;
      document.getElementById("id_qr").innerText = data.id_qr;
      document.getElementById("fecha_asignacion").innerText = data.fecha_asignacion;
      document.getElementById("id").innerText = data.id;
    })
    
    .catch(error => {
      console.error('Error:', error);
    });
  }
};

// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}





