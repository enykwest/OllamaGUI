import tkinter as tk

def remove_menu_item():
    file_menu.delete("Open")  # Removes the "Open" option
    # or
    # file_menu.delete(0) # Removes the first item in the menu

root = tk.Tk()

menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open")
file_menu.add_command(label="Save")
file_menu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=file_menu)

remove_button = tk.Button(root, text="Remove 'Open'", command=remove_menu_item)
remove_button.pack()

root.config(menu=menubar)
root.mainloop()
