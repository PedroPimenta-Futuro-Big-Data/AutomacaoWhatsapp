import pyautogui

print("Posicione o mouse sobre o local desejado e pressione Ctrl + C para parar.")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Coordenadas: X={x}, Y={y}", end="\r")  # Atualiza na mesma linha do terminal
except KeyboardInterrupt:
    print("\nCaptura encerrada.")
