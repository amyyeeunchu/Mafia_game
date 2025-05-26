import random
import pygame
import sys
from transformers import pipeline

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mafia Game")
clock = pygame.time.Clock()

# List of image file paths 
avatar_paths = [
    r'c:\Users\juicy\OneDrive\Desktop\avatar1.png',
    r'c:\Users\juicy\OneDrive\Desktop\avatar2.png',
    r'c:\Users\juicy\OneDrive\Desktop\avatar3.png',
    r'c:\Users\juicy\OneDrive\Desktop\avatar4.png',
    r'c:\Users\juicy\OneDrive\Desktop\avatar5.png',
]

# Load and scale avatars
avatars = []
avatar_size = (100, 100)
for path in avatar_paths:
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, avatar_size)
    avatars.append(img)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)

# Define roles and players
roles = ['Mafia', 'Townspeople', 'Townspeople', 'Doctor', 'Detective']
random.shuffle(roles)

players = {
    'Alex': roles[0],
    'Blake': roles[1],
    'Casey': roles[2],
    'Dana': roles[3],
    'Elliot': roles[4]
}

player_names = list(players.keys())

# Map players to their avatar images
player_avatars = {
    'Alex': avatars[0],
    'Blake': avatars[1],
    'Casey': avatars[2],
    'Dana': avatars[3],
    'Elliot': avatars[4]
}

player_status = [True] * len(player_names)  # Track if a player is alive

# Debug: print roles
print("DEBUG - Player roles:")
for name, role in players.items():
    print(f"{name}: {role}")

# Game state variables
discussion_log = []
question_history = {player: [] for player in players}
user_input = ''
active_input = False
current_player_index = 0
round_counter = 1

# Emotion classifier
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")


# Dynamic placeholder values
placeholder_values = {
    'place': ["home", "the clinic", "the park", "my apartment", "the bakery", "the square"],
    'activity': ["reading", "watching TV", "resting", "working", "playing games"],
    'sound': ["footsteps", "a door creaking", "a scream", "muffled voices"]
}

# Flexible response templates
response_templates = {
    'Mafia': {
        'alibi': ["I was at {place}.", "Just {activity} all night."],
        'observation': ["I didn’t see anyone, it was dark.", "I heard {sound}, but couldn’t tell where it came from."],
        'accusation': ["Why are you blaming me?", "This is ridiculous!"],
        'general': ["I don’t know what to say.", "I can’t help you with that."]
    },
    'Townspeople': {
        'alibi': ["I was home with my dog.", "Just {activity}, nothing special."],
        'observation': ["I saw someone near {place}.", "I heard {sound} late at night."],
        'accusation': ["I’m innocent!", "Why would I do that?"],
        'general': ["Sorry, I don’t know anything.", "That’s confusing to me too."]
    },
    'Doctor': {
        'alibi': ["I was at the clinic.", "I was making rounds at the hospital."],
        'observation': ["I didn’t see much. It was a quiet night.", "I heard {sound} outside."],
        'accusation': ["I'm a doctor! Why would I be involved in this?", "Stop accusing me!"],
        'general': ["I don't have all the details.", "I can't say much."]
    },
    'Detective': {
        'alibi': ["I was investigating near {place}.", "I was checking out some leads."],
        'observation': ["I saw someone near {place}.", "I observed people coming and going."],
        'accusation': ["I have more information than you think.", "Don’t question me!"],
        'general': ["I don’t have any new leads.", "I’ll keep an eye on things."]
    }
}

def analyze_emotion(text):
    result = emotion_classifier(text)
    if result and isinstance(result, list):
        return result[0]['label']
    return "neutral"


def display_text(text, x, y, color=BLACK, max_width=760, line_height=40):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '

    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines):
        text_surface = font.render(line.strip(), True, color)
        screen.blit(text_surface, (x, y + i * line_height))


