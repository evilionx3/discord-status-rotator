import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from queue import Queue
import json

class DiscordStatusRotatingTool:
    def __init__(self, master):
        self.master = master
        master.title("Status Rotating Tool by evilionx3 <3")
        master.geometry("600x600")
        master.configure(bg='#2E003E')
        master.resizable(False, False)

        self.statuses = []
        self.delays = []
        self.running = False
        self.discord_token = ""
        self.message_queue = Queue()

        self.create_widgets()
        self.check_message_queue()

    def check_message_queue(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            if msg.startswith("ERROR:"):
                messagebox.showerror("Error", msg[6:])
            elif msg.startswith("WARNING:"):
                messagebox.showwarning("Warning", msg[8:])
        self.master.after(100, self.check_message_queue)

    def create_widgets(self):
        self.title_font = ("Arial", 24, "bold")
        self.label_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Changed to clam theme for Windows compatibility
        
        # Configure custom styles
        self.style.configure("Custom.TButton", 
                           font=self.button_font,
                           background="#D9A0D3",
                           foreground="white",
                           borderwidth=0)
        self.style.map("Custom.TButton",
                      background=[('active', '#C090B3'), ('pressed', '#B080A3')])
        
        self.style.configure("Custom.TEntry", 
                           fieldbackground="#3E1F56",
                           foreground="white")

        # Title
        self.title_label = tk.Label(
            self.master, text="Discord Status Rotator",
            font=self.title_font, bg="#2E003E", fg="#D9A0D3", pady=10
        )
        self.title_label.pack(fill=tk.X)

        # Token Entry
        self.token_frame = tk.Frame(self.master, bg="#2E003E")
        self.token_frame.pack(pady=10)

        self.token_label = tk.Label(
            self.token_frame, text="Enter Discord User Token:",
            font=self.label_font, bg="#2E003E", fg="#D9A0D3"
        )
        self.token_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.token_entry = ttk.Entry(
            self.token_frame, font=self.label_font, width=40,
            style="Custom.TEntry", show="*"
        )
        self.token_entry.grid(row=0, column=1, padx=10, pady=5)
        self.token_entry.bind('<Control-a>', self.select_all)

        # Status Input
        self.input_frame = tk.Frame(self.master, bg="#2E003E")
        self.input_frame.pack(pady=10)

        self.status_label = tk.Label(
            self.input_frame, text="Enter your custom status:",
            font=self.label_font, bg="#2E003E", fg="#D9A0D3"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.status_entry = ttk.Entry(
            self.input_frame, font=self.label_font, width=30, style="Custom.TEntry"
        )
        self.status_entry.grid(row=0, column=1, padx=10, pady=5)
        self.status_entry.bind('<Control-a>', self.select_all)

        # Delay Input
        self.delay_label = tk.Label(
            self.input_frame, text="Enter delay in seconds:",
            font=self.label_font, bg="#2E003E", fg="#D9A0D3"
        )
        self.delay_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.delay_entry = ttk.Entry(
            self.input_frame, font=self.label_font, width=30, style="Custom.TEntry"
        )
        self.delay_entry.grid(row=1, column=1, padx=10, pady=5)
        self.delay_entry.bind('<Control-a>', self.select_all)

        # Add Button
        self.add_button = ttk.Button(
            self.input_frame, text="Add Status",
            style="Custom.TButton", command=self.add_status
        )
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Status List
        self.status_listbox_label = tk.Label(
            self.master, text="Current Statuses:",
            font=self.label_font, bg="#2E003E", fg="#D9A0D3"
        )
        self.status_listbox_label.pack(pady=5)

        # Listbox with Scrollbar
        self.listbox_frame = tk.Frame(self.master, bg="#2E003E")
        self.listbox_frame.pack(pady=5)

        self.status_listbox = tk.Listbox(
            self.listbox_frame, width=50, height=5, bg="#3E1F56",
            fg="white", font=self.label_font, bd=0, highlightthickness=0
        )
        self.status_listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.listbox_frame, orient="vertical", command=self.status_listbox.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.status_listbox.config(yscrollcommand=self.scrollbar.set)
        self.status_listbox.bind("<Button-3>", self.show_popup_menu)
        self.status_listbox.bind('<ButtonPress-1>', self.on_drag_start)
        self.status_listbox.bind('<ButtonRelease-1>', self.on_drag_end)

        # Config Buttons
        self.config_frame = tk.Frame(self.master, bg="#2E003E")
        self.config_frame.pack(pady=10)

        self.save_button = ttk.Button(
            self.config_frame, text="Save Config",
            style="Custom.TButton", command=self.save_config
        )
        self.save_button.grid(row=0, column=0, padx=10)

        self.load_button = ttk.Button(
            self.config_frame, text="Load Config",
            style="Custom.TButton", command=self.load_config
        )
        self.load_button.grid(row=0, column=1, padx=10)

        # Clear Button
        self.clear_button = ttk.Button(
            self.config_frame, text="Clear",
            style="Custom.TButton", command=self.confirm_clear
        )
        self.clear_button.grid(row=0, column=2, padx=10)

        # Control Buttons
        self.button_frame = tk.Frame(self.master, bg="#2E003E")
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            self.button_frame, text="Start",
            style="Custom.TButton", command=self.start_rotating
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(
            self.button_frame, text="Stop",
            style="Custom.TButton", command=self.stop_rotating
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        # Status Indicator
        self.running_label = tk.Label(
            self.master, text="Status: Not Running",
            font=self.label_font, bg="#2E003E", fg="#FF5050"
        )
        self.running_label.pack(pady=10)

        # Popup Menu
        self.popup_menu = tk.Menu(self.master, tearoff=0, bg="#3E1F56", fg="white")
        self.popup_menu.add_command(label="Delete Status", command=self.delete_status)
        self.popup_menu.add_command(label="Edit Status", command=self.edit_status)

    def select_all(self, event):
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
        return 'break'

    def add_status(self):
        status = self.status_entry.get()
        delay = self.delay_entry.get()

        if status and delay.isdigit() and int(delay) > 0:
            self.statuses.append(status)
            self.delays.append(int(delay))
            self.status_listbox.insert(tk.END, f"{status} (Delay: {delay} sec)")
            self.status_entry.delete(0, tk.END)
            self.delay_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter valid status and positive delay in seconds.")

    def show_popup_menu(self, event):
        index = self.status_listbox.nearest(event.y)
        if index >= 0 and index < self.status_listbox.size():
            self.status_listbox.select_clear(0, tk.END)
            self.status_listbox.select_set(index)
            self.popup_menu.post(event.x_root, event.y_root)

    def delete_status(self):
        selected_index = self.status_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            self.status_listbox.delete(selected_index)
            del self.statuses[selected_index]
            del self.delays[selected_index]

    def edit_status(self):
        selected_index = self.status_listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        current_status = self.statuses[index]
        current_delay = self.delays[index]
        
        self.edit_window = tk.Toplevel(self.master)
        self.edit_window.title("Edit Status")
        self.edit_window.grab_set()
        
        # Status
        tk.Label(self.edit_window, text="Status:").grid(row=0, column=0, padx=5, pady=5)
        status_entry = ttk.Entry(self.edit_window, width=30)
        status_entry.grid(row=0, column=1, padx=5, pady=5)
        status_entry.insert(0, current_status)
        
        # Delay
        tk.Label(self.edit_window, text="Delay (seconds):").grid(row=1, column=0, padx=5, pady=5)
        delay_entry = ttk.Entry(self.edit_window, width=30)
        delay_entry.grid(row=1, column=1, padx=5, pady=5)
        delay_entry.insert(0, str(current_delay))
        
        # Save Button
        save_button = ttk.Button(
            self.edit_window, text="Save",
            command=lambda: self.save_edited_status(index, status_entry.get(), delay_entry.get())
        )
        save_button.grid(row=2, column=0, columnspan=2, pady=5)

    def save_edited_status(self, index, new_status, new_delay):
        if not new_status:
            messagebox.showwarning("Input Error", "Status cannot be empty.")
            return
        if not new_delay.isdigit() or int(new_delay) <= 0:
            messagebox.showwarning("Input Error", "Delay must be a positive integer.")
            return
        
        self.statuses[index] = new_status
        self.delays[index] = int(new_delay)
        self.status_listbox.delete(index)
        self.status_listbox.insert(index, f"{new_status} (Delay: {new_delay} sec)")
        self.edit_window.destroy()

    def on_drag_start(self, event):
        index = self.status_listbox.nearest(event.y)
        if index >= 0:
            self.drag_start_index = index

    def on_drag_end(self, event):
        if hasattr(self, 'drag_start_index'):
            end_index = self.status_listbox.nearest(event.y)
            if end_index >= 0 and end_index != self.drag_start_index:
                self.move_item(self.drag_start_index, end_index)
            del self.drag_start_index

    def move_item(self, start_index, end_index):
        # Move in Listbox
        item_text = self.status_listbox.get(start_index)
        self.status_listbox.delete(start_index)
        self.status_listbox.insert(end_index, item_text)
        
        # Move in statuses and delays
        status = self.statuses.pop(start_index)
        delay = self.delays.pop(start_index)
        self.statuses.insert(end_index, status)
        self.delays.insert(end_index, delay)
        
        # Update selection
        self.status_listbox.selection_clear(0, tk.END)
        self.status_listbox.selection_set(end_index)

    def start_rotating(self):
        if not self.running and self.statuses:
            self.discord_token = self.token_entry.get().strip()
            if not self.discord_token:
                messagebox.showwarning("Input Error", "Please enter your Discord user token.")
                return

            self.running = True
            self.running_label.config(text="Status: Running", fg="#50FF50")
            threading.Thread(target=self.rotation_loop, daemon=True).start()

    def stop_rotating(self):
        self.running = False
        self.running_label.config(text="Status: Not Running", fg="#FF5050")
        threading.Thread(target=self.clear_status, daemon=True).start()

    def clear_status(self):
        if self.discord_token:
            self.send_status("")

    def rotation_loop(self):
        while self.running:
            for i in range(len(self.statuses)):
                if not self.running:
                    return
                status = self.statuses[i]
                delay = self.delays[i]
                self.send_status(status)
                start_time = time.time()
                while time.time() - start_time < delay and self.running:
                    time.sleep(0.1)

    def send_status(self, status):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Authorization': self.discord_token,
            'Origin': 'https://discord.com',
            'Connection': 'keep-alive',
            'Referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        json_data = {
            'custom_status': {
                'text': status
            }
        }

        try:
            response = requests.patch(
                'https://discord.com/api/v9/users/@me/settings',
                headers=headers,
                json=json_data
            )
            if response.status_code == 429:
                retry_after = response.json().get('retry_after', 1)
                time.sleep(retry_after)
                response = requests.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers=headers,
                    json=json_data
                )
            if response.status_code not in (200, 204):
                self.message_queue.put(f"ERROR: Failed to set status: {response.text}")
                self.stop_rotating()
        except Exception as e:
            self.message_queue.put(f"ERROR: Request failed: {str(e)}")
            self.stop_rotating()

    def save_config(self):
        config = {
            "statuses": self.statuses,
            "delays": self.delays
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="discord_status_config.json"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                messagebox.showinfo("Success", "Configuration saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {str(e)}")

    def load_config(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)

                self.statuses.clear()
                self.delays.clear()
                self.status_listbox.delete(0, tk.END)

                for status, delay in zip(config["statuses"], config["delays"]):
                    self.statuses.append(status)
                    self.delays.append(delay)
                    self.status_listbox.insert(tk.END, f"{status} (Delay: {delay} sec)")

                messagebox.showinfo("Success", "Configuration loaded successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Invalid config file: {str(e)}")

    def confirm_clear(self):
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear all statuses and delays?"
        )
        if confirm:
            self.clear_all()

    def clear_all(self):
        # Clear statuses and delays
        self.statuses.clear()
        self.delays.clear()

        # Clear the listbox
        self.status_listbox.delete(0, tk.END)

        # Clear the status and delay entry fields
        self.status_entry.delete(0, tk.END)
        self.delay_entry.delete(0, tk.END)

        # Show confirmation message
        messagebox.showinfo("Cleared", "All statuses and delays have been cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordStatusRotatingTool(root)
    root.mainloop()