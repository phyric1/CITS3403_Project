const TILE_CLASS = {
    "-1": "dark",
    "0": "floor",
    "1": "wall",
    "2": "start",
    "3": "end",
    "4": "enemy",
    "5": "key",
    "6": "exit",
    "7": "gold",
    "8": "finish"
};

const DIRECTION_NAMES = {
    0: 'left',
    1: 'right',
    2: 'up',
    3: 'down'
};
const DIRECTION_CLASSES = [
    'player-left', 'player-right', 'player-up', 'player-down',
    'enemy-left', 'enemy-right', 'enemy-up', 'enemy-down'
];

const SOUNDS = {
    player_move: new Audio("/static/sounds/blip.wav"),
    pickup: new Audio("/static/sounds/pickup.wav"),
    floor_cleared: new Audio("/static/sounds/clear.wav"),
    player_hurt: new Audio("/static/sounds/hurt.wav"),
    game_win: new Audio("/static/sounds/win.wav"),
    game_lose: new Audio("/static/sounds/lose.wav"),
    play_card: new Audio("/static/sounds/card.wav"),
    explosion: new Audio("/static/sounds/explosion.wav"),
    attack: new Audio("/static/sounds/slash.wav"),
    alert: new Audio("/static/sounds/alert.ogg"),
    buff: new Audio("/static/sounds/buff.wav"),
    flash: new Audio("/static/sounds/flash.wav"),
    guard: new Audio("/static/sounds/guard.wav"),
};

let previousGrid = [];
let previousEntities = [];
let previousFilter = [];
const tileElements = [];
let gameEnded = false;

function playSound(event) {
    if (Array.isArray(event)) {
        event.forEach(playSound);
        return;
    }
    const sound = SOUNDS[event];
    if (!sound) return;
    sound.currentTime = 0;
    sound.play();
}

function setTileEntity(tile, entity) {
    tile.classList.remove(...DIRECTION_CLASSES);
    if (!entity) {
        return;
    }
    const direction = DIRECTION_NAMES[entity.direction] || 'down';
    const className = `${entity.type}-${direction}`;
    tile.classList.add(className);
}

function createGridTiles(grid) {
    console.log('Creating grid tiles');
    const gridElement = document.getElementById('grid');
    if (!gridElement || !Array.isArray(grid)) return;

    gridElement.innerHTML = '';
    tileElements.length = 0;
    gridElement.style.gridTemplateColumns = `repeat(${grid[0].length}, 24px)`;

    for (let row = 0; row < grid.length; row++) {
        tileElements[row] = [];
        for (let col = 0; col < grid[row].length; col++) {
            const tile = document.createElement('div');
            tile.className = `grid-tile row-${row} col-${col}`;
            tile.dataset.tileType = '';
            tile.addEventListener('click', () => handleTileClick(col, row));
            tileElements[row][col] = tile;
            gridElement.appendChild(tile);
        }
    }
}