def categorize_question(question):
    q = question.lower()
    if any(word in q for word in ['where', 'location', 'go', 'doing', 'last night', 'yesterday', 'were you']):
        return 'alibi'
    elif any(word in q for word in ['see', 'hear', 'notice', 'watch', 'who']):
        return 'observation'
    elif any(word in q for word in ['why', 'lying', 'suspicious', 'truth', 'hid', 'accus']):
        return 'accusation'
    else:
        return 'general'

def fill_placeholders(text):
    for key, options in placeholder_values.items():
        if f"{{{key}}}" in text:
            text = text.replace(f"{{{key}}}", random.choice(options))
    return text

def generate_dynamic_response(player, question, emotion='neutral'):
    role = players[player]
    category = categorize_question(question)
    response_pool = response_templates[role].get(category, response_templates[role]['general'])

    if emotion == 'anger':
        response_pool += ["Why are you so aggressive?", "Calm down, I’m just trying to help."]
    elif emotion == 'joy':
        response_pool += ["You seem cheerful about this.", "Glad to see some positivity."]
    elif emotion == 'sadness':
        response_pool += ["You seem upset. I'm sorry.", "It's a hard time for all of us."]

    part1 = random.choice(["Honestly,", "Well,", "To be honest,", ""])
    part2 = fill_placeholders(random.choice(response_pool))
    part3 = random.choice(["That's all I can say.", "Hope that helps.", "", "I’m not sure what else to add."])

    response = " ".join(part for part in [part1, part2, part3] if part).strip()
    discussion_log.append(f"{response}")
    return response


