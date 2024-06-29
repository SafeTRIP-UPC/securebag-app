const video = document.getElementById('camera');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture-btn');
const numScalesInput = document.getElementById('num-scales');

// Acceder a la cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error al acceder a la cámara: ", err);
    });

captureButton.addEventListener('click', () => {
    const width = video.videoWidth;
    const height = video.videoHeight;
    canvas.width = width;
    canvas.height = height;
    canvas.getContext('2d').drawImage(video, 0, 0, width, height);
    const imageData = canvas.toDataURL('image/png');
    const numScales = parseInt(numScalesInput.value, 10);

    fetch('/estimate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData, num_scales: numScales })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            const details = encodeURIComponent(JSON.stringify(data.details));
            window.location.href = `/result?value=${data.estimated_value}&image=${data.image_filename}&details=${details}&num_scales=${numScales}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
