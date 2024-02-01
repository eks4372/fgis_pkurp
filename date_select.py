import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from datetime import datetime

width = 280
height = 180


def center(win, w, h):
    """
    centers a tkinter window
    :param w: width win
    :param h: height win
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    # width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = w + 2 * frm_width
    # height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = h + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(w, h, x, y))
    win.deiconify()


def select_dates():
    def on_done():
        start_date = start_entry.get()
        end_date = end_entry.get()

        if datetime.strptime(end_date, "%d.%m.%Y") < datetime.strptime(start_date, "%d.%m.%Y"):
            messagebox.showerror("Ошибка", "Дата 'дата по' не может быть раньше даты 'дата с'.")
        else:
            root.destroy()
            selected_dates.extend([start_date, end_date])

    def on_cancel():
        root.destroy()

    selected_dates = []
    root = tk.Tk()
    root.title("Выбор дат")
    # root.geometry("400x300")
    root.geometry(f'{width}x{height}')  # размер и сдвиг в пикселях
    root.attributes('-topmost', 1)  # поверх окон

    # Поле выбора даты "дата с"
    start_label = ttk.Label(root, text="Дата с:")
    start_label.pack(pady=5)

    start_entry = DateEntry(root, width=12, background="grey",
                            date_pattern="dd.mm.yyyy", locale="ru_RU")
    start_entry.pack(pady=5)

    # Поле выбора даты "дата по"
    end_label = ttk.Label(root, text="Дата по:")
    end_label.pack(pady=5)

    end_entry = DateEntry(root, width=12, background="grey",
                          date_pattern="dd.mm.yyyy", locale="ru_RU")
    end_entry.pack(pady=5)

    # Кнопки "Готово" и "Отмена"
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    btn_done = ttk.Button(btn_frame, text="Готово", command=on_done)
    btn_done.pack(side=tk.LEFT, padx=5)

    btn_cancel = ttk.Button(btn_frame, text="Отмена", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    center(root, width, height)  # вызываем функцию центровки окна
    root.mainloop()
    return selected_dates


selected_dates = select_dates()
if __name__ == '__main__':
    if selected_dates:
        start_date, end_date = selected_dates
        print(f"Выбранные даты: {start_date} - {end_date}")
