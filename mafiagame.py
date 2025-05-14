import random
import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mafia Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

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

# Response templates
response_templates = {
    'Mafia': {
        'alibi': ["I was just home alone.", "Nowhere special, just chilling."],
        'observation': ["I didn't see anyone.", "It was too dark to notice anything."],
        'accusation': ["Why are you blaming me?", "This is ridiculous!"],
        'general': ["I don’t know what to say.", "I can’t help you with that."]
    },
    'Townspeople': {
        'alibi': ["I was at home with my dog.", "Just reading. Quiet night."],
        'observation': ["I saw Blake near the market.", "Someone walked by, not sure who."],
        'accusation': ["I’m innocent!", "Why would I do that?"],
        'general': ["Sorry, I don’t know anything.", "That’s confusing to me too."]
    },
    'Doctor': {
        'alibi': ["I was at the clinic.", "I was making rounds at the hospital."],
        'observation': ["I didn’t see much. It was a quiet night.", "I heard some footsteps outside."],
        'accusation': ["I'm a doctor! Why would I be involved in this?", "Stop accusing me!"],
        'general': ["I don't have all the details.", "I can't say much."]
    },
    'Detective': {
        'alibi': ["I was investigating last night.", "I was checking out some leads."],
        'observation': ["I saw something suspicious near the bakery.", "I observed people coming and going."],
        'accusation': ["I have more information than you think.", "Don’t question me!"],
        'general': ["I don’t have any new leads.", "I’ll keep an eye on things."]
    }
}

def display_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def categorize_question(question):
    q = question.lower()
    if any(word in q for word in ['where', 'location', 'go', 'doing', 'last night', 'yesterday']):
        return 'alibi'
    elif any(word in q for word in ['see', 'hear', 'notice', 'watch', 'who']):
        return 'observation'
    elif any(word in q for word in ['why', 'lying', 'suspicious', 'truth', 'hide']):
        return 'accusation'
    else:
        return 'general'

def generate_dynamic_response(player, question):
    role = players[player]
    category = categorize_question(question)
    response_pool = response_templates[role].get(category, response_templates[role]['general'])
    response = random.choice(response_pool)
    discussion_log.append(f"{player}: {response}")
    return response

def show_log():
    scroll = 0
    running = True
    while running:
        screen.fill(WHITE)
        display_text("Discussion Log", 20, 20, BLUE)

        for i, log_entry in enumerate(discussion_log[scroll:scroll + 10]):
            display_text(log_entry, 20, 60 + i * 40)

        display_text("Press ESC to return", 20, 550, RED)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP and scroll > 0:
                    scroll -= 1
                elif event.key == pygame.K_DOWN and scroll + 10 < len(discussion_log):
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Exit when the button is clicked


def play_game():
    global user_input, active_input, current_player_index, round_counter

    input_box = pygame.Rect(20, 140, 760, 40)

    while True:
        screen.fill(WHITE)

        current_player = player_names[current_player_index]
        display_text(f"Round {round_counter}", 20, 20, BLUE)
        display_text(f"Investigate {current_player}", 20, 60, BLACK)

        # Input box
        pygame.draw.rect(screen, BLUE if active_input else BLACK, input_box, 2)
        display_text(user_input, input_box.x + 10, input_box.y + 5, BLACK)
       # Draw View Log button
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
                    if event.key == pygame.K_RETURN:
                        question = user_input.strip()
                        discussion_log.append(f"{current_player}: {question}")
                        response = generate_dynamic_response(current_player, question)

                        # Display the response briefly
                        screen.fill(WHITE)
                        display_text(f"Q: {question}", 20, 100, BLACK)
                        display_text(f"{current_player}'s response:", 20, 160, BLACK)
                        display_text(f"A: {response}", 20, 200, BLUE)
                        pygame.display.update()
                        wait_for_continue_button()

                        user_input = ''
                        current_player_index += 1
                        if current_player_index >= len(player_names):
                            current_player_index = 0
                            round_counter += 1
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

        clock.tick(30)

if __name__ == "__main__":
    play_game()
