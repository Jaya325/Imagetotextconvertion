import tkinter as tk
from PIL import Image, ImageTk
from picamera2 import Picamera2
import threading
import time

class CameraApp:
    def __init__(self, window, width=640, height=480, fps=30):
        self.window = window
        self.window.title("Raspberry Pi Camera Stream")
        self.label = tk.Label(window)
        self.label.pack()

        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": (width, height)})
        self.picam2.configure(config)
        self.picam2.start()

        self.update_interval = int(1000 / fps)
        self.running = True
        threading.Thread(target=self._update_frame, daemon=True).start()
        window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _update_frame(self):
        while self.running:
            frame = self.picam2.capture_array()
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
            time.sleep(self.update_interval / 1000.0)

    def _on_close(self):
        self.running = False
        self.picam2.stop()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
