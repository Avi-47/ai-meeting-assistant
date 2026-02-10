import tkinter as tk

class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.geometry("600x220")
        self.root.title("AI Meeting Assistant")

        self.status = tk.Label(
            self.root,
            text="🎤 Mic OFF",
            font=("Segoe UI", 12),
            fg="red"
        )
        self.status.pack(pady=5)

        self.text = tk.Text(self.root, wrap="word", font=("Segoe UI", 14))
        self.text.pack(expand=True, fill="both")

    def set_listening(self, listening: bool):
        if listening:
            self.status.config(text="🎤 Listening...", fg="green")
        else:
            self.status.config(text="🎤 Mic OFF", fg="red")

    def update_text(self, content):
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, content)

    def run(self):
        self.root.mainloop()

    def show_live_text(self, text):
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, text)
