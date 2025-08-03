import tkinter as tk
import random
import json
import os

# Window dimensions
GAME_WIDTH = 800
GAME_HEIGHT = 600
SPEED = 100       # Smaller is faster
SPACE_SIZE = 20
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BONUS_FOOD_COLOR = "#FF0000"  # Big red circle
BG_COLOR = "#1A1A1A"
HIGH_SCORE_FILE = "snake_high_score.json"

# Motivational thoughts for the game
MOTIVATIONAL_THOUGHTS = [
    "🎯 Focus on your goal!",
    "💪 You've got this!",
    "🚀 Keep pushing forward!",
    "⭐ Every point counts!",
    "🔥 You're on fire!",
    "🎮 Stay sharp and focused!",
    "🏆 You're a champion!",
    "⚡ Speed and precision!",
    "🌟 Believe in yourself!",
    "🎪 You're doing amazing!"
]


def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except Exception:
        pass
    return 0


def save_high_score(high_score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump({'high_score': high_score}, f)
    except Exception:
        pass


def reset_high_score_and_start():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        os.remove(HIGH_SCORE_FILE)
    high_score = 0
    start_game()
    label.config(text="Score: 0 | High Score: 0")


class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        for _ in range(BODY_PARTS):
            self.coordinates.append([0, 0])


class Food:
    def __init__(self, canvas, snake, obstacles):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake.coordinates and [x, y] not in obstacles:
                break
        self.coordinates = [x, y]
        self.food = canvas.create_oval(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food"
        )


class BonusFood:
    def __init__(self, canvas, snake, obstacles):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake.coordinates and [x, y] not in obstacles:
                break
        self.coordinates = [x, y]
        # Big red circle (2x size)
        self.bonus_food = canvas.create_oval(
            x - 10, y - 10, x + SPACE_SIZE + 10, y + SPACE_SIZE + 10,
            fill=BONUS_FOOD_COLOR, outline="#FFFFFF", width=3, tag="bonus_food"
        )


class Wall:
    """A wall made of adjacent grid blocks. We separate coordinate generation
    from drawing so we can validate before rendering (prevents ghost walls)."""

    def __init__(self, orientation, pos, length=8):
        self.orientation = orientation  # 'h' or 'v'
        self.pos = pos  # (x, y)
        self.length = length
        self.coordinates = []
        for i in range(length):
            if orientation == 'h':
                x = pos[0] + i * SPACE_SIZE
                y = pos[1]
            else:
                x = pos[0]
                y = pos[1] + i * SPACE_SIZE
            self.coordinates.append([x, y])

    def draw(self, canvas):
        color = '#888888'
        for x, y in self.coordinates:
            canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                                    fill=color, outline='#222', tag='wall')


def _coords_overlap_with_game(coords, snake, food, bonus_food, obstacles, walls):
    # Check overlap with snake, food, bonus, existing walls (coords lists) and obstacles
    for c in coords:
        if c in snake.coordinates or c == food.coordinates or c in obstacles:
            return True
        if bonus_food is not None and c == bonus_food.coordinates:
            return True
        for w in walls:
            if c in w:
                return True
    return False


