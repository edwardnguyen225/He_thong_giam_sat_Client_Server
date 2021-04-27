import tkinter as tk


def populate_list():
    print("Populate")


def search():
    print("Search")


def clear():
    print("Clear")


class MainApplication(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("Server Manager")
        self.geometry("1240x520")

        # Device name
        self.name_text = tk.StringVar()
        self.name_label = tk.Label(
            self, text="Device Name", font=("bold", 14), pady=16)
        self.name_label.grid(row=0, column=0, sticky=tk.W)
        self.name_entry = tk.Entry(
            self, textvariable=self.name_text, width=32, font=14)
        self.name_entry.grid(row=0, column=1)

        # Device IP
        self.ip_text = tk.StringVar()
        self.ip_label = tk.Label(self, text="Device IP", font=("bold", 14))
        self.ip_label.grid(row=0, column=2, sticky=tk.W, padx=(24, 0))
        self.ip_entry = tk.Entry(
            self, textvariable=self.ip_text, width=24, font=14)
        self.ip_entry.grid(row=0, column=3)

        # Report list
        self.report_list = tk.Listbox(
            self, height=21, width=120, border=0, font=12)
        self.report_list.grid(row=2, column=0, columnspan=10,
                              rowspan=6, pady=16, padx=16)

        # Create scrollbar
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=2, column=9)
        # Set scroll to Listbox
        self.report_list.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.report_list.yview)

        # Buttons
        self.search_btn = tk.Button(
            self, text="Search", width=12, command=search)
        self.search_btn.grid(row=1, column=0)

        self.clear_btn = tk.Button(self, text="Clear search",
                                   width=12, command=clear)
        self.clear_btn.grid(row=1, column=1)


def main():
    app = MainApplication(None)
    app.mainloop()


if __name__ == "__main__":
    main()