document.addEventListener('keydown', (e) => {
        switch (e.code) {
            case 'ArrowLeft':
                e.preventDefault()
                move({ type: 'move', direction: 'left' })
                break
            case 'ArrowRight':
                e.preventDefault()
                move({ type: 'move', direction: 'right' })
                break
            case 'ArrowUp':
                e.preventDefault()
                move({ type: 'move', direction: 'up' })
                break
            case 'ArrowDown':
                e.preventDefault();
                move({ type: 'move', direction: 'down' });
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

        move({ type: 'pick_card', slot: index });
    });
}

    function move(input) {
        if (gameEnded) {
            return;
        }
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
                updateGridDisplay(data.grid, data.filter, data.entities);
                playSound(data.events);
            updateGameState(data.turn, data.hp, data.keys, data.gold, data.stealth, data.floor, data.maxFloors, data.deckMax, data.deckSize);
            if (data.isGameOver) {
                renderHand([], false, null);
                showGameEnd(data);
                return;
            }
            renderHand(data.cards, data.waitingForTileClick, data.pendingCard);
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

function assignTileVariants(tileElements, variantCount = 4) {
  for (let i = 0; i < tileElements.length; i++) {
    for (let j = 0; j < tileElements[i].length; j++) {
      const tile = tileElements[i][j];
      if (tile.dataset.variant) continue;

      const variant = hash2D(i, j) % variantCount;
      tile.dataset.variant = variant;
      tile.classList.add(`variant-${variant}`);
    }
  }
}

function hash2D(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return (h ^ (h >> 16)) >>> 0;
}

function updateGridDisplay(newGrid, filter, entities = []) {
    const entityMap = new Map();
    entities.forEach(entity => {
        entityMap.set(`${entity.x},${entity.y}`, entity);
    });

    for (let i = 0; i < newGrid.length; i++) {
        for (let j = 0; j < newGrid[i].length; j++) {
            const tile = tileElements[i][j];
            if (!previousGrid[i] || newGrid[i][j] !== previousGrid[i][j]) {
                setTileType(tile, newGrid[i][j]);
            }
            if (!previousFilter[i] || filter[i][j] !== previousFilter[i][j]) {
                setTileFilter(tile, filter[i][j]);
            }
            const newEntity = entityMap.get(`${j},${i}`);
            const prevEntity = previousEntities[i]?.[j];
            if (
                !prevEntity ||
                !newEntity ||
                prevEntity.type !== newEntity.type ||
                prevEntity.direction !== newEntity.direction
            ) {
                setTileEntity(tile, newEntity);
            }
        }
    }
    previousGrid = newGrid.map(row => [...row]);
    previousFilter = filter.map(row => [...row]);
    previousEntities = entities.map(e => ({
        ...e
    }));
}

function setTileType(tile, value) {
    const newClass = TILE_CLASS[value] || 'floor';

    if (tile.dataset.tileType === newClass) {
        return;
    }

    if (tile.dataset.tileType) {
        tile.classList.remove(tile.dataset.tileType);
    }

    tile.classList.add(newClass);
    tile.dataset.tileType = newClass;
}

function setTileFilter(tile, filterValue) {
    tile.classList.remove(
        "bright",
        "clickable-tile",
        "blink-fast"
    );
    if (filterValue === 1 || filterValue === 5) {
        tile.classList.add("bright");
    }
    if (filterValue === 5) {
        tile.classList.add(
            "clickable-tile",
            "blink-fast"
        );
    }
}

    function handleTileClick(x, y) {
        if (gameEnded) {
            return;
        }
        const tile = tileElements[y]?.[x];
        if (!tile || !tile.classList.contains('clickable-tile')) {
            return;
        }
        move({ type: 'tile_click', x: x, y: y });
    }

    function showGameEnd(data) {
        gameEnded = true;
        const overlay = document.getElementById('game-overlay');
        if (!overlay) return;

        overlay.classList.remove('d-none');
        overlay.classList.add('active');

        const title = document.getElementById('game-overlay-title');
        const message = document.getElementById('game-overlay-text');
        const stats = document.getElementById('game-overlay-stats');
        const button = document.getElementById('game-overlay-button');

        title.textContent = data.isWin ? 'Victory!' : 'Game Over';
        message.textContent = data.isWin
            ? `You reached the end and found a ${data.gameOverStats.reward} token.`
            : `You died :(`;

        stats.innerHTML = `
            <div>Floor: ${data.floor} / ${data.maxFloors}</div>
            <div>Turns: ${data.gameOverStats.turnsPlayed}</div>
            <div>Gold: ${data.gameOverStats.goldCollected}</div>
            <div>Enemies defeated: ${data.gameOverStats.enemiesDefeated}</div>
            <div>Difficulty: ${data.gameOverStats.difficulty}</div>
        `;

        button.textContent = data.isWin ? 'Claim Reward' : 'Play Again';
        button.onclick = resetGame;
    }

    function renderHand(cards, waitingForTileClick, pendingCard) {
        const handArea = document.getElementById('hand-cards');
        if (!handArea) return;

        handArea.classList.toggle('waiting', Boolean(waitingForTileClick));
        handArea.innerHTML = '';

        if (waitingForTileClick) {
            const cardName = pendingCard ? ` ${pendingCard}` : '';
            const message = `Select a tile to continue.`;
            handArea.innerHTML = `<div class="game-message">${message}</div>`;
            return;
        }

        if (!cards || cards.length === 0) {
            return;
        }

        updateCards(cards);
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

    function updateGameState(turn, hp, keys, gold, stealth, floor, floorMax, deckMax, deckSize) {
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

        const maxLevel = document.getElementById('floor-max');
        maxLevel.textContent = floorMax;

        const deckSizeCount = document.getElementById('deck-size');
        deckSizeCount.textContent = deckSize;

        const deckMaxSize = document.getElementById('deck-max');
        deckMaxSize.textContent = deckMax;
    }

function loadGameState() {
    fetch('/game/state')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Game state error:', data.error);
                return;
            }
            createGridTiles(data.grid);
            console.log("Loading state")
            assignTileVariants(tileElements, 2);
            updateGridDisplay(data.grid, data.filter, data.entities);
            updateGameState(data.turn, data.hp, data.keys, data.gold, data.stealth, data.floor, data.maxFloors, data.deckMax, data.deckSize);
            if (data.isGameOver) {
                renderHand([], false, null);
                showGameEnd(data);
                return;
            }
            renderHand(data.cards, data.waitingForTileClick, data.pendingCard);
            if (data.discard) {
                updateDiscard(data.discard);
            }
        })
        .catch((error) => console.error('Error loading game state:', error));
}

function resetGame() {
        fetch('/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/game';
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function startGame() {
        const difficulty = document.getElementById("difficulty").value;

        fetch('/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty })
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/game';
            }
        })
        .catch(error => console.error('Error:', error));
    }

window.startGame = startGame;

document.addEventListener('DOMContentLoaded', () => {
    // If on the start page, update the displayed max floor count when difficulty changes
    const difficultySelect = document.getElementById('difficulty');
    function getMaxFloors(difficulty) {
        if (difficulty === 'Easy') return 2;
        if (difficulty === 'Normal') return 4;
        if (difficulty === 'Hard') return 6;
        return 0;
    }
    if (difficultySelect) {
        const floorCountElem = document.getElementById('floor-count');
        const updateFloorCount = () => {
            if (floorCountElem) floorCountElem.textContent = getMaxFloors(difficultySelect.value);
        };
        difficultySelect.addEventListener('change', updateFloorCount);
        updateFloorCount();
    }

    if (document.getElementById('game-container')) {
        loadGameState();
    }
});
