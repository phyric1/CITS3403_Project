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
  const card = button.closest(".card-wrapper")

  const ids = card.dataset.cardIds.split(",");
  const user_card_id = ids.shift();
  card.dataset.cardIds = ids.join(",");

  const res = await fetch("/api/deck/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ user_card_id: user_card_id })
  })

  const data = await res.json();
  if (!res.ok) {
    alert(data.error);
    button.disabled = false;
    return
  }

  updateDeckCount(1);

  const deck_card = card.cloneNode(true);
  deck_card.dataset.cardId = user_card_id;
  const quantity_label = deck_card.querySelector(".card-quantity");
  if (quantity_label) quantity_label.remove();

  deck_card.querySelector(".add-to-deck")?.remove();
  addRemoveButton(deck_card);

  document.getElementById("deck").appendChild(deck_card);

  const quantity = getQuantity(card);
  if (quantity <= 1) {
    card.remove();
  } else {
    setQuantity(card, quantity - 1);
  }

  button.disabled = false;
}


async function removeFromDeck(button) {
  button.disabled = true;
  const card = button.closest(".card-wrapper")

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

  const card_name = card.querySelector(".card-title-box p").textContent.trim();
  const uses = card.querySelector(".card-uses")?.textContent.trim() ?? "";
  const inventory = document.getElementById("inventory");

  // Search for stack of same card with same uses in inventory
  const existing_stack = [...inventory.querySelectorAll(".card-wrapper")]
      .find(card => {const existing_name = card.querySelector(".card-title-box p").textContent.trim();
      const existing_uses = card.querySelector(".card-uses")?.textContent.trim() ?? "";
      return existing_name === card_name && existing_uses === uses;
    });

  if (existing_stack) {
    const quantity = getQuantity(existing_stack);
    setQuantity(existing_stack, quantity + 1)

    const ids = existing_stack.dataset.cardIds
      ? existing_stack.dataset.cardIds.split(",")
      : [];
    ids.push(card.dataset.cardId);
    existing_stack.dataset.cardIds = ids.join(",");
  } else {
    const inventory_card = card.cloneNode(true);
    inventory_card.dataset.cardIds = card.dataset.cardId;
    inventory_card.removeAttribute("data-card-id");
    inventory_card.querySelector(".remove-from-deck")?.remove();

    addAddButton(inventory_card);
    inventory.appendChild(inventory_card);
  }

  card.remove();
  button.disabled = false;
}


function addRemoveButton(card) {
  const button = document.createElement("button")
  button.className = "btn btn-sm btn-danger w-100 mt-1 remove-from-deck";
  button.textContent = "Remove";
  card.appendChild(button);
}


function addAddButton(card) {
  const button = document.createElement("button")
  button.className = "btn btn-sm btn-success w-100 mt-1 add-to-deck";
  button.textContent = "Add to Deck";
  card.appendChild(button);
}


function updateDeckCount(change) {
  const deck_card_count = document.getElementById("deck-count");
  let current = parseInt(deck_card_count.textContent);
  deck_card_count.textContent = current + change;
}


function getQuantity(card) {
  const quantity = card.querySelector(".card-quantity");
  if (!quantity) return 1;
  return parseInt(quantity.textContent.replace("x", ""));
}


function setQuantity(card, quantity) {
  let quantity_div = card.querySelector(".card-quantity");
  if (quantity <= 1) {
    if (quantity_div) quantity_div.remove();
    return;
  }

  if (!quantity_div) {
    quantity_div = document.createElement("div");
    quantity_div.className = "card-quantity";
    card.querySelector(".game-card").prepend(quantity_div);
  }
  quantity_div.textContent = `x${quantity}`;
}


async function toggleTradable(button) {
  const card = button.closest(".card-wrapper");
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
