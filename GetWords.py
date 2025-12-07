

class GetWords:

    def __init__(self):
        pass

    def get_word_list(self):
        words = []
        reversed_words = []
        cel = 0
        lang = "en"
        with open("words.txt", "r", encoding="utf-8") as f:
            for i, line  in enumerate(f):
                line = line.strip()
                if i == 0:
                    _, typ = line.split(":", 1)
                    cel = int(typ.strip())
                    continue

                if i == 1:
                    _, lang = line.split(":", 1)
                    lang = lang.strip()
                    continue
                
                # if line:
                eng, pl = line.split(";", 1)
                words.append([eng, pl])

        if cel == 2:
            for eng, pl in words:
                reversed_words.append([pl, eng])

        words = reversed_words if cel == 2 else words

        # print(f"Liczba słówek załadowanych: words {words} lang: {lang}")
                    
        return words, cel, lang
        