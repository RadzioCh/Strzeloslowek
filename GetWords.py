

class GetWords:

    def __init__(self):
        pass

    def get_word_list(self):
        words = []
        with open("words.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    eng, pl = line.split(";", 1)
                    words.append([eng, pl])
                    
        return words
        