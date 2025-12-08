import pyttsx3
print("Początek skryptu")

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"Język: {voice.languages}, Nazwa: {voice.name}")

print("Koniec skryptu")
