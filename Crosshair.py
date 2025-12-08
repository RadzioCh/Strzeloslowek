import tkinter as tk

class Crosshair:
    def __init__(self, canvas, radius=12, color='red', thickness=2, root=None):
        self.canvas = canvas
        self.root = root or canvas.winfo_toplevel()  # Pobierz root jeśli nie podany
        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.oval = None
        self.hline = None
        self.vline = None

        # ukryj systemowy kursor nad canvasem
        try:
            self.canvas.config(cursor='none')
        except Exception:
            pass

        # utwórz elementy (początkowo poza obszarem) z tagiem 'crosshair'
        self._create_items(-100, -100)

        # wypchnij na wierzch i ustaw jako 'disabled' żeby nie przechwytywały kliknięć
        try:
            self.canvas.tag_raise('crosshair')
            self.canvas.itemconfigure('crosshair', state='disabled')
        except Exception:
            pass

        self._bind_events()

    def _create_items(self, x, y):
        r = self.radius
        if self.oval is None:
            self.oval = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                                outline=self.color, width=self.thickness, tags='crosshair')
            self.hline = self.canvas.create_line(x - r*2, y, x + r*2, y,
                                                 fill=self.color, width=self.thickness, tags='crosshair')
            self.vline = self.canvas.create_line(x, y - r*2, x, y + r*2,
                                                 fill=self.color, width=self.thickness, tags='crosshair')
        else:
            self.canvas.coords(self.oval, x - r, y - r, x + r, y + r)
            self.canvas.coords(self.hline, x - r*2, y, x + r*2, y)
            self.canvas.coords(self.vline, x, y - r*2, x, y + r*2)

    def _bind_events(self):
        self.canvas.bind('<Motion>', self._on_motion)
        self.canvas.bind('<Enter>', self._on_enter)
        self.canvas.bind('<Leave>', self._on_leave)
        self.canvas.bind('<Destroy>', self._on_destroy)

    def _on_motion(self, event):
        x, y = event.x, event.y
        w = max(1, int(self.canvas.winfo_width()))
        h = max(1, int(self.canvas.winfo_height()))
        x = max(0, min(w, x))
        y = max(0, min(h, y))
        # przenosimy elementy; ponieważ są 'disabled', kliknięcia nie będą blokowane
        self._create_items(x, y)

    def _on_enter(self, event):
        # pokaż (itemy są widoczne niezależnie od state)
        self.canvas.itemconfigure('crosshair', state='disabled')

    def _on_leave(self, event):
        # ukryj, gdy mysz wychodzi
        self.canvas.itemconfigure('crosshair', state='hidden')

    def _on_destroy(self, event):
        self.destroy()

    def animate_shot(self, start_x, start_y):
        x1, y1, x2, y2 = self.canvas.coords(self.oval)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        shot_line = self.canvas.create_line(start_x, start_y, start_x, start_y, fill='red', width=3, tags='shot')
        self.canvas.tag_raise('shot')

        def animate_step(step=0, max_steps=20):
            if step >= max_steps:
                self.canvas.delete(shot_line)
                return

            new_x = start_x + (center_x - start_x) * (step + 1) / max_steps
            new_y = start_y + (center_y - start_y) * (step + 1) / max_steps

            self.canvas.coords(shot_line, start_x, start_y, new_x, new_y)
            self.root.after(30, lambda: animate_step(step + 1))

        animate_step()


    def destroy(self):
        try:
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Enter>')
            self.canvas.unbind('<Leave>')
            self.canvas.unbind('<Destroy>')
            self.canvas.delete('crosshair')
            self.canvas.delete('shot')  # Usuń ewentualne pozostałe linie strzału
            try:
                self.canvas.config(cursor='')
            except Exception:
                pass
        except Exception:
            pass