document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector("#inventory-container");
  container.addEventListener("click", handleClick);
})


async function handleClick(e) {
  const button = e.target.closest("button");

  if (!button) return;

  if (button.classList.contains("add-to-deck")) {
    return addToDeck(button);
  }

  if (button.classList.contains("remove-from-deck")) {
    return removeFromDeck(button);
  }

  if (button.classList.contains("tradable-toggle")) {
    return toggleTradable(button);
  }
}


async function addToDeck(button) {
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


async function removeFromDeck(button) {
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


async function toggleTradable(button) {
  const card = button.closest(".inventory-card-wrapper");
  const current = button.dataset.tradable === "true";
  const newValue = !current;
  await setTradable(button, card.dataset.cardId, newValue);
}


async function setTradable(button, cardId, value) {
  button.disabled = true;

  try {
    const res = await fetch("/api/user_card/tradable", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_card_id: cardId,
        value: value
      })
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Something went wrong");
      button.disabled = false;
      return;
    }
    button.dataset.tradable = value.toString();
    if (value) {
      button.textContent = "Tradable";
      button.classList.remove("btn-warning");
      button.classList.add("btn-success");
    } else {
      button.textContent = "Not Tradable";
      button.classList.remove("btn-success");
      button.classList.add("btn-warning");
    }
  } catch (err) {
    alert("Network error");
  }
  button.disabled = false;
}
