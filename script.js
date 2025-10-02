async function scanURL() {
  const url = document.getElementById("url").value.trim();
  if (!url) return alert("Please enter a URL");

  startLoader();

  try {
    const response = await fetch("/check_url", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({url})
    });
    const result = await response.json();
    showResult(result);
  } catch (err) {
    showResult({safe: false, message: "Error connecting to server!"});
  } finally {
    stopLoader();
  }
}

async function scanQR() {
  const fileInput = document.getElementById("qrImage");
  if (fileInput.files.length === 0) return alert("Please upload a QR image");

  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = async function(event) {
    const base64Image = event.target.result;

    startLoader();

    try {
      const response = await fetch("/scan_qr", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({image: base64Image})
      });
      const result = await response.json();
      showResult(result);
    } catch (err) {
      showResult({safe: false, message: "Error scanning QR code!"});
    } finally {
      stopLoader();
    }
  };

  reader.readAsDataURL(file);
}

let videoStream;
let scanning = false;
const video = document.getElementById("video");
const startScanBtn = document.getElementById("startScanBtn");
const stopScanBtn = document.getElementById("stopScanBtn");

startScanBtn.addEventListener("click", async () => {
  if (scanning) return;
  scanning = true;
  startScanBtn.disabled = true;
  stopScanBtn.disabled = false;

  try {
    videoStream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
    video.srcObject = videoStream;
    video.setAttribute("playsinline", true);
    video.play();
    scanRealtime();
  } catch (err) {
    alert("Could not access camera: " + err);
    scanning = false;
    startScanBtn.disabled = false;
    stopScanBtn.disabled = true;
  }
});

stopScanBtn.addEventListener("click", () => {
  scanning = false;
  startScanBtn.disabled = false;
  stopScanBtn.disabled = true;
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop());
  }
  video.srcObject = null;
});

async function scanRealtime() {
  if (!scanning) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const base64Image = canvas.toDataURL("image/png");

  try {
    const response = await fetch("/scan_qr_realtime", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({image: base64Image})
    });
    const result = await response.json();
    if (result.no_qr) {
      showResult({safe: null, message: "No QR code detected."});
    } else {
      showResult(result);
      if (result.safe) {
        // Stop scanning if safe QR code detected
        stopScanBtn.click();
        return;
      }
    }
  } catch (err) {
    showResult({safe: false, message: "Error scanning QR code!"});
  }

  setTimeout(scanRealtime, 1000);
}

function showResult(result) {
  const resultCard = document.getElementById("resultCard");
  const resultBadge = document.getElementById("resultBadge");
  const resultMessage = document.getElementById("resultMessage");

  if (result.safe === true) {
    resultBadge.textContent = "SAFE";
    resultBadge.className = "badge safe";
    let message = result.message || "The QR code or URL is safe.";
    if (result.analysis) {
      message += `<br>Type: ${result.analysis.type}<br>Length: ${result.analysis.length}<br>Preview: ${result.analysis.content_preview}`;
    }
    resultMessage.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
  } else if (result.safe === false) {
    resultBadge.textContent = "UNSAFE";
    resultBadge.className = "badge unsafe";
    let message = result.message || "Warning! The QR code or URL may be malicious.";
    if (result.details) {
      message += `<br>Details: ${result.details.info || result.details}`;
    }
    resultMessage.innerHTML = `<i class="fas fa-times-circle"></i> ${message}`;
  } else {
    // Neutral or no QR code detected
    resultBadge.textContent = "NO QR";
    resultBadge.className = "badge";
    resultMessage.innerHTML = `<i class="fas fa-info-circle"></i> ${result.message || "No QR code detected."}`;
  }

  resultCard.style.display = "block";
}
