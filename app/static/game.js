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

const cards = document.querySelectorAll('.card-wrapper');
cards[0].addEventListener("click", function() {
    move('None');
    console.log('slot1');
})
cards[1].addEventListener("click", function() {
    move('None');
    console.log('slot2');
})
cards[2].addEventListener("click", function() {
    move('None');
    console.log('slot3');
})

    function move(direction) {
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ direction: direction }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Update the grid display with new player position
            updateGridDisplay(data.grid, data.filter);
            updateGameState(data.turn, data.hp, data.keys, data.gold, data.floor);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function updateCards(){
        const cards = document.querySelectorAll('.inventory-card-wrapper');
        //find out how to pass card data and display it
    }

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

                if (filter[i][j] === 1) {
                    tile.classList.add('bright');
                } else {
                    tile.classList.remove('bright');
                }

                gridContainer.appendChild(tile);
            }
        }

    }

    function updateGameState(turn, hp, keys, gold, floor) {
        const turnCount = document.getElementById('turn-value');
        turnCount.textContent = turn;

        const health = document.getElementById('health-value');
        health.textContent = hp;

        const keyCount = document.getElementById('keys-value');
        keyCount.textContent = keys;

        const goldCount = document.getElementById('treasure-value');
        goldCount.textContent = gold;

        const levelCount = document.getElementById('floor-value');
        levelCount.textContent = floor;
    }
