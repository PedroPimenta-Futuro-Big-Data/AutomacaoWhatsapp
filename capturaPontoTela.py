import pyautogui
pos = pyautogui.locateOnScreen('assets/lupa.png', confidence=0.7)
print("Posição encontrada:", pos)