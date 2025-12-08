from threading import Thread
import tkinter as tk
from GetWords import GetWords
from Crosshair import Crosshair
import random
from tkinter import font as tkfont
from time import sleep
#import pyttsx3
import os
import pygame
from threading import Thread
from gtts import gTTS
import tempfile


class Aplikacja:
    def __init__(self, root):
        self.root = root
        self.root.title("Strzelosłówek")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        
        # narzędzie do mowy SYSTEMOWE  działa z funkcją generate_speech_OLD
        # self.engine = pyttsx3.init()
        # self.engine.setProperty('rate', 150)
        # self.engine.setProperty('volume', 1.0)

        
        
        # Tworzenie głównego menu
        self.menu_glowne = tk.Menu(self.root)
        self.root.config(menu=self.menu_glowne)
        
        # Tworzenie menu "GRA"
        self.menu_gra = tk.Menu(self.menu_glowne, tearoff=0)
        self.menu_glowne.add_cascade(label="GRA", menu=self.menu_gra)
        
        # Dodawanie opcji do menu "GRA"
        self.menu_gra.add_command(label="START", command=self.start)
        self.menu_gra.add_command(label="PAUZA", command=self.pauza)
        self.menu_gra.add_command(label="STOP", command=self.stop)

        # Obszar gry (początkowo ukryty)
        self.obszar_gry = None

        # celowniczek
        self.crosshair = None

        # lista prostokątów już zajętych: (x1, y1, x2, y2)
        self.placed_boxes = []
        # mapowanie tag -> dane słowa (do obsługi kliknięć)
        self.word_map = {}
        self.remember_good_word = {}
        self.countWords = 0
        self.all_words = ""
        self.lang = "en"
        self.cel = 1
        

    def start(self):
        if self.obszar_gry:
            self.obszar_gry.destroy()  # Usuń poprzedni obszar, jeśli istnieje

        # Tworzenie nowego obszaru gry
        self.obszar_gry = tk.Canvas(self.root, bg="lightblue")

        # Ustawienie stałych współrzędnych i rozmiarów
        x1, y1 = 50, 50  # Lewy górny róg
        x2, y2 = self.root.winfo_screenwidth() - 50, self.root.winfo_screenheight() - 100  # Prawy dolny róg
        width = x2 - x1
        height = y2 - y1

        self.obszar_gry.place(x=x1, y=y1, width=width, height=height)

        # pobieramy słówka
        self.getWords = GetWords()
        words, cel, lang = self.getWords.get_word_list()
        self.lang = lang
        self.cel = cel

        # print('Liczba słówek do nauki:', self.all_words)

        self.countWords = len(words)
        countWordsArray = (self.countWords -1)
        self.countWordsArray = countWordsArray
        self.words = words
        self.width = width
        self.height = height

        if self.countWords > len(self.remember_good_word):
            self.new_load_words(countWordsArray, words, width, height)
        else:
            try:
                self.obszar_gry.update_idletasks()
                cx = (self.obszar_gry.winfo_width() // 2) - 450
                cy = self.obszar_gry.winfo_height() // 2
            except Exception:
                cx, cy = 200, 200

            text_ok = self.obszar_gry.create_text(
                cx, cy,
                text="BRAWO! Wszystkie słowa opanowane!",
                anchor="w",
                font=("Arial", 60),
                fill="black"
            )
            self.obszar_gry.tag_lower(text_ok)

    def new_load_words(self, countWordsArray, words, width=0, height=0):

        

        self.word_map = {}
        self.placed_boxes = []
        self.obszar_gry.delete("all")

        points = "PUNKTY: " + str(len(self.remember_good_word)) + " / " + str(self.countWords)
        self.obszar_gry.update_idletasks()
        cx = (self.obszar_gry.winfo_width() // 2) - 120
        self.obszar_gry.create_text(
            cx, 10,
            anchor="nw",
            font=("Arial", 20),
            fill="black",
            width=500,
            justify="center",
            text=points
        )

        if self.countWords == len(self.remember_good_word):
            try:
                self.obszar_gry.update_idletasks()
                cx = (self.obszar_gry.winfo_width() // 2)
                cy = self.obszar_gry.winfo_height() // 2
            except Exception:
                cx, cy = 200, 200

            text_winer = self.obszar_gry.create_text(
                cx, cy,
                text="BRAWO! Wszystkie słowa opanowane!",
                anchor="w",
                font=("Arial", 50),
                fill="black",
                width=500,
                justify="center"
            )
            self.obszar_gry.tag_lower(text_winer)
            self.word_map = {}
            self.placed_boxes = []
            #self.obszar_gry.delete("all")
            if self.crosshair:
                self.crosshair.destroy()
                self.crosshair = None
                return


        i = random.randint(0, countWordsArray)
        # słówka do nauki
        wordToLearn = words[i][0]
        wordTranslation = words[i][1]

        if wordToLearn.upper() in self.remember_good_word:
            while wordToLearn.upper() in self.remember_good_word:
                i = random.randint(0, countWordsArray)
                wordToLearn = words[i][0]
                wordTranslation = words[i][1]

        #słówka aby zrobić szum
        noisePool = [w for idx, w in enumerate(words) if idx != i]
        noiseWords = random.sample(noisePool, 5)

        self.writeWord(wordToLearn, wordTranslation, width, height, True)
        for nw in noiseWords:
            self.writeWord(nw[0], nw[1], width, height)

        # utwórz celowniczek który będzie śledzić mysz nad canvassem
        self.crosshair = Crosshair(self.obszar_gry, root=self.root)


    def generate_speech(self, word):
        def speak():
            output_file = "out.mp3"
            try:
                # Inicjalizuj pygame mixer dla odtwarzania dźwięku
                pygame.mixer.init()
                
                # Utwórz plik audio
                tts = gTTS(text=word, lang=self.lang, slow=False)
                tts.save(output_file)
                
                # Odtwórz za pomocą pygame
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                
                # Czekaj aż się skończy
                while pygame.mixer.music.get_busy():
                    #sleep(0.1)
                    pass

                # Zatrzymaj i zamknij mixer aby zwolnić plik
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                #sleep(0.1)

                # Usuń plik po odtworzeniu
                if os.path.exists(output_file):
                    os.remove(output_file)
                    
            except Exception as e:
                print(f"Błąd gTTS: {e}")
        
        thread = Thread(target=speak, daemon=True)
        thread.start()
        #thread.join()

    def reload_game(self):
        self.new_load_words(self.countWordsArray, self.words, self.width, self.height)

    def writeWord(self, word, translateWord, width, height, showTranslaction=False):

        if(showTranslaction == True):
            translateWord = translateWord.upper()

            # font i padding dla tłumaczenia (wyświetlane w lewym górnym rogu canvasa)
            font_t = tkfont.Font(family="Helvetica", size=18, weight="bold")
            pad_t = 5

            # zmierz rozmiary tekstu tłumaczenia
            tw = font_t.measure(translateWord)
            th = font_t.metrics("linespace")

            # pozycja w lewym górnym rogu (wewnątrz canvasa)
            tx1, ty1 = pad_t, pad_t
            tx2, ty2 = tx1 + tw + 2 * pad_t, ty1 + th + 2 * pad_t

            rect_id = self.obszar_gry.create_rectangle(
                tx1, ty1,
                tx2, ty2,
                fill="green", outline=""
            )

            text_id_translate = self.obszar_gry.create_text(
                tx1 + pad_t, ty1 + pad_t,
                anchor="nw",
                text=translateWord,
                font=font_t,
                fill="black"
            )

            if self.cel == 2:
                self.root.after(5, lambda: self.generate_speech(translateWord))

            self.obszar_gry.tag_lower(rect_id, text_id_translate)

            # zarejestruj zajęty obszar, żeby inne słowa się nie nakładały
            self.placed_boxes.append((tx1, ty1, tx2, ty2))


        word = word.upper()
        # Wyświetl wordToLearn na canvase w losowej pozycji z białym tłem i paddingiem 5px
        pad = 5  # padding w pikselach
        # wybierz font (możesz zmienić rodzinę/rozmiar)
        font = tkfont.Font(family="Helvetica", size=24, weight="normal")

         # zmierz rozmiary tekstu
        text_w = font.measure(word)
        text_h = font.metrics("linespace")

        # upewnij się, że mieści się w obszarze gry
        max_x = max(0, width - (text_w + 2 * pad))
        max_y = max(0, height - (text_h + 2 * pad))

        def overlaps(a, b, gap=0):
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 + gap <= bx1 or bx2 + gap <= ax1 or ay2 + gap <= by1 or by2 + gap <= ay1)

        max_attempts = 200
        chosen_box = None
        last_box = None
        gap_between = 5  # minimal odstęp między prostokątami

        for _ in range(max_attempts):
            rx = random.randint(0, max_x)
            ry = random.randint(0, max_y)
            box = (rx, ry, rx + text_w + 2 * pad, ry + text_h + 2 * pad)
            last_box = box
            collision = False
            for placed in self.placed_boxes:
                if overlaps(box, placed, gap=gap_between):
                    collision = True
                    break
            if not collision:
                chosen_box = box
                break

        # jeśli nie znaleziono bezkolizyjnej pozycji, użyj ostatniej (lub wrzuć mimo kolizji)
        if chosen_box is None:
            chosen_box = last_box

        rx1, ry1, rx2, ry2 = chosen_box

        # narysuj prostokąt tła (biały) i tekst na nim
        tag = f"word_{len(self.word_map)}"
        rect_id = self.obszar_gry.create_rectangle(
            rx1, ry1,
            rx2, ry2,
            fill="white", outline="", tags=(tag, "word")
        )
        text_id = self.obszar_gry.create_text(
            rx1 + pad, ry1 + pad,
            anchor="nw",
            text=word,
            font=font,
            fill="black",
            tags=(tag, "word")
        )
        # upewnij się, że tło jest pod tekstem
        self.obszar_gry.tag_lower(rect_id, text_id)

        # zarejestruj kliknięcie na elemencie (powiązane z tagiem)
        # użycie domyślnego argumentu t=tag zapobiega zamykaniu się na zmienne w pętli
        self.obszar_gry.tag_bind(tag, '<Button-1>', lambda e, t=tag: self.on_word_click(e, t))


        # zapamiętaj zajęty obszar
        self.placed_boxes.append(chosen_box)
        self.word_map[tag] = {
            "word": word,
            "translate": translateWord,
            "box": chosen_box,
            "rect_id": rect_id,
            "text_id": text_id
        }

    

    def on_word_click(self, event, tag):
        """Obsługa kliknięcia w słowo na canvasie."""
        text_ok = None
        bad_text = None

        translatWorld = self.word_map.get('word_0')

        info = self.word_map.get(tag)
        if not info:
            return

        # Animacja strzału do środka kółka
        if self.crosshair:
            self.crosshair.animate_shot(event.x, event.y)
        
        try:
            self.obszar_gry.update_idletasks()
            cx = self.obszar_gry.winfo_width() // 2
            cy = self.obszar_gry.winfo_height() // 2
        except Exception:
            cx, cy = 200, 200

            print(f"cx: {cx}, cy: {cy}, canvas width: {self.obszar_gry.winfo_width()}, height: {self.obszar_gry.winfo_height()}")

        # przykładowa akcja: wypisz i chwilowo podświetl ramkę
        #print(f"Kliknięto: {info['word']}  tłum.: {info.get('translate')}")
        try:
            if translatWorld is None:
                print("translatWorld is None")
                return

            if info['word'] == translatWorld['word']:
                # Generuj dźwięk asynchronicznie
                

                text_ok = self.obszar_gry.create_text(
                    cx, cy,
                    text="GOOD JOB!",
                    anchor="center",
                    font=("Arial", 60),
                    fill="black",
                    width=300,
                    justify="center"
                )
                self.obszar_gry.tag_lower(text_ok)

                if self.cel == 1:
                    self.root.after(10, lambda: self.generate_speech(translatWorld['word']))

                self.remember_good_word[info['word']] = True

                # usuń komunikaty po x
                self.root.after(800, lambda: (self.obszar_gry.delete(text_ok) if text_ok else None))
                self.root.after(900, lambda: self.reload_game())

            elif info['word'] != translatWorld['word']:
                print("GAME OVER condition met")
                bad_text = self.obszar_gry.create_text(
                    cx, cy,
                    text=f"GAME OVER\nPrawidłowe słówko to: {translatWorld['word']}",
                    anchor="center",
                    font=("Arial", 40),
                    fill="black",
                    width=700,
                    justify="center"
                )
                self.obszar_gry.tag_lower(bad_text)
                self.word_map = {}
                self.placed_boxes = []
                self.remember_good_word = {}
                #self.obszar_gry.delete("all")
                if self.crosshair:
                    self.crosshair.destroy()
                    self.crosshair = None


            if text_ok:
                self.obszar_gry.tag_raise(text_ok)
            if bad_text:
                self.obszar_gry.tag_raise(bad_text)

            # podświetlenie klikniętego prostokąta
            self.obszar_gry.itemconfigure(info['rect_id'], outline='blue', width=2)
            # przywróć po krótkim czasie
            self.root.after(200, lambda: self.obszar_gry.itemconfigure(info['rect_id'], outline='', width=1))

            print(self.remember_good_word)

        except Exception as e:
            print(f"Exception in on_word_click: {e}")


    def pauza(self):
        print("Pauza gry")
        
    def stop(self, word):
        # usuń celowniczek najpierw
        if self.crosshair:
            self.crosshair.destroy()
            self.crosshair = None

        if self.obszar_gry:
            self.obszar_gry.destroy()
            self.obszar_gry = None
            self.placed_boxes.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = Aplikacja(root)
    root.mainloop()