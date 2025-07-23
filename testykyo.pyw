import tkinter as tk
from tkinter import ttk

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Participant Data Collection")
        self.geometry("600x400")
        self.row_count = 0

        # Column titles
        ttk.Label(self, text="Participant ID").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self, text="Start").grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self, text="Stop").grid(row=0, column=2, padx=10, pady=5)

        # Row container for participants
        self.rows_frame = ttk.Frame(self)
        self.rows_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Add Row Button
        add_btn = ttk.Button(self, text="Add Participant", command=self.add_row)
        add_btn.grid(row=2, column=0, columnspan=3, pady=10)

    def add_row(self):
        row = self.row_count
        entry = ttk.Entry(self.rows_frame)
        entry.grid(row=row, column=0, padx=10, pady=5)

        start_btn = ttk.Button(self.rows_frame, text="Start", command=lambda r=row: self.start_recording(r))
        start_btn.grid(row=row, column=1, padx=10, pady=5)

        stop_btn = ttk.Button(self.rows_frame, text="Stop", command=lambda r=row: self.stop_recording(r))
        stop_btn.grid(row=row, column=2, padx=10, pady=5)

        self.row_count += 1

    def start_recording(self, row):
        print(f"Start recording for row {row}")

    def stop_recording(self, row):
        print(f"Stop recording for row {row}")

if __name__ == "__main__":
    app = GUI()
    app.mainloop()