import tkinter as tk
import socket
import threading

root = tk.Tk()
root.title("Memory Game")
buttons = []
client_socket = None
player_id = None
current_player = 0
cards_turned = 0
can_turn = False
player_id_label = tk.Label(root, text="You are the player ")
player_scores = [0, 0] 

player1_score_label = tk.Label(root, text=f"Score Player 0 - {player_scores[0]}")

player2_score_label = tk.Label(root, text=f"Score Player 1 - {player_scores[1]}")

# Função para enviar ações para o servidor
def send_action(action):
    print(f"Enviando ação: {action}")
    try:
        client_socket.send(action.encode())
    except Exception as e:
        print(f"Erro ao enviar ação para o servidor: {e}")


# Função para atualizar a aparência das cartas
def update_card(card_index, card_value):
    buttons[card_index].config(text=card_value)


# Função para esconder as cartas viradas
def hide_cards(card_index1, card_index2):
    buttons[card_index1].config(text=" ")
    buttons[card_index2].config(text=" ")


# Função para remover as cartas correspondentes
def remove_cards(card_index1, card_index2):
    buttons[card_index1].config(state=tk.DISABLED)
    buttons[card_index2].config(state=tk.DISABLED)

# Função para atualizar e exibir a pontuação dos jogadores na GUI
def update_player_scores():
    global player1_score_label, player2_score_label
    player1_score_label.config(text=f"Score Player 0 - {player_scores[0]}")
    player2_score_label.config(text=f"Score Player 1 - {player_scores[1]}")

# Função para processar as atualizações recebidas do servidor
def process_update(data):
    global current_player, cards_turned, can_turn, player_id
    try:
        parts = data.strip().split()
        print("Parts", parts)
        if parts[0] == "UPDATE":
            _, card_index = map(int, parts[1:3])
            card_value = parts[3]  # Card is a string
            update_card(card_index, card_value)
        elif parts[0] == "REMOVE":
            card_index1, card_index2 = map(int, parts[1:])
            remove_cards(card_index1, card_index2)
        elif parts[0] == "HIDE":
            card_index1, card_index2 = map(int, parts[1:])
            hide_cards(card_index1, card_index2)
        elif parts[0] == "PLAYERTURN":
            current_player = int(parts[1])
            if player_id == current_player:
                can_turn = True
            else:
                can_turn = False
        elif parts[0] == "PLAYERID":
            player_id = int(parts[1])
            update_player_id_label(player_id)
        elif parts[0] == "SCORE":
            player_scores[0], player_scores[1] = map(int, parts[1:])
            update_player_scores()  


    except Exception as e:
        print(f"Erro ao processar atualização: {e}")


def on_card_click(card_index):
    global can_turn
    if can_turn:
        print(f"Carta {card_index} clicada")
        send_action(f"TURN {card_index}")


def receive_updates():
    global client_socket
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            process_update(data)
        except Exception as e:
            print(f"Erro ao receber atualizações do servidor: {e}")


def create_gui():
    global player_id, player_id_label, player1_score_label, player2_score_label

    player1_score_label = tk.Label(root, text=f"Score Player 0 - {player_scores[0]}")
    player1_score_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    player2_score_label = tk.Label(root, text=f"Score Player 1 - {player_scores[1]}")
    player2_score_label.grid(row=0, column=2, columnspan=2, padx=10, pady=10)

    card_buttons = []
    for i in range(16):  # 16 Cards
        card_button = tk.Button(
            root, text=" ", width=5, height=2, command=lambda i=i: on_card_click(i)
        )
        card_buttons.append(card_button)
        card_button.grid(row=i // 4 + 1, column=i % 4)

    player_id_label = tk.Label(root, text=f"You are the player {player_id}")
    player_id_label.grid(row=17 // 4 + 1, columnspan=4)     
    return card_buttons


def update_player_id_label(new_player_id):
    global player_id_label
    player_id_label.config(text=f"You are the player {new_player_id}")

def main():
    global client_socket, buttons

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("localhost", 9999))
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")
        return

    # Thread to receive server updates
    receive_thread = threading.Thread(target=receive_updates)
    receive_thread.start()

    buttons = create_gui()

    root.mainloop()


if __name__ == "__main__":
    main()
