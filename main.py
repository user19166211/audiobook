import pyttsx3
import PyPDF2
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename
from queue import Queue, Empty

class AudioBookReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Audiobook Reader")
        self.text_chunks = []
        self.current_index = 0
        self.queue = Queue()
        self.is_paused = False
        self.is_reading = False

        self.engine = pyttsx3.init()
        self.speech_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.speech_thread.start()

        tk.Button(root, text="Open PDF", command=self.load_pdf).pack(pady=10)
        self.play_btn = tk.Button(root, text="Play", command=self.play_text)
        self.play_btn.pack(pady=5)
        self.pause_btn = tk.Button(root, text="Pause", command=self.pause)
        self.pause_btn.pack(pady=5)
        self.resume_btn = tk.Button(root, text="Resume", command=self.resume)
        self.resume_btn.pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=10)

    def load_pdf(self):
        path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return

        reader = PyPDF2.PdfReader(path)
        self.text_chunks.clear()

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"[Page {page_num + 1}] Raw text:\n{text}\n{'-'*30}")
            if text:
                for line in text.strip().split('.'):
                    line = line.strip()
                    if line:
                        sentences = line.split('. ')
                        self.text_chunks.extend(sentences)

            
        for i, chunk in enumerate(self.text_chunks[:5]):
            print(f"{i + 1}: {repr(chunk)}")

        self.status_label.config(text="PDF loaded. Ready to play.")
        self.current_index = 0


    def play_text(self):
        if not self.text_chunks or self.is_reading:
            return

        self.is_reading = True
        self.status_label.config(text="Reading...")

        threading.Thread(target=self.read_loop, daemon=True).start()

    def read_loop(self):
        while self.current_index < len(self.text_chunks) and self.is_reading:
            if self.is_paused:
                continue 
            chunk = self.text_chunks[self.current_index]
            self.queue.put(chunk)
            self.current_index += 1
        self.is_reading = False

    def process_queue(self):
        while True:
            try:
                text = self.queue.get(timeout=0.5)
                self.engine.say(text)
                self.engine.runAndWait()
            except Empty:
                continue

    def pause(self):
        self.is_paused = True
        self.status_label.config(text="Paused.")

    def resume(self):
        self.is_paused = False
        self.status_label.config(text="Resumed.")
        if not self.is_reading and self.current_index < len(self.text_chunks):
            self.is_reading = True
            threading.Thread(target=self.read_loop, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioBookReader(root)
    root.mainloop()
