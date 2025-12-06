import tkinter as tk

class Crosshair:
    def __init__(self, canvas, radius=12, color='red', thickness=2):
        self.canvas = canvas
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

    def destroy(self):
        try:
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Enter>')
            self.canvas.unbind('<Leave>')
            self.canvas.unbind('<Destroy>')
            self.canvas.delete('crosshair')
            try:
                self.canvas.config(cursor='')
            except Exception:
                pass
        except Exception:
            pass