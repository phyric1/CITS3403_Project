document.addEventListener('keydown', (e) => {
        switch (e.code) {
            case 'ArrowLeft':
                e.preventDefault()
                console.log('left')
                move('left')
                break
            case 'ArrowRight':
                e.preventDefault()
                console.log('right')
                move('right')
                break
            case 'ArrowUp':
                e.preventDefault()
                console.log('up')
                move('up')
                break
            case 'ArrowDown':
                e.preventDefault()
                console.log('down')
                move('down')
                break
        }
    })

const handArea = document.getElementById('hand-cards');
if (handArea) {
    handArea.addEventListener('click', (e) => {
        const wrapper = e.target.closest('.card-wrapper');
        if (!wrapper) return;

        const wrappers = Array.from(handArea.querySelectorAll('.card-wrapper'));
        const index = wrappers.indexOf(wrapper);
        if (index === -1) return;

        move(`${index}`);
    });
}

    function move(input) {
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: input }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            updateGridDisplay(data.grid, data.filter);
            updateGameState(data.turn, data.hp, data.keys, data.gold, data.stealth, data.floor, data.deckMax, data.deckSize);
            if (data.cards) {
                updateCards(data.cards);
            }
            if (data.discard) {
                updateDiscard(data.discard);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function updateCards(cards) {
        const handArea = document.getElementById('hand-cards');
        if (!handArea) return;

        handArea.innerHTML = '';
        cards.forEach(card => {
            const cardWrapper = document.createElement('div');
            cardWrapper.className = 'card-wrapper';

            const usesHtml = card.uses_remaining !== undefined && card.uses_remaining !== null ?
                `<div class="card-uses">${card.uses_remaining === -1 ? '∞' : `${card.uses_remaining}/${card.uses}`}</div>` : '';

            const maxInDeck = card.max_in_deck === -1 ? '∞' : card.max_in_deck;
            const cardHtml = `
                <div class="game-card rarity-${card.rarity}">
                    ${usesHtml}
                    <div class="card-image type-${card.type}">
                        <img src="/static/img/${card.type}.png" alt="${card.type}">
                    </div>
                    <div class="card-title-box" title="${card.name}">
                        <p>${card.name}</p>
                    </div>
                    <div class="card-divider"></div>
                    <div class="card-body" title="${card.effect}">
                        <div class="effect-wrapper">
                            <p id="effect">${card.effect}</p>
                        </div>
                        <div class="card-footer">
                            <p id="footer">${card.type.charAt(0).toUpperCase() + card.type.slice(1)} - Max ${maxInDeck}</p>
                        </div>
                    </div>
                </div>
            `;

            cardWrapper.innerHTML = cardHtml;
            handArea.appendChild(cardWrapper);
        });
    }

    function updateDiscard(card) {
        const discardSlot = document.getElementById("discard");
        if (!discardSlot) return;

        discardSlot.innerHTML = '';
        const cardWrapper = document.createElement('div');
        cardWrapper.className = 'card-wrapper';

        const usesHtml = card.uses_remaining !== undefined && card.uses_remaining !== null ?
        `<div class="card-uses">${card.uses_remaining === -1 ? '∞' : `${card.uses_remaining}/${card.uses}`}</div>` : '';

        const maxInDeck = card.max_in_deck === -1 ? '∞' : card.max_in_deck;
        const cardHtml = `
                <div class="game-card rarity-${card.rarity}">
                    ${usesHtml}
                    <div class="card-image type-${card.type}">
                        <img src="/static/img/${card.type}.png" alt="${card.type}">
                    </div>
                    <div class="card-title-box" title="${card.name}">
                        <p>${card.name}</p>
                    </div>
                    <div class="card-divider"></div>
                    <div class="card-body" title="${card.effect}">
                        <div class="effect-wrapper">
                            <p id="effect">${card.effect}</p>
                        </div>
                        <div class="card-footer">
                            <p id="footer">${card.type.charAt(0).toUpperCase() + card.type.slice(1)} - Max ${maxInDeck}</p>
                        </div>
                    </div>
                </div>
            `;

        cardWrapper.innerHTML = cardHtml;
        discardSlot.appendChild(cardWrapper);
    };

    function updateGridDisplay(newGrid, filter) {
        const gridContainer = document.getElementById('grid');
        gridContainer.innerHTML = '';

        for (let i = 0; i < newGrid.length; i++) {
            for (let j = 0; j < newGrid[i].length; j++) {
                const tile = document.createElement('div');
                tile.className = 'grid-tile';
                if (newGrid[i][j] === 0) {
                    tile.classList.add('floor', 'bg-secondary');
                } else if (newGrid[i][j] === 1) {
                    tile.classList.add('wall', 'bg-dark');
                } else if (newGrid[i][j] === 2) {
                    tile.classList.add('start', 'bg-success');
                } else if (newGrid[i][j] === 3) {
                    tile.classList.add('end', 'bg-danger');
                } else if (newGrid[i][j] === 4) {
                    tile.classList.add('enemy', 'bg-info');
                } else if (newGrid[i][j] === -1) {
                    tile.classList.add('bg-dark');
                } else if (newGrid[i][j] === 5) {
                    tile.classList.add('key', 'bg-white');
                } else if (newGrid[i][j] === 6) {
                    tile.classList.add('exit', 'bg-primary');
                } else if (newGrid[i][j] === 7) {
                    tile.classList.add('gold', 'bg-warning');
                }

                if (filter[i][j] === 1 || filter[i][j] === 5) {
                    tile.classList.add('bright');
                } else {
                    tile.classList.remove('bright');
                }

                if (filter[i][j] === 5) {
                    tile.classList.add('clickable-tile');
                    tile.classList.add('blink-fast');
                    tile.dataset.x = j;
                    tile.dataset.y = i;
                    tile.style.cursor = 'pointer';
                    tile.addEventListener('click', () => {
                        handleFilterTileClick(j, i);
                    });
                }

                gridContainer.appendChild(tile);
            }
        }
    }

    function handleTileClick(x, y) {
        return { x, y };
    }

    function updateGameState(turn, hp, keys, gold, stealth, floor, deckMax, deckSize) {
        const turnCount = document.getElementById('turn-value');
        turnCount.textContent = turn;

        const health = document.getElementById('health-value');
        health.textContent = hp;

        const keyCount = document.getElementById('keys-value');
        keyCount.textContent = keys;

        const stealthCount = document.getElementById('stealth-value');
        stealthCount.textContent = stealth;

        const goldCount = document.getElementById('treasure-value');
        goldCount.textContent = gold;

        const levelCount = document.getElementById('floor-value');
        levelCount.textContent = floor;

        const deckMaxSize = document.getElementById('deck-max');
        deckMaxSize.textContent = deckMax;

        const deckSizeCount = document.getElementById('deck-size');
        deckSizeCount.textContent = deckSize;
    }