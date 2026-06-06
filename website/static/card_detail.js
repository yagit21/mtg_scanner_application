// Waiting for page to fully load before running anything
document.addEventListener("DOMContentLoaded", () => {

    // Loading all card related data at once
    loadBuyLinks(CARD_ID);
    loadAI(CARD_ID);
    loadPriceHistory(CARD_ID);

});


// Pulling buy links from backend
async function loadBuyLinks(id) {

    const res = await fetch(`/api/card/${id}/buy-links`);
    const data = await res.json();

    // Injecting buy links into page
    document.getElementById("buy-links").innerHTML = `
        <div class="buy-grid">

            <a target="_blank" href="${data.tcgplayer}">
                TCGPlayer
            </a>

            <a target="_blank" href="${data.cardmarket}">
                Cardmarket
            </a>

        </div>

        <div class="cheapest">
            Cheapest: <b>${data.cheapest}</b>
        </div>
    `;
}

//Report analysis

// Pulling report from backend
async function loadAI(id) {

    const res = await fetch(`/api/card/${id}/ai`);
    const data = await res.json();

    const rpBox = document.getElementById("rp-box");

    // If report box doesn't exist just stop
    if (!rpBox) return;

    // Displaying report analysis
    rpBox.innerHTML = `
        <h3>Report Analysis</h3>
        <div class="rp-rating">${data.rating}</div>
        <p>${data.comment}</p>
    `;
}

//Price History Graph:

// Drawing simple price graph on canvas
async function loadPriceHistory(id) {

    const res = await fetch(`/api/card/${id}/history`);
    const data = await res.json();

    const canvas = document.getElementById("price-chart");
    const ctx = canvas.getContext("2d");

    const prices = data.prices;

    // Clearing old graph
    ctx.clearRect(0,0,300,120);

    ctx.beginPath();

    // Plotting points into a line
    prices.forEach((p, i) => {

        const x = i * 45;
        const y = 120 - (p * 10);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });

    // Styling graph line
    ctx.strokeStyle = "#8b5cf6";
    ctx.lineWidth = 2;
    ctx.stroke();
}