def next_turn(snake, food, obstacles, walls, wall_score_thresholds):
    global game_running, paused, score, high_score, bonus_food

    if not game_running or paused:
        return

    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0, [x, y])
    square = canvas.create_rectangle(
        x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR
    )
    snake.squares.insert(0, square)

    # Check for food collision
    if x == food.coordinates[0] and y == food.coordinates[1]:
        score += 1
        if score > high_score:
            high_score = score
            save_high_score(high_score)
        label.config(text=f"Score: {score} | High Score: {high_score}")
        canvas.delete("food")
        # respawn food
        food.__init__(canvas, snake, obstacles)

        # Create bonus food every 10 points (fixed operator precedence bug)
        if (score % 10 == 0) and ((bonus_food is None)):
            bonus_food = BonusFood(canvas, snake, obstacles)

    # Check for bonus food collision
    elif (bonus_food is not None and
          x == bonus_food.coordinates[0] and y == bonus_food.coordinates[1]):
        score += 2
        if score > high_score:
            high_score = score
            save_high_score(high_score)
        label.config(text=f"Score: {score} | High Score: {high_score}")
        canvas.delete("bonus_food")
        bonus_food = None
    else:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    # Add new wall if score threshold reached
    if wall_score_thresholds and score >= wall_score_thresholds[0]:
        # Try to add a wall that doesn't overlap snake, food, obstacles, or other walls
        placed = False
        for _ in range(30):
            orientation = random.choice(['h', 'v'])
            if orientation == 'h':
                wx = random.randint(2, (GAME_WIDTH // SPACE_SIZE) - 10) * SPACE_SIZE
                wy = random.randint(2, (GAME_HEIGHT // SPACE_SIZE) - 3) * SPACE_SIZE
            else:
                wx = random.randint(2, (GAME_WIDTH // SPACE_SIZE) - 3) * SPACE_SIZE
                wy = random.randint(2, (GAME_HEIGHT // SPACE_SIZE) - 10) * SPACE_SIZE

            candidate = Wall(orientation, (wx, wy))
            if not _coords_overlap_with_game(candidate.coordinates, snake, food, bonus_food, obstacles, walls):
                candidate.draw(canvas)
                walls.append(candidate.coordinates)
                obstacles.extend(candidate.coordinates)
                placed = True
                break
        # Only pop threshold if we managed to place a wall
        if placed:
            wall_score_thresholds.pop(0)

    # Game over conditions
    if (
        x < 0 or x >= GAME_WIDTH
        or y < 0 or y >= GAME_HEIGHT
        or [x, y] in snake.coordinates[1:]
        or [x, y] in obstacles
    ):
        game_over()
    else:
        window.after(SPEED, next_turn, snake, food, obstacles, walls, wall_score_thresholds)


def change_direction(new_direction):
    global direction
    if not game_running:
        return
    if new_direction == "left" and direction != "right":
        direction = new_direction
    elif new_direction == "right" and direction != "left":
        direction = new_direction
    elif new_direction == "up" and direction != "down":
        direction = new_direction
    elif new_direction == "down" and direction != "up":
        direction = new_direction


def update_thought():
    """Periodic motivational text updater."""
    global thought_index, thought_timer_id, game_running
    if not game_running:
        return
    thought_index = (thought_index + 1) % len(MOTIVATIONAL_THOUGHTS)
    thought_label.config(text=MOTIVATIONAL_THOUGHTS[thought_index])
    thought_timer_id = window.after(3000, update_thought)


def pause_game():
    global paused
    if not game_running or paused:
        return
    paused = True
    pause_button.config(text="Resume", command=resume_game)
    if 'thought_timer_id' in globals() and thought_timer_id:
        window.after_cancel(thought_timer_id)


def resume_game():
    global paused, thought_timer_id
    if not game_running or not paused:
        return
    paused = False
    pause_button.config(text="Pause", command=pause_game)
    thought_timer_id = window.after(3000, update_thought)
    if 'snake' in globals() and 'food' in globals():
        next_turn(snake, food, obstacles, walls, wall_score_thresholds)


def game_over():
    global game_running, thought_timer_id
    game_running = False
    if 'thought_timer_id' in globals() and thought_timer_id:
        window.after_cancel(thought_timer_id)

    # Check if this is a new high score
    is_new_high_score = score >= high_score

    canvas.create_text(
        GAME_WIDTH / 2, GAME_HEIGHT / 2 - 60, font=("Arial", 32, "bold"), fill="#FFFFFF",
        text="GAME OVER"
    )

    if is_new_high_score:
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 - 20, font=("Arial", 28, "bold"), fill="#FFD700",
            text="🎉 NEW HIGH SCORE! 🎉"
        )
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20, font=("Arial", 24), fill="#FFD700",
            text="🏆 Congratulations! 🏆"
        )
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 + 60, font=("Arial", 20), fill="#FF8888",
            text=f"Final Score: {score} (New Record!)"
        )
    else:
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20, font=("Arial", 20), fill="#FF8888",
            text=f"Final Score: {score}"
        )

    restart_button.pack(side="left", padx=5)

    # Stop obstacle timer
    if 'obstacle_timer_id' in globals() and obstacle_timer_id:
        window.after_cancel(obstacle_timer_id)


def start_game():
    global score, direction, snake, food, bonus_food, obstacles, walls, wall_score_thresholds, game_running, thought_index, thought_timer_id, paused

    start_button.pack_forget()
    restart_button.pack_forget()

    score = 0
    direction = "right"
    game_running = True
    paused = False
    thought_index = 0
    label.config(text=f"Score: 0 | High Score: {high_score}")
    thought_label.config(text=MOTIVATIONAL_THOUGHTS[0])
    if 'thought_timer_id' in globals() and thought_timer_id:
        window.after_cancel(thought_timer_id)
    thought_timer_id = window.after(3000, update_thought)
    canvas.delete(tk.ALL)

    # One random obstacle at start
    obstacles = []
    for _ in range(1):
        x = random.randint(2, (GAME_WIDTH // SPACE_SIZE) - 3) * SPACE_SIZE
        y = random.randint(2, (GAME_HEIGHT // SPACE_SIZE) - 3) * SPACE_SIZE
        emoji = random.choice(["🪨", "🌵", "🔥", "💎", "🌲", "⚡", "💀", "🚫"])
        canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                           fill="#333333", outline="#666666", width=2, tag="obstacle")
        canvas.create_text(x + SPACE_SIZE // 2, y + SPACE_SIZE // 2,
                           text=emoji, font=("Arial", 14, "bold"), fill="#FFFFFF", tag="obstacle")
        obstacles.append([x, y])

    # Start dynamic obstacle spawning
    global obstacle_timer_id
    if 'obstacle_timer_id' in globals() and obstacle_timer_id:
        window.after_cancel(obstacle_timer_id)
    obstacle_timer_id = window.after(10000, spawn_obstacle)

    snake = Snake()
    food = Food(canvas, snake, obstacles)
    bonus_food = None

    walls = []
    wall_score_thresholds = [40, 60, 80, 100, 120]

    for x, y in snake.coordinates:
        square = canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR
        )
        snake.squares.append(square)

    next_turn(snake, food, obstacles, walls, wall_score_thresholds)


def spawn_obstacle():
    global obstacles, obstacle_timer_id, snake, food, bonus_food
    if not game_running:
        return
    obstacle_emojis = ["🪨", "🌵", "🔥", "💎", "🌲", "⚡", "💀", "🚫"]
    for _ in range(20):
        x = random.randint(2, (GAME_WIDTH // SPACE_SIZE) - 3) * SPACE_SIZE
        y = random.randint(2, (GAME_HEIGHT // SPACE_SIZE) - 3) * SPACE_SIZE
        if (
            [x, y] not in snake.coordinates and
            [x, y] != food.coordinates and
            (bonus_food is None or [x, y] != bonus_food.coordinates) and
            [x, y] not in obstacles
        ):
            canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                               fill="#333333", outline="#666666", width=2, tag="obstacle")
            emoji = random.choice(obstacle_emojis)
            canvas.create_text(x + SPACE_SIZE // 2, y + SPACE_SIZE // 2,
                               text=emoji, font=("Arial", 14, "bold"), fill="#FFFFFF", tag="obstacle")
            obstacles.append([x, y])
            break
    # Schedule next obstacle spawn
    obstacle_timer_id = window.after(10000, spawn_obstacle)


# Create the main window
window = tk.Tk()
window.title("Snake Game")
window.resizable(False, False)

# Center the window on screen
window_width = GAME_WIDTH + 50  # Extra space for buttons
window_height = GAME_HEIGHT + 150  # Extra space for score and buttons
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Initialize game variables
score = 0
direction = "right"
game_running = False
high_score = load_high_score()
thought_index = 0
paused = False
bonus_food = None

# Create UI elements
label = tk.Label(window, text=f"Score: 0 | High Score: {high_score}", font=("Arial", 24), bg=BG_COLOR, fg="#FFF")
label.pack(fill="x")

thought_label = tk.Label(window, text=MOTIVATIONAL_THOUGHTS[0], font=("Arial", 16), bg=BG_COLOR, fg="#FFD700")
thought_label.pack(fill="x")

canvas = tk.Canvas(window, bg=BG_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

# Create button frame first
button_frame = tk.Frame(window, bg=BG_COLOR)
button_frame.pack(side="bottom", pady=10)

# Create buttons
start_button = tk.Button(button_frame, text="Start Game", font=("Arial", 14), command=start_game, bg="#00AA00", fg="white", width=10)
start_button.pack(side="left", padx=15)

restart_button = tk.Button(button_frame, text="Restart Game", font=("Arial", 14), command=start_game, bg="#0088FF", fg="white", width=10)
restart_button.pack_forget()

exit_button = tk.Button(button_frame, text="Exit Game", font=("Arial", 14), command=window.quit, bg="#FF4444", fg="white", width=10)
exit_button.pack(side="left", padx=15)

pause_button = tk.Button(button_frame, text="Pause", font=("Arial", 14), command=pause_game, bg="#FFA500", fg="white", width=13)
pause_button.pack(side="left", padx=15)

delete_button = tk.Button(button_frame, text="Start from Beginning", font=("Arial", 14), command=reset_high_score_and_start, bg="#AA00AA", fg="white", width=20)
delete_button.pack(side="left", padx=15)

# Bind keyboard events
window.bind("<Left>", lambda event: change_direction("left"))
window.bind("<Right>", lambda event: change_direction("right"))
window.bind("<Up>", lambda event: change_direction("up"))
window.bind("<Down>", lambda event: change_direction("down"))
window.bind("<Escape>", lambda event: window.quit())  # Exit game with Escape key

window.mainloop()