def show_log():
    scroll = 0
    running = True

    VISIBLE_HEIGHT = 400
    ENTRY_SPACING = 10
    LINE_HEIGHT = 30
    MAX_WIDTH = 740

    SCROLLBAR_X = 780
    SCROLLBAR_Y = 60
    SCROLLBAR_WIDTH = 10
    SCROLLBAR_HEIGHT = VISIBLE_HEIGHT

    while running:
        screen.fill(WHITE)
        display_text("Discussion Log", 20, 20, BLUE)


        y_offset = 60
        lines_displayed = 0
        wrapped_entries = []

        # Pre-wrap all log entries
        for entry in discussion_log:
            words = entry.split(' ')
            line = ''
            lines = []
            for word in words:
                test_line = line + word + ' '
                if font.size(test_line)[0] <= MAX_WIDTH:
                    line = test_line
                else:
                    lines.append(line)
                    line = word + ' '
            if line:
                lines.append(line)

            wrapped_entries.append(lines)

        # Flattened view for scrolling
        flat_lines = []
        for entry in wrapped_entries:
            for line in entry:
                flat_lines.append(line.strip())

        total_lines = len(flat_lines)
        max_scroll = max(0, total_lines - VISIBLE_HEIGHT // LINE_HEIGHT)
        visible_lines = flat_lines[scroll:scroll + VISIBLE_HEIGHT // LINE_HEIGHT]

        for line in visible_lines:
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (20, y_offset))
            y_offset += LINE_HEIGHT

        # Instructions and scrollbar
        display_text("Press ESC to return", 20, 550, RED)

        pygame.draw.rect(screen, GRAY, (SCROLLBAR_X, SCROLLBAR_Y, SCROLLBAR_WIDTH, SCROLLBAR_HEIGHT))
        if total_lines > VISIBLE_HEIGHT // LINE_HEIGHT:
            thumb_height = max(SCROLLBAR_HEIGHT * (VISIBLE_HEIGHT // LINE_HEIGHT) // total_lines, 20)
            thumb_pos = SCROLLBAR_Y + (SCROLLBAR_HEIGHT - thumb_height) * scroll // max_scroll
            pygame.draw.rect(screen, (100, 100, 100), (SCROLLBAR_X, thumb_pos, SCROLLBAR_WIDTH, thumb_height))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP and scroll > 0:
                    scroll -= 1
                elif event.key == pygame.K_DOWN and scroll < max_scroll:
                    scroll += 1


def wait_for_continue_button():
    button_rect = pygame.Rect(600, 500, 160, 50)
    while True:
        pygame.draw.rect(screen, BLUE, button_rect)
        display_text("Continue", button_rect.x + 20, button_rect.y + 10, WHITE)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if active_input:
                    if event.key == pygame.K_RETURN:
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return


def accusation_phase():
    accused = None
    buttons = []
    button_y = 150

    # Filter out dead players
    alive_players = [name for name in player_names if player_status[player_names.index(name)]]

    for name in alive_players:
        btn_rect = pygame.Rect(100, button_y, 600, 40)
        buttons.append((btn_rect, name))
        button_y += 60

    log_button_rect = pygame.Rect(20, 500, 160, 50)  # Log button rectangle
    while accused is None:
        screen.fill(WHITE)
        display_text("Accusation Phase", 20, 20, RED)
        display_text("Click on a player to accuse them.", 20, 70, BLACK)
        pygame.draw.rect(screen, BLUE, log_button_rect)  # Draw the log button
        display_text("View Log", log_button_rect.x + 20, log_button_rect.y + 10, WHITE)

        # Draw the accusation buttons for each player
        for rect, name in buttons:
            pygame.draw.rect(screen, GRAY, rect)
            display_text(name, rect.x + 10, rect.y + 5)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the log button is clicked
                if log_button_rect.collidepoint(event.pos):
                    show_log()
                # Check if any player accusation button is clicked
                for rect, name in buttons:
                    if rect.collidepoint(event.pos):
                        accused = name

    # Check if the accused player is the Mafia
    if players[accused] == 'Mafia':
        # The player wins if they correctly accused the Mafia
        discussion_log.append(f"{accused} was accused and revealed to be: Mafia. You win!")
        screen.fill(WHITE)
        display_text(f"Congratulations! {accused} was the Mafia. You win!", 20, 150, BLUE)
        pygame.display.update()
        pygame.time.delay(3000)  # Wait a few seconds before exiting
        pygame.quit()
        sys.exit()

    # If the accused is not Mafia, they are killed
    player_status[player_names.index(accused)] = False
    discussion_log.append(f"{accused} was accused wrongly and has been killed.")
    
    screen.fill(WHITE)
    display_text(f"{accused} was wrongly accused!", 20, 150, RED)
    display_text(f"{accused} has been killed.", 20, 200, RED)
    pygame.display.update()
    pygame.time.delay(2000)  # Wait for 2 seconds to show the death message

    # Proceed with the next round or night phase
    wait_for_continue_button()



def mafia_kills():
    alive_civilians = [i for i in range(len(player_names)) if player_names[i] != "Mafia" and player_status[i]]
    if alive_civilians:
        civilian_to_kill = random.choice(alive_civilians)  # Mafia kills a random civilian
        player_status[civilian_to_kill] = False
        print(f"{player_names[civilian_to_kill]} has been killed by the mafia.")
        return civilian_to_kill
    return None


def check_end_game():
    # Check if only 2 players are left
    alive_players = [i for i, status in enumerate(player_status) if status]
    if len(alive_players) == 1:
        if "You" in [player_names[i] for i in alive_players]:
            print("You lost! The mafia defeated you.")
        else:
            print("You won! You survived.")
        pygame.time.delay(2000)
        main_menu()
        return



def night_phase():
    screen.fill(WHITE)
    display_text("Night phase begins...", 20, 100, BLACK)
    pygame.display.update()
    pygame.time.delay(1000)  # Wait for 1 second to show the night phase message

    # Mafia kills one civilian
    killed_player = mafia_kills()

    # Display who was killed
    if killed_player is not None:
        screen.fill(WHITE)
        display_text(f"{player_names[killed_player]} has been killed by the mafia.", 20, 100, RED)
        pygame.display.update()
        pygame.time.delay(2000)  # Wait for 2 seconds to show the death message

    # Show alive players
    alive_players = [player_names[i] for i in range(len(player_names)) if player_status[i]]
    screen.fill(WHITE)
    display_text("Alive players:", 20, 200, BLACK)
    for i, player in enumerate(alive_players):
        display_text(f"{i + 1}. {player}", 20, 240 + i * 30, BLACK)

    pygame.display.update()
    pygame.time.delay(2000)  # Wait for 2 seconds to show the alive players

    check_end_game()


def play_game():
    global user_input, active_input, round_counter

    input_box = pygame.Rect(20, 140, 760, 40)

    while True:
        # Get all alive players
        alive_player_indices = [i for i, alive in enumerate(player_status) if alive]

        for current_player_index in alive_player_indices:
            current_player = player_names[current_player_index]
            answered = False  # Flag to ensure player answers before moving on

            while not answered:
                screen.fill(WHITE)
                
                display_text(f"Round {round_counter}", 20, 20, BLUE)
                display_text(f"Investigate {current_player}", 20, 60, BLACK)

                if current_player in player_avatars:
                    screen.blit(player_avatars[current_player], (600, 20))  # Position top-right

                pygame.draw.rect(screen, BLUE if active_input else BLACK, input_box, 2)
                display_text(user_input, input_box.x + 10, input_box.y + 5, BLACK)

                # Log button
                log_button_rect = pygame.Rect(20, 500, 160, 50)
                pygame.draw.rect(screen, BLUE, log_button_rect)
                display_text("View Log", log_button_rect.x + 20, log_button_rect.y + 10, WHITE)

                pygame.display.update()
                events = pygame.event.get()

                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        active_input = input_box.collidepoint(event.pos)
                        if log_button_rect.collidepoint(event.pos):
                            show_log()

                    elif event.type == pygame.KEYDOWN:
                        if active_input:
                            if event.key == pygame.K_RETURN and user_input.strip():
                                question = user_input.strip()
                                emotion = analyze_emotion(question)
                                discussion_log.append(f"{current_player}: {question}")
                                response = generate_dynamic_response(current_player, question, emotion)

                                screen.fill(WHITE)
                                display_text(f"Q: {question}", 20, 100, BLACK)
                                display_text(f"{current_player}'s response:", 20, 160, BLACK)
                                display_text(f"A: {response}", 20, 200, BLUE)
                                pygame.display.update()

                                wait_for_continue_button()
                                user_input = ''
                                answered = True  # Move to next player

                            elif event.key == pygame.K_BACKSPACE:
                                user_input = user_input[:-1]
                            else:
                                user_input += event.unicode

                clock.tick(30)

        # After questioning all alive players
        accusation_phase()
        night_phase()
        round_counter += 1

def reset_game():
    global player_status, discussion_log, question_history, user_input, active_input, current_player_index, round_counter

    player_status = [True] * len(player_names)
    discussion_log = []
    question_history = {player: [] for player in players}
    user_input = ''
    active_input = False
    current_player_index = 0
    round_counter = 1

    # Shuffle roles again for new game (optional)
    new_roles = ['Mafia', 'Townspeople', 'Townspeople', 'Doctor', 'Detective']
    random.shuffle(new_roles)
    for i, name in enumerate(players):
        players[name] = new_roles[i]

    # Debug print
    print("DEBUG - New player roles:")
    for name, role in players.items():
        print(f"{name}: {role}")


def main_menu():
    while True:
        screen.fill(WHITE)
        display_text("Welcome to Mafia Game", 250, 100, BLUE)

        # Buttons
        start_button = pygame.Rect(300, 250, 200, 60)
        quit_button = pygame.Rect(300, 350, 200, 60)

        pygame.draw.rect(screen, BLUE, start_button)
        display_text("Start Game", start_button.x + 40, start_button.y + 15, WHITE)

        pygame.draw.rect(screen, RED, quit_button)
        display_text("Quit", quit_button.x + 70, quit_button.y + 15, WHITE)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()
                    play_game()
                    return
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main_menu()

