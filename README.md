# Connect 4 AI Game

A web-based Connect 4 game featuring an AI opponent powered by a minimax algorithm with alpha-beta pruning.

## Features

- Modern, responsive UI
- AI opponent with configurable difficulty
- Win detection
- Draw detection
- Real-time game state updates

## Prerequisites

- Python 3.8 or higher
- Flask and other Python dependencies

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## How to Play

1. The game starts with you (red) making the first move
2. Click on any column to drop your piece
3. The AI (yellow) will respond with its move
4. The game continues until someone wins or the board is full

## Technical Details

The AI uses a minimax algorithm with alpha-beta pruning to determine the best move. The search depth can be adjusted in the `app.py` file.

## License

MIT License 