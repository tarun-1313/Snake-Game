# Snake-Game
Python Tkinter Edition with Bonus Food, Obstacles &amp; High Score
# 🐍 Snake Game — Python + Tkinter Edition

A modern twist on the classic Snake Game 🕹️ built using **Python** and **Tkinter**, featuring:

- 🧠 Smart collision detection  
- 🍎 Food & 🔴 Bonus Food  
- ⚡ Dynamic obstacle generation  
- 🧱 Walls that appear as your score increases  
- 🎯 Motivational messages during gameplay  
- 🕹️ Pause/Resume, Restart, and Reset Score buttons  
- 🏆 High Score tracking saved to a JSON file

---

## 🚀 Features

- **Bonus Points** for special food 🏅
- **Dynamic Obstacles** like fire, rocks, cactus, and lightning ⚠️
- **Motivational Thoughts** update every 3 seconds to keep you inspired ✨
- **Walls** appear at score milestones (40, 60, 80…) to increase difficulty ⛔
- **High Score Saving** using a JSON file
- **Full GUI Controls** for start, restart, pause, and exit
- **Responsive Controls** via Arrow keys and `Esc` for quit

---
Screenshot
<img width="1064" height="976" alt="Snake" src="https://github.com/user-attachments/assets/eda9fd69-76d6-4fc3-8208-d0825da375a1" />


## 🎮 How to Play

- Use the **arrow keys** to control the snake.
- **Eat food (red circles)** to grow and score points.
- Avoid **obstacles**, **walls**, and your own tail.
- Catch **bonus food** (big red glowing circles) for double points.
- Press `Pause` to take a break, and `Start from Beginning` to reset your high score.

---

## 📦 Requirements

- Python 3.x  
- Tkinter (comes pre-installed with most Python distributions)

> 🛠 No external libraries required — everything is standard Python.

---

## 🖼 UI Overview

- **Scoreboard:** Displays current and high score.
- **Motivational Bar:** Rotates uplifting messages while you play.
- **Game Canvas:** Snake, food, bonus, and dynamic obstacles appear here.
- **Control Panel:**  
  - 🔁 Start Game  
  - 🔄 Restart Game  
  - ⏸ Pause/Resume  
  - 🧹 Start from Beginning (resets high score)  
  - ❌ Exit Game

---

## 💾 High Score

High score is stored in a local file:  
`snake_high_score.json`  
It's persistent across sessions unless reset.

---

## 🔧 File Structure

```plaintext
Snake.py                # Main game logic
snake_high_score.json   # High score data (auto-generated)
README.md               # This file
