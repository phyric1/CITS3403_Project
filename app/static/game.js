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

const cards = document.querySelectorAll('.inventory-card-wrapper');
cards[0].addEventListener("click", function() {
    move('None');
})
cards[1].addEventListener("click", function() {
    move('None');
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
            updateGridDisplay(data.grid);
            updateGameState(data.turn, data.keys);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function updateGridDisplay(newGrid) {
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
                }
                else if (newGrid[i][j] === 5) {
                    tile.classList.add('key', 'bg-white');
                }
                gridContainer.appendChild(tile);
            }
        }
    }

    function updateGameState(turn, keys) {
        const turnCount = document.getElementById('turn-value');
        turnCount.textContent = turn;

        const keyCount = document.getElementById('keys-value');
        keyCount.textContent = keys;
    }