document.addEventListener('DOMContentLoaded', () => {
    const captureBtn = document.getElementById('captureBtn');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const previewContainer = document.getElementById('previewContainer');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');

    let imageFile = null;

    captureBtn.addEventListener('click', () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    video.play();

                    const canvas = document.createElement('canvas');
                    canvas.width = 640;
                    canvas.height = 480;

                    setTimeout(() => {
                        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
                        stream.getTracks().forEach(track => track.stop());
                        canvas.toBlob(blob => {
                            imageFile = new File([blob], "captured_image.jpg", { type: "image/jpeg" });
                            preview.src = URL.createObjectURL(blob);
                            previewContainer.classList.remove('hidden');
                            analyzeBtn.classList.remove('hidden');
                        }, 'image/jpeg');
                    }, 300);
                })
                .catch(error => console.error('Error accessing camera:', error));
        } else {
            console.error('getUserMedia is not supported in this browser');
        }
    });

    fileInput.addEventListener('change', (e) => {
        imageFile = e.target.files[0];
        if (imageFile) {
            preview.src = URL.createObjectURL(imageFile);
            previewContainer.classList.remove('hidden');
            analyzeBtn.classList.remove('hidden');
        }
    });

    analyzeBtn.addEventListener('click', () => {
        if (!imageFile) {
            alert('Please capture or upload an image first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', imageFile);

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayResult(data);
            resultContainer.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during analysis. Please try again.');
        });
    });

    function displayResult(data) {
        console.log("Received data:", data);  // Add this line for debugging

        const sections = [
            { title: "Plant Name", key: "name" },
            { title: "Suitable Locations", key: "locations" },
            { title: "Benefits", key: "benefits" },
            { title: "Care Tips", key: "care_tips" }
        ];

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';

        sections.forEach(section => {
            const content = data[section.key] || "Information not available";
            html += `
                <div class="bg-white p-4 rounded-lg shadow">
                    <h4 class="font-semibold text-lg text-green-700 mb-2">${section.title}</h4>
                    <p class="text-gray-700">${content}</p>
                </div>
            `;
        });

        html += '</div>';
        resultContent.innerHTML = html;
    }
});
