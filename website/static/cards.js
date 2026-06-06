// Keeping track of selected card id
let selectedCard = null

// Loading cards when page starts
loadCards()

// Fetching all cards from backend
async function loadCards(){

    try{

        const response =
        await fetch("/api/cards")

        const cards =
        await response.json()

        const grid =
        document.getElementById(
            "cards-grid"
        )

        // Clearing grid before adding cards
        grid.innerHTML = ""

        // Looping through all cards
        cards.forEach(card=>{

            grid.innerHTML += `

            <div
            class="card-tile"
            onclick="showCard(${card.id})">

                <img
                src="${card.image}"
                alt="${card.name}">

                <h4>
                    ${card.name}
                </h4>

            </div>

            `
        })

    }
    catch(error){

        console.error(error)
    }
}

// Opening card modal with full details
async function showCard(cardId){

    try{

        const response =
        await fetch(
            `/api/card/${cardId}`
        )

        const card =
        await response.json()

        // If backend fails
        if(!card.success){

            return
        }

        selectedCard = card.id

        // Filling modal content
        document.getElementById(
            "modal-image"
        ).src = card.image

        document.getElementById(
            "modal-name"
        ).innerText = card.name

        document.getElementById(
            "modal-mana"
        ).innerText =
        card.mana_cost || ""

        document.getElementById(
            "modal-rarity"
        ).innerText =
        "Rarity: " +
        (card.rarity || "")

        document.getElementById(
            "modal-set"
        ).innerText =
        "Set: " +
        (card.set || "")

        document.getElementById(
            "modal-text"
        ).innerText =
        card.oracle_text || ""

        document.getElementById(
            "modal-price"
        ).innerText =
        "$" +
        (card.price || "0.00")

        document.getElementById(
            "card-modal"
        ).style.display = "flex"

    }
    catch(error){

        console.error(error)
    }
}

// Closing modal function
function closeCardModal(){

    document.getElementById(
        "card-modal"
    ).style.display = "none"
}

// Close button listener
const closeBtn =
document.getElementById(
    "close-card-modal"
)

if(closeBtn){

    closeBtn.onclick =
    closeCardModal
}

// Clicking outside modal closes it
window.addEventListener(
    "click",
    (event)=>{

        const modal =
        document.getElementById(
            "card-modal"
        )

        if(event.target === modal){

            closeCardModal()
        }
    }
)

// Wishlist button
const wishlistBtn =
document.getElementById(
    "wishlist-btn"
)

if(wishlistBtn){

    wishlistBtn.onclick =
    ()=>{

        if(!selectedCard){
            return
        }

        addWishlist(selectedCard)
    }
}

// Sending wishlist request
async function addWishlist(cardId){

    try{

        const response =
        await fetch(
            "/api/wishlist/add",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({
                    card_id:cardId
                })
            }
        )

        const data =
        await response.json()

        if(data.success){

            wishlistBtn.innerText =
            "Added ✓"

            setTimeout(()=>{

                wishlistBtn.innerText =
                "Add To Wishlist"

            },2000)

        }
        else{

            alert(
                data.message ||
                "Already in wishlist"
            )
        }

    }
    catch(error){

        console.error(error)

        alert(
            "Unable to add card"
        )
    }
}