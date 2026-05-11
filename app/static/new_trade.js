document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", async (e) => {
        const button = e.target.closest(".trade-toggle-btn");
        if (!button) return;

        button.disabled = true;

        const userCardId = parseInt(button.dataset.userCardId, 10);
        const currentAction = button.dataset.action;

        try {
            const res = await fetch("/trading/new/update-ajax", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    action: currentAction,
                    user_card_id: userCardId
                })
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                alert(data.error || "Something went wrong");
                button.disabled = false;
                return;
            }

            if (currentAction === "add_requested") {
                button.dataset.action = "remove_requested";
                button.textContent = "Remove";
                button.classList.remove("btn-success");
                button.classList.add("btn-danger");
            } else if (currentAction === "remove_requested") {
                button.dataset.action = "add_requested";
                button.textContent = "Add";
                button.classList.remove("btn-danger");
                button.classList.add("btn-success");
            } else if (currentAction === "add_offered") {
                button.dataset.action = "remove_offered";
                button.textContent = "Remove";
                button.classList.remove("btn-success");
                button.classList.add("btn-danger");
            } else if (currentAction === "remove_offered") {
                button.dataset.action = "add_offered";
                button.textContent = "Add";
                button.classList.remove("btn-danger");
                button.classList.add("btn-success");
            }

            const requestedCount = document.getElementById("requested-count");
            const offeredCount = document.getElementById("offered-count");
            const requestedSection = document.getElementById("requested-cards-section");
            const offeredSection = document.getElementById("offered-cards-section");

            if (requestedCount) requestedCount.textContent = data.requested_count;
            if (offeredCount) offeredCount.textContent = data.offered_count;
            if (requestedSection) requestedSection.innerHTML = data.requested_html;
            if (offeredSection) offeredSection.innerHTML = data.offered_html;

        } catch (err) {
            alert("Network error");
        }

        button.disabled = false;
    });
});
