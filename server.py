import socket
import threading
import random
import time

# Server settings
HOST = "0.0.0.0"
PORT = 9999

# Game state variables
cards = ["A", "B", "C", "D", "E", "F", "G", "H"]
cards = cards * 2
random.shuffle(cards)
card_states = [""] * len(cards)
turned_cards = [-1, -1]
player_turn = 0  # 0 for the first player, 1 for the second player

# List of connected clients
clients = []
turned_cards_player = 0


# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            clients.remove(client)


# Function to handle player actions
def handle_client(client_socket, player_id):

    # Add the client to the list of connected clients
    clients.append(client_socket)

    # Send a welcome message to the player
    client_socket.send("Welcome to the Memory Game!\n".encode())

    while True:
        try:
            data = client_socket.recv(1024).decode()
            print(data)
            if not data:
                break

            process_player_action(data, player_id)

        except Exception as e:
            print(f"Error handling client: {e}")
            break

    # Remove the client from the list of connected clients
    clients.remove(client_socket)
    client_socket.close()


# Function to process a player's action
def process_player_action(data, player_id):
    global turned_cards, player_turn, turned_cards_player

    action = data.strip().upper()
    parts = data.strip().split()
    print("Action", action)

    if parts[0] == "TURN":
        try:
            card_index = int(parts[1])
            print("Card Valid Card", is_valid_card(card_index))
            print("Card Hidden", is_card_hidden(card_index))
            if is_valid_card(card_index) and is_card_hidden(card_index):
                flip_card(player_id, card_index)
                turned_cards_player += 1

                if turned_cards_player == 2:
                    check_cards()
                    turned_cards_player = 0
                    change_player_turn(player_id)

        except Exception as e:
            print(f"Error processing card flip action: {e}")


# Function to check if the card index is valid
def change_player_turn(player_id):
    time.sleep(0.5)
    broadcast(f"PLAYERTURN {player_id}\n")

# Function to check if the card index is valid
def is_valid_card(card_index):
    return 0 <= card_index < len(cards)


# Function to check if the card is hidden
def is_card_hidden(card_index):
    return card_states[card_index] == ""


# Function to flip a card and process game logic
def flip_card(player_id, card_index):
    global turned_cards, player_turn

    card_states[card_index] = cards[card_index]
    broadcast(f"UPDATE {player_id} {card_index} {cards[card_index]}\n")

    if turned_cards[0] == -1:
        turned_cards[0] = card_index
    elif turned_cards[1] == -1:
        turned_cards[1] = card_index
        check_cards()


# Function to check if the turned cards are equal and update the game state
def check_cards():
    global turned_cards

    card1 = cards[turned_cards[0]]
    card2 = cards[turned_cards[1]]

    if card1 == card2:
        if turned_cards[0] != -1 and turned_cards[1] != -1:
            time.sleep(1)
            broadcast(f"REMOVE {turned_cards[0]} {turned_cards[1]}\n")
            turned_cards = [-1, -1]
    else:
        time.sleep(2)
        card_states[turned_cards[0]] = ""
        card_states[turned_cards[1]] = ""
        broadcast(f"HIDE {turned_cards[0]} {turned_cards[1]}\n")
        turned_cards = [-1, -1]



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)  # Allow two connections

    print("Waiting for connections...")

    player_id = 0  # 0 for the first player, 1 for the second player

    while True:
        client_socket, client_addr = server.accept()
        print(f"Connection received from {client_addr[0]}:{client_addr[1]}")

        # Start a thread to handle the client
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, player_id)
        )
        client_handler.start()

        player_id = 1 - player_id  # Switch between players


if __name__ == "__main__":
    main()
