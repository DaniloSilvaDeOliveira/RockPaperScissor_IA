import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
import random
import time

# Define o caminho absoluto para o diretório do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Largura
cap.set(4, 720)   # Altura

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Variáveis do Jogo
game_started = False
game_over = False
player_choice = None
computer_choice = None
choices = ["Pedra", "Papel", "Tesoura"]
score = {"Jogador": 0, "Computador": 0}
round_result = ""
countdown = 3  # Tempo de contagem regressiva em segundos
start_time = None
choice_time = None  # Tempo em que as escolhas foram feitas
display_duration = 3  # Duração para exibir as escolhas em segundos

# Coordenadas e cor do botão "INICIAR"
start_button_color = (0, 255, 0)
start_button_pos = (640, 360)  # Centro da tela
start_button_radius = 50

# Nome do jogo
game_name = "Pedra Papel Tesoura"

# Função para detectar a escolha do jogador
def detect_choice(hand):
    fingers = detector.fingersUp(hand)
    if fingers == [0, 1, 1, 0, 0]:
        return "Tesoura"
    elif fingers == [0, 0, 0, 0, 0]:
        return "Pedra"
    elif fingers == [1, 1, 1, 1, 1]:
        return "Papel"
    return None

# Função para determinar o vencedor
def determine_winner(player, computer):
    if player == computer:
        return "Empate"
    elif (player == "Pedra" and computer == "Tesoura") or \
         (player == "Papel" and computer == "Pedra") or \
         (player == "Tesoura" and computer == "Papel"):
        return "Jogador"
    else:
        return "Computador"

# Loop principal
while True:
    success, img = cap.read()
    
    # Verifica se a captura foi bem-sucedida
    if not success:
        print("Falha ao capturar a imagem da webcam")
        break

    img = cv2.flip(img, 1)  # Espelha a imagem

    # Detecta as mãos
    hands, img = detector.findHands(img, draw=False)

    if not game_started:
        # Exibe o nome do jogo centralizado no topo da tela
        text_size = cv2.getTextSize(game_name, cv2.FONT_HERSHEY_COMPLEX, 2, 2)[0]
        text_x = (1280 - text_size[0]) // 2  # Centraliza o texto horizontalmente
        cvzone.putTextRect(img, game_name, (text_x, 100), scale=4, offset=20, colorR=(0, 0, 255), thickness=5)

        # Exibe o botão INICIAR centralizado
        cv2.circle(img, start_button_pos, start_button_radius, start_button_color, cv2.FILLED)
        cvzone.putTextRect(img, 'INICIAR', (start_button_pos[0] - 50, start_button_pos[1] + 10), scale=3, offset=20)

        # Verifica se a mão está "tocando" o botão INICIAR
        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            x1, y1, _ = lmList[5]

            # Calcula a distância entre o dedo e o centro do botão INICIAR
            distance = np.sqrt((x1 - start_button_pos[0]) ** 2 + (y1 - start_button_pos[1]) ** 2)

            if distance < start_button_radius:
                game_started = True
                game_over = False
                player_choice = None
                computer_choice = None
                round_result = ""
                start_time = time.time()  # Inicia o temporizador

    elif not game_over:
        elapsed_time = time.time() - start_time
        remaining_time = countdown - int(elapsed_time)

        if remaining_time > 0:
            # Exibe a contagem regressiva
            cvzone.putTextRect(img, f'Tempo: {remaining_time}', (600, 300), scale=3, offset=20, colorR=(0, 0, 255), thickness=5)
        else:
            if hands and not player_choice:
                hand = hands[0]
                player_choice = detect_choice(hand)

                if player_choice:
                    computer_choice = random.choice(choices)
                    winner = determine_winner(player_choice, computer_choice)

                    if winner == "Jogador":
                        score["Jogador"] += 1
                    elif winner == "Computador":
                        score["Computador"] += 1

                    round_result = f"{winner} venceu" if winner != "Empate" else "empate"
                    choice_time = time.time()  # Armazena o tempo em que as escolhas foram feitas

            # Exibe as escolhas do jogador e do computador por um período específico
            if player_choice and computer_choice:
                cvzone.putTextRect(img, f'Jogador: {player_choice}', (100, 200), scale=3, offset=20)
                cvzone.putTextRect(img, f'Computador: {computer_choice}', (800, 200), scale=3, offset=20)

                if time.time() - choice_time > display_duration:
                    game_over = True

    else:
        # Exibe o resultado da rodada e a pontuação
        cvzone.putTextRect(img, round_result, (500, 300), scale=3, offset=20)
        cvzone.putTextRect(img, f'Pontos - Jogador: {score["Jogador"]} Computador: {score["Computador"]}', (400, 400), scale=2, offset=20)
        cvzone.putTextRect(img, 'Pressione R para Reiniciar', (500, 500), scale=2, offset=10)

    cv2.imshow("Imagem", img)
    key = cv2.waitKey(1)

    # Pressione 'r' para reiniciar o jogo
    if key == ord('r') and game_over:
        game_started = False
        game_over = False
        player_choice = None
        computer_choice = None
        round_result = ""

    # Pressione 'ESC' para sair
    if key == 27:  # 27 é o código da tecla ESC
        break

cap.release()
cv2.destroyAllWindows()