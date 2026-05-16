# CITS3403 Project - Dungeon Dealer
## Purpose

**Dungeon Dealer** is a top-down, turn-based dungeon crawler web game where players progress through procedurally generated floors, battle enemies, collect loot, and strategically build powerful card decks. The objective is to complete a set number of dungeon floors while surviving encounters, managing resources, and optimising deck strategy.

The game combines tactical combat, resource management, and card-based progression. Each run is different, with players adapting to enemies, locked pathways, and available loot while making decisions that influence long-term progression and competitive standing.

Players can also interact with a wider community through trading systems, leaderboards, and profile-based statistics tracking.

---

## Key Features
- **Turn-Based Top-Down Dungeon Gameplay**: Navigate dungeon floors, fight enemies, use keys, and collect gold
- **Procedural Floor Progression**: Each run features different layouts, enemies, and item placements
- **Card-Based Ability System**: Players use a shuffled deck each turn to gain abilities, buffs, and combat advantages
- **Deck Customisation**: Add, remove, and manage cards to build personalised strategies
- **Card Trading System**: Mark cards as tradable, search other users’ inventories, and trade directly with players
- **Multi-Card Trading Offers**: Send and receive structured trade offers involving multiple cards on both sides
- **In-Game Economy**:
  - Earn gold during runs
  - Spend gold in shops on daily cards
  - Purchase card packs using difficulty-based tokens earned from completed runs
- **Difficulty-Based Rewards**: Higher difficulty runs reward better tokens and progression incentives
- **Player Accounts**: Secure authentication with persistent profiles and game data storage
- **Leaderboard System**: Compare performance, wins, and progression against other players globally
- **Player Profiles & Analytics**: View detailed statistics, including performance graphs and gameplay history
- **Trade Visibility Controls**: Users can mark inventory cards as tradable or private
- **Social Interaction Features**: View other users’ profiles, inventories, and trade activity
- **Notifications System**: Receive alerts for incoming trade offers and responses

---

## Design and Use

The design of **Dungeon Dealer** focuses on strategic depth, replayability, and social interaction within a competitive dungeon-crawling environment. The gameplay loop is built around repeated dungeon runs where players improve their decks, refine strategies, and unlock stronger cards over time.

Each dungeon run requires careful decision-making as players balance fighting enemies, resource collection, and navigation through locked paths. The card system introduces randomness and strategy through a shuffled hand each turn, encouraging adaptive playstyles.

Outside of gameplay, the system emphasises long-term engagement through persistent progression systems. Players can customise their decks, trade with others, and optimise builds based on available cards and strategies, with higher rarity cards being an objective to work towards.

The social layer of the game allows users to compare performance via leaderboards, inspect other players’ profiles, and engage in a player-driven trading economy. Analytics and visualisations help users track improvement over time and the trade system and inventory management add depth to the progression.

---

## Group Members

| **UWA ID** | **Name** | **GitHub Username** |
| ---------- | -------- | ------------------- |
| 23413047 | Ben Ward  | Wardy3iccc |
| 24224402 | Jacob Pranoto | kaojb-bass |
| 24278297 | Campbell Henderson | phyric1 |
| 24381263 | Harry Zhang | zjhzz |

---

## How to Run the Website

1. **Clone the repository**

   ```bash
   git clone https://github.com/phyric1/CITS3403_Project.git
   ```

2. **Navigate into the project directory**

   ```bash
   cd CITS3403_Project
   ```

3. **Create and activate a virtual environment**

   If on Windows:

   ```bash
   wsl
   python3 -m venv venv
   source venv/bin/activate
   ```

   If on Linux/macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set the SECRET_KEY environment variable**

   ```bash
   export SECRET_KEY=your_actual_secret_key
   ```

   **NOTE:** Replace `"your_actual_secret_key"` with a secure secret key. Do not use the placeholder value in production.

6. **Setup the database**

   ```bash
   flask db upgrade
   ```

7. **Seed Needed data**

    Add needed card data:
  
    ```bash
    flask seed-cards
    ```

7. **Run the Flask server**

   ```bash
   flask run
   ```

8. **Open the application in your browser**

   Visit:

   ```text
   http://127.0.0.1:5000
   ```

---

## How to Run Tests

Follow the above steps to run the website. Once it is up, open a new terminal window in the project directory with the virtual environment activated, and then run:

```bash
python3 -m pytest -v
```
