// app.js
const API_URL = CONFIG.API_URL;

let originalFileName = ""; // Store the original file name

function startPolling(currentRequestId) {
    const statusUrl = `${API_URL}/status?request_id=${currentRequestId}`;
    console.log('Polling started for request ID:', statusUrl);

    // Immediately update the progress to "PROCESSING"
    updateProgress('PROCESSING'); // Show "Translation in progress..." as soon as polling starts

    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(statusUrl);
            if (!response.ok) throw new Error('Status check failed');

            const status = await response.json();

            // Update progress bar
            updateProgress(status.status);

            if (status.status === 'COMPLETED' && status.translated_text) {
                clearInterval(pollInterval);
                createDownloadLinkFromText(status.translated_text, originalFileName); // Use original file name here
            } else if (status.status === 'FAILED') {
                clearInterval(pollInterval);
                alert('Translation failed. Please try again.');
                updateProgress('FAILED');
            }
        } catch (error) {
            console.error('Polling error:', error);
            // Handle error case: if the first poll fails, still show "Translation in progress..."
            updateProgress('PROCESSING'); // Keep showing that it's in progress
        }
    }, CONFIG.POLL_INTERVAL_MS); // Check every n seconds
}

// Update the progress bar and status message
function updateProgress(status) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    switch (status) {
        case 'PROCESSING':
            progressBar.value = 50;  // Example: set to 50% during processing
            progressText.textContent = 'Translation in progress...';
            break;
        case 'COMPLETED':
            progressBar.value = 100;
            progressText.textContent = 'Translation completed!';
            break;
        case 'FAILED':
            progressBar.value = 0;
            progressText.textContent = 'Translation failed.';
            break;
        default:
            progressBar.value = 0;
            progressText.textContent = ''; // Don't show any progress message on page load
    }
}

function createDownloadLinkFromText(text, originalFileName) {
    const downloadLink = document.getElementById('downloadLink');

    const blob = new Blob([text], { type: 'text/plain' });
    const blobUrl = URL.createObjectURL(blob);

    // Change the file name from the original file name (e.g., test.pdf) to test.txt
    const filename = originalFileName.replace('.pdf', '.txt'); // Ensure to replace .pdf with .txt

    downloadLink.href = blobUrl;
    downloadLink.download = filename; // Suggested filename
    downloadLink.textContent = `Download ${filename}`;
    downloadLink.style.display = 'inline-block';
}

// Upload the PDF file to S3 and start the translation
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

    originalFileName = file.name; // Save the original file name

    try {
        // 1. Get pre-signed URL
        const response = await fetch(`${API_URL}/generate-url`);
        if (!response.ok) throw new Error('Failed to get upload URL');
        // Parse the body as a string and then parse the nested JSON body
        const responseBody = await response.json();
        const parsedBody = JSON.parse(responseBody.body);  // Parsing the string inside the body

        // Extract url and request_id
        const { url, request_id } = parsedBody;

        // Show loading and progress
        updateProgress('PROCESSING'); // Show "Translation in progress..." as soon as we start uploading

        // 2. Upload to S3
        await fetch(url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': 'application/pdf'
            }
        });

        // 3. Start polling
        startPolling(request_id);
        console.log('File uploaded successfully:', request_id);
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Error: ' + error.message);
        updateProgress('FAILED');
    }
}
