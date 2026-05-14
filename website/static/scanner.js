const video = document.getElementById("webcam")
const button = document.getElementById("scan-btn")
const canvas = document.getElementById("canvas")
const resultDiv = document.getElementById("result")


navigator.mediaDevices.getUserMedia({
    video: true
})
.then((stream) => {
    video.srcObject = stream
})
.catch((err) => {
    console.log(err)
})

button.addEventListener("click", async () => {

    const context = canvas.getContext("2d")

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    context.drawImage(video, 0, 0)

    const imageData = canvas.toDataURL("image/jpeg")

    resultDiv.innerHTML = "Scanning..."

    const response = await fetch("/scan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image: imageData
        })
    })

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