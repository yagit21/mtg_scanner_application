
// Tracking currently opened collection
let activeCollection = null;

// Tracking if we are adding cards into existing collection
let isAddMode = false;

// Running once page loads
document.addEventListener("DOMContentLoaded", () => {

    loadCollections();

    // New collection button
    const newBtn = document.getElementById("new-collection");

    if (newBtn) {

        newBtn.onclick = () => {

            isAddMode = false;
            activeCollection = null;

            openCollectionModal();
        };
    }

    // Create / Add button inside modal
    const createBtn = document.getElementById("create-collection-btn");

    if (createBtn) {

        createBtn.onclick = handleCreateOrAdd;
    }
});

// Getting all collections from backend
async function loadCollections() {

    const res = await fetch("/api/collections");
    const collections = await res.json();

    const container = document.getElementById("collections");

    container.innerHTML = "";

    collections.forEach(c => {

        const div = document.createElement("div");
        div.className = "collection-card";

        div.innerHTML = `
            <h3>${c.name}</h3>
            <button class="delete-btn">Delete</button>
        `;

        // Opening collection when clicking card
        div.onclick = () => openCollection(c.id);

        // Prevent delete button triggering open
        div.querySelector(".delete-btn").onclick = (e) => {

            e.stopPropagation();

            deleteCollection(c.id);
        };

        container.appendChild(div);
    });
}

// Opening selected collection view
async function openCollection(id) {

    activeCollection = id;

    const root = document.getElementById("collection-cards");

    root.replaceChildren();

    const res = await fetch(`/api/collections/${id}`);
    const cards = await res.json();

    const wrapper = document.createElement("div");

    wrapper.innerHTML = `
        <div class="collection-topbar">

            <button id="close-btn">Close</button>

            <button id="add-btn">Add Cards</button>

        </div>

        <div class="collection-view"></div>
    `;

    root.appendChild(wrapper);

    // Close collection
    document.getElementById("close-btn").onclick = closeCollection;

    // Switch to add mode
    document.getElementById("add-btn").onclick = () => {

        isAddMode = true;

        openCollectionModal();
    };

    const view = wrapper.querySelector(".collection-view");

    // Rendering cards in collection
    cards.forEach(card => {

        const el = document.createElement("div");

        el.className = "arena-card";

        el.style.backgroundImage =
        `url('${card.image}')`;

        el.onmouseenter = () => previewCard(card.image);
        el.onmouseleave = hidePreview;

        el.innerHTML = `
            <div class="card-actions">
                <button class="remove-btn">Remove</button>
            </div>
        `;

        // Remove card from collection
        el.querySelector(".remove-btn").onclick = (e) => {

            e.stopPropagation();

            removeCard(id, card.id);
        };

        view.appendChild(el);
    });
}
// Closing collection
function closeCollection() {

    activeCollection = null;
    isAddMode = false;

    document.getElementById("collection-cards").replaceChildren();

    hidePreview();
}

// Opening modal for creating or adding cards
async function openCollectionModal() {

    const modal = document.getElementById("collection-modal");

    modal.style.display = "flex";

    const nameInput = document.getElementById("collection-name");
    const list = document.getElementById("saved-card-list");

    list.innerHTML = "";

    // Hide name input if we are just adding cards
    nameInput.style.display = isAddMode ? "none" : "block";

    const res = await fetch("/api/saved-cards");
    const cards = await res.json();

    cards.forEach(card => {

        const label = document.createElement("label");

        label.innerHTML = `
            <input type="checkbox" value="${card.id}">
            ${card.name}
        `;

        list.appendChild(label);
        list.appendChild(document.createElement("br"));
    });
}

//Create and Adding handler
async function handleCreateOrAdd() {

    const selected = Array.from(
        document.querySelectorAll("#saved-card-list input:checked")
    ).map(c => parseInt(c.value));

    if (selected.length === 0) {

        alert("Select cards");
        return;
    }
    // Adding Cards to collections
    if (isAddMode && activeCollection) {

        for (const cardId of selected) {

            await fetch("/api/collections/add-card", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    collection_id: activeCollection,
                    card_id: cardId
                })
            });
        }

        closeModal();
        openCollection(activeCollection);
        return;
    }

    //Creating Collections
    const name = document.getElementById("collection-name").value.trim();

    if (!name) {

        alert("Enter name");
        return;
    }

    await fetch("/api/collections/create", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            name,
            cards: selected
        })
    });

    closeModal();
    loadCollections();
}
//Close Modal
function closeModal() {

    document.getElementById("collection-modal").style.display = "none";

    document.getElementById("collection-name").value = "";

    isAddMode = false;

    activeCollection = null;
}
//Removing Cards From Collections
async function removeCard(collectionId, cardId) {

    await fetch("/api/collections/remove-card", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            collection_id: collectionId,
            card_id: cardId
        })
    });

    openCollection(collectionId);
}
//Deleting Collections
async function deleteCollection(id) {

    await fetch(`/api/collections/delete/${id}`, {

        method: "DELETE"
    });

    loadCollections();
    closeCollection();
}

//Previews
function previewCard(img) {

    const panel = document.getElementById("preview-panel");
    const preview = document.getElementById("preview-image");

    preview.src = img;
    panel.style.display = "block";
}

function hidePreview() {

    document.getElementById("preview-panel").style.display = "none";
}