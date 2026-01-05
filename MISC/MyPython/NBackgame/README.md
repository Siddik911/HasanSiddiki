# 🧠 Dual N-Back Game

A cognitive training game designed to improve working memory by simultaneously tracking both **position** and **visual stimuli** (strings).

## 🎮 What is Dual N-Back?

Dual N-Back is a scientifically-backed cognitive training exercise. The game presents:
1. **Position**: A highlighted cell on a grid
2. **String**: A sequence of characters displayed on screen

Your task is to remember if the **current** position or string matches what was shown **N steps ago**.

### Example (2-Back):
If N=2, you need to remember if the current stimulus matches what was shown 2 rounds ago.

```
Round 1: Position(1,1), String "AB"
Round 2: Position(2,1), String "XY"
Round 3: Position(1,1), String "CD"  ← Position matches Round 1!
Round 4: Position(3,2), String "XY"  ← String matches Round 2!
```

## 🚀 Quick Start

### Windows (Easiest Method)
Simply double-click `run_game.bat` - it will:
1. ✅ Check if Python is installed
2. ✅ Install Python automatically if needed
3. ✅ Launch the game

### Manual Launch
If you already have Python installed:
```bash
python dual_nback.py
```

## ⚙️ Game Settings

Before each game, you can customize:

| Setting | Description | Range |
|---------|-------------|-------|
| **N-Back Level** | How many steps back to remember | 1-9 |
| **Grid Rows** | Number of rows in the position grid | 2-6 |
| **Grid Columns** | Number of columns in the position grid | 2-6 |
| **Round Duration** | Time each stimulus is shown | 1-10 seconds |
| **Total Rounds** | Number of stimuli in a game | 10-100 |
| **String Length** | Characters per string | 1-6 |
| **String Type** | Letters, Numbers, or Combination | - |
| **Letter Case** | Capital, Lowercase, or Combination | - |

### Quick Start Presets
- **Easy (2-Back)**: 20 rounds - Good for beginners
- **Medium (3-Back)**: 25 rounds - Standard difficulty
- **Hard (4-Back)**: 30 rounds - Challenge mode

## 🎯 Controls

| Key | Action |
|-----|--------|
| `A` | Report **Position** match |
| `L` | Report **String** match |
| `Space` | Pause / Resume game |
| `Escape` | End game early |

You can also click the on-screen buttons.

## 📊 Scoring System

### Points
- **+10 points** for each correct identification (hit)
- **-5 points** for each false alarm (incorrect press)
- **0 points** for missed matches

### Accuracy
- **Position Accuracy**: `(Position Hits / Total Position Responses) × 100%`
- **String Accuracy**: `(String Hits / Total String Responses) × 100%`

### Statistics Tracked
- High scores per N-level
- Game history with dates
- Position and String accuracy per game

## 🎨 Features

### Visual Design
- 🌿 **Green Theme**: Easy on the eyes for extended sessions
- 📊 **Live Stats**: Real-time hit/miss counters
- 🎯 **Visual Feedback**: Buttons change color for correct/incorrect

### Game Features
- 📈 **Progressive Difficulty**: Choose your N-level
- 🎲 **Randomization**: Fair distribution of matches
- 💾 **Statistics Tracking**: All games saved to JSON
- 🏆 **High Score System**: Per-level high scores
- ⏸️ **Pause Support**: Take breaks mid-game
- ⌨️ **Keyboard Shortcuts**: Fast responses

### Accessibility
- 🖱️ Mouse + Keyboard support
- 📐 Resizable window
- 🔤 Configurable string types

## 🧪 Cognitive Benefits

Research suggests regular N-Back training may improve:
- Working memory capacity
- Fluid intelligence
- Attention control
- Processing speed

**Recommended**: 15-20 minutes per session, 3-5 times per week.

## 📁 File Structure

```
NBackgame/
├── dual_nback.py      # Main game application
├── run_game.bat       # Windows auto-installer/launcher
├── README.md          # This documentation
└── game_stats.json    # Game statistics (auto-created)
```

## 🔧 Requirements

- **Python 3.6+** (with tkinter - included by default on Windows)
- **Operating System**: Windows 7/8/10/11 (batch script), or any OS with Python

### Dependencies
The game uses only Python standard library modules:
- `tkinter` - GUI framework (included with Python)
- `json` - Statistics storage
- `random` - Randomization
- `string` - Character generation
- `datetime` - Timestamps

**No external packages needed!**

## 🐛 Troubleshooting

### "Python not found"
- Run `run_game.bat` which will install Python automatically
- Or download Python from [python.org](https://www.python.org/downloads/)
- ⚠️ During installation, check **"Add Python to PATH"**

### "tkinter not found"
- Reinstall Python and ensure Tk/Tcl is included
- On Windows, this is included by default

### Game runs slowly
- Reduce grid size
- Close other applications
- Try increasing round duration

### Statistics not saving
- Ensure write permissions in the game folder
- Check if `game_stats.json` can be created

## 📄 License

This game is provided free for personal and educational use.

---

**Enjoy training your brain! 🧠✨**
