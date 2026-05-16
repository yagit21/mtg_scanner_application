const video = document.getElementById("webcam") //This gets the video (show camera)
const button = document.getElementById("scan-btn") //The button that triggers the scan
const canvas = document.getElementById("canvas") //A hidden canvas (to process the image)
const resultDiv = document.getElementById("result") //Display the result

//Requesting permission to access the user's camera
navigator.mediaDevices.getUserMedia({
    video: true
})
.then((stream) => {
    video.srcObject = stream //Setting the camera as the source of the video
})
.catch((err) => {
    console.log(err)
})
//When the button is clicked it takes a snapshot
button.addEventListener("click", async () => {
    //Creates a canvas size to match the video and draws the current video frame onto the canvas
    const context = canvas.getContext("2d")
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    context.drawImage(video, 0, 0)
    //Converts the image into a base64 encoded JPEG string (which can be sent over the internet)
    const imageData = canvas.toDataURL("image/jpeg")
    //'Scanning...' message in the result area
    resultDiv.innerHTML = "Scanning..."
    //Using a fetch API to send a POST request to the /scan route
    const response = await fetch("/scan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image: imageData
        })
    })
    //Displays the result
    const result = await response.json()

    if (result.success) {
        resultDiv.innerHTML = `
            <h2>${result.card}</h2>
            <p>Confidence: ${result.confidence}</p>
        `
    } else {
        resultDiv.innerHTML = result.message
    }
})