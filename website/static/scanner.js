
// Taking important page elements so we can use them later
const video = document.getElementById("webcam");
const scanBtn = document.getElementById("scan-btn");
const flipBtn = document.getElementById("flip-btn");
const canvas = document.getElementById("canvas");
const saveBtn = document.getElementById("save-btn");

// Storing current camera mode (front or back)
let currentCamera = "user";

// Storing last scanned card so we can save it later
let currentCard = null;

// Storing camera stream so we can properly reset it
let currentStream = null;

// Starting camera feed
async function startCamera() {

    try {

        // If camera already running we stop it first
        if(currentStream){

            currentStream.getTracks().forEach(track => track.stop());
        }

        // Requesting camera access
        const stream = await navigator.mediaDevices.getUserMedia({

            video: {
                facingMode: currentCamera
            }
        });

        // Saving stream so we can stop it later
        currentStream = stream;

        // Showing camera on video element
        video.srcObject = stream;

    } catch (err) {

        console.error("Camera error:", err);

        alert("Could not access camera");
    }
}

// Starting camera on page load
startCamera();

// Switching between front and back camera
flipBtn.onclick = () => {

    currentCamera =
    currentCamera === "user"
    ? "environment"
    : "user";

    startCamera();
};

// Taking snapshot and sending to backend
scanBtn.onclick = async () => {

    const context = canvas.getContext("2d");

    // Matching canvas size to camera feed
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Drawing camera frame onto canvas
    context.drawImage(video, 0, 0);

    // Converting image to base64
    const image = canvas.toDataURL("image/jpeg");

    // Sending image to backend for prediction
    const response = await fetch("/scan", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({ image })
    });

    const result = await response.json();

    // If scan failed show message
    if (!result.success) {

        alert(result.message || "Scan failed");
        return;
    }

    // Storing scanned card globally
    currentCard = result;

    // Updating UI with scanned card data
    document.getElementById("card-name").innerText =
    result.card || "Unknown";

    document.getElementById("confidence").innerText =
    "Confidence: " + (result.confidence || 0);

    document.getElementById("card-type").innerText =
    result.rarity || "";

    document.getElementById("card-text").innerText =
    result.oracle_text || "";

    document.getElementById("card-price").innerText =
    "$" + (result.price || 0);

    // Updating card image if available
    if (result.image) {

        document.getElementById("card-art").src =
        result.image;
    }
};

// Saving scanned card to account
saveBtn.onclick = async () => {

    if (!currentCard) {

        alert("No card scanned yet");
        return;
    }

    const response = await fetch("/api/save-card", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            card_name: currentCard.card
        })
    });

    const data = await response.json();

    // If save worked
    if (data.success) {

        showPopup("Card Saved!");

        // Clearing current card so user doesn't double save same scan
        currentCard = null;

    } else {

        showLoginPopup();
    }
};

// Showing login popup if user is not authenticated
function showLoginPopup() {

    const popup = document.getElementById("login-popup");

    if (popup) popup.style.display = "flex";
}

// Showing temporary popup message
function showPopup(msg) {

    const popup = document.getElementById("login-popup");

    if (!popup) {

        alert(msg);
        return;
    }

    popup.querySelector("h2").innerText = msg;
    popup.style.display = "flex";

    setTimeout(() => {

        popup.style.display = "none";

    }, 1500);
}