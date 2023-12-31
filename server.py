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
current_player = 0 
# List of connected clients
clients = []
turned_cards_player = 0
player_scores = [0, 0]



def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            clients.remove(client)



def handle_client(client_socket, player_id):

    clients.append(client_socket)

    client_socket.send("Welcome to the Memory Game!\n".encode())

    print(player_id, current_player)
    if player_id == current_player:
        time.sleep(0.3)
        broadcast(f"PLAYERTURN {player_id}\n") 

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

        except Exception as e:
            print(f"Error processing card flip action: {e}")


def change_player_turn():
    global current_player
    current_player = 1 - current_player
    time.sleep(0.5)
    broadcast(f"PLAYERTURN {current_player}\n")

def update_player_scores():
    global player_scores
    player_scores[current_player] += 1
    time.sleep(0.3)
    broadcast(f"SCORE {player_scores[0]} {player_scores[1]}\n")    


def is_valid_card(card_index):
    return 0 <= card_index < len(cards)

def is_card_hidden(card_index):
    global card_states
    return card_states[card_index] == ""

def is_game_over():
    global card_states
    return card_states.count("") == 0

def end_game():
    global player_scores
    winner = player_scores.index(max(player_scores))
    time.sleep(1) 
    broadcast(f"GAMEOVER WINNER {winner}\n")


def flip_card(player_id, card_index):
    global turned_cards

    card_states[card_index] = cards[card_index]
    broadcast(f"UPDATE {player_id} {card_index} {cards[card_index]}\n")

    if turned_cards[0] == -1:
        turned_cards[0] = card_index
    elif turned_cards[1] == -1:
        turned_cards[1] = card_index
        check_cards()


def check_cards():
    global turned_cards

    card1 = cards[turned_cards[0]]
    card2 = cards[turned_cards[1]]

    if card1 == card2:
        if turned_cards[0] != -1 and turned_cards[1] != -1:
            time.sleep(1)
            broadcast(f"REMOVE {turned_cards[0]} {turned_cards[1]}\n")
            turned_cards = [-1, -1]
            update_player_scores()
            if is_game_over():
                end_game()
            
    else:
        time.sleep(2)
        card_states[turned_cards[0]] = ""
        card_states[turned_cards[1]] = ""
        broadcast(f"HIDE {turned_cards[0]} {turned_cards[1]}\n")
        turned_cards = [-1, -1]
        change_player_turn()    



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)  # Allow two connections

    print("Waiting for connections...")

    player_id = 0  # 0 for the first player, 1 for the second player

    while True:
        client_socket, client_addr = server.accept()
        print(f"Connection received from {client_addr[0]}:{client_addr[1]}")

        client_socket.send(f"PLAYERID {player_id}\n".encode())
        # Start a thread to handle the client
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, player_id)
        )
        client_handler.start()

        player_id = 1 - player_id  # Switch between players


if __name__ == "__main__":
    main()
