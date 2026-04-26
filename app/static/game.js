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
            updateGameState();
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
                } else if (newGrid[i][j] === -1) {
                    tile.classList.add('shadow', 'bg-dark');
                }
                gridContainer.appendChild(tile);
            }
        }
    }

    function updateGameState() {
          const turnCount = document.getElementById('turn-value');
        turnCount.textContent = parseInt(turnCount.textContent) + 1;
    }