// app.js
const API_URL = CONFIG.API_URL;

let originalFileName = "";

function updateProgress(status) {
    const progressBarFilled = document.getElementById('progressBarFilled');
    const progressText = document.getElementById('progressText');

    switch (status) {
        case 'UPLOADING':
            progressBarFilled.style.width = '20%';
            progressText.textContent = 'Uploading file...';
            break;
        case 'PROCESSING':
            progressBarFilled.style.width = '60%';
            progressText.textContent = 'Translation in progress...';
            break;
        case 'COMPLETED':
            progressBarFilled.style.width = '100%';
            progressText.textContent = 'Translation completed!';
            break;
        case 'FAILED':
            progressBarFilled.style.width = '0%';
            progressText.textContent = 'Translation failed.';
            break;
        default:
            progressBarFilled.style.width = '0%';
            progressText.textContent = '';
    }
}

function createDownloadLinkFromText(text, originalFileName) {
    const downloadLink = document.getElementById('downloadLink');

    const blob = new Blob([text], { type: 'text/plain' });
    const blobUrl = URL.createObjectURL(blob);

    const filename = originalFileName.replace('.pdf', '.txt');

    downloadLink.href = blobUrl;
    downloadLink.download = filename;
    downloadLink.textContent = `Download ${filename}`;
    downloadLink.style.display = 'inline-block';
}

function startPolling(currentRequestId) {
    const statusUrl = `${API_URL}/status?request_id=${currentRequestId}`;
    console.log('Polling started for request ID:', statusUrl);

    updateProgress('PROCESSING');

    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(statusUrl);
            if (!response.ok) throw new Error('Status check failed');

            const status = await response.json();
            updateProgress(status.status);

            if (status.status === 'COMPLETED' && status.translated_text) {
                clearInterval(pollInterval);
                createDownloadLinkFromText(status.translated_text, originalFileName);
            } else if (status.status === 'FAILED') {
                clearInterval(pollInterval);
                alert('Translation failed. Please try again.');
                updateProgress('FAILED');
            }
        } catch (error) {
            console.error('Polling error:', error);
            updateProgress('PROCESSING');
        }
    }, CONFIG.POLL_INTERVAL_MS);
}

async function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a PDF file first!');
        return;
    }

    if (file.type !== 'application/pdf') {
        alert('Only PDF files are allowed');
        return;
    }

    originalFileName = file.name;

    try {
        updateProgress('UPLOADING');

        const response = await fetch(`${API_URL}/generate-url`);
        if (!response.ok) throw new Error('Failed to get upload URL');

        const responseBody = await response.json();
        const parsedBody = JSON.parse(responseBody.body);

        const { url, request_id } = parsedBody;

        await fetch(url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': 'application/pdf'
            }
        });

        updateProgress('PROCESSING');
        startPolling(request_id);
        console.log('File uploaded successfully:', request_id);
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Error: ' + error.message);
        updateProgress('FAILED');
    }
}
