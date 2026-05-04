document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".add-to-deck").forEach(button => {
    button.onclick = addToDeck;
  });
  document.querySelectorAll(".remove-from-deck").forEach(button => {
    button.onclick = removeFromDeck;
  });
})


async function addToDeck(e) {
  const button = e.target;
  button.disabled = true;
  const card = button.closest(".inventory-card-wrapper")

  const res = await fetch("/api/deck/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({user_card_id: card.dataset.cardId})
  })

  const data = await res.json();
  if (!res.ok) {
    alert(data.error);
    button.disabled = false;
    return
  }

  updateDeckCount(1);
  document.getElementById("deck").appendChild(card);
  button.remove();
  addRemoveButton(card);
}


async function removeFromDeck(e) {
  const button = e.target
  button.disabled = true;
  const card = button.closest(".inventory-card-wrapper")

  const res = await fetch("/api/deck/remove", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({user_card_id: card.dataset.cardId})
  })

  const data = await res.json();
  if (!res.ok) {
    alert(data.error);
    button.disabled = false;
    return
  }

  updateDeckCount(-1);
  document.getElementById("inventory").appendChild(card);
  button.remove();
  addAddButton(card);
}


function addRemoveButton(card) {
  const button = document.createElement("button")
  button.className = "btn btn-sm btn-danger w-100 mt-1 remove-from-deck";
  button.textContent = "Remove";
  button.onclick = removeFromDeck;
  card.appendChild(button);
}


function addAddButton(card) {
  const button = document.createElement("button")
  button.className = "btn btn-sm btn-success w-100 mt-1 add-to-deck";
  button.textContent = "Add to Deck";
  button.onclick = addToDeck;
  card.appendChild(button);
}


function updateDeckCount(change) {
  const deck_card_count = document.getElementById("deck-count");
  let current = parseInt(deck_card_count.textContent);
  deck_card_count.textContent = current + change;
}
