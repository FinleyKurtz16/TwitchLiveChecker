import tkinter as tk
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
import webbrowser
import os

STREAMER_FILE = "streamer_urls.txt"

class TwitchCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch Live Checker")
        
        self.streamer_urls = []
        self.live_streamers = {}

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=10)

        self.add_button = tk.Button(root, text="Add Streamer", command=self.add_streamer)
        self.add_button.pack(pady=5)

        self.url_listbox = tk.Listbox(root, width=50, height=10)
        self.url_listbox.pack(pady=10)

        self.delete_button = tk.Button(root, text="Delete Selected", command=self.delete_streamer)
        self.delete_button.pack(pady=5)

        self.interval_label = tk.Label(root, text="Check Interval (minutes):")
        self.interval_label.pack(pady=5)
        self.interval_entry = tk.Entry(root, width=5)
        self.interval_entry.pack(pady=5)
        self.interval_entry.insert(0, "5")

        self.run_button = tk.Button(root, text="Start Checking", command=self.start_checking)
        self.run_button.pack(pady=20)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.pack_forget()

        self.status_text = tk.Text(root, height=10, width=50)
        self.status_text.pack(pady=10)

        self.load_streamers()

    def add_streamer(self):
        url = self.url_entry.get()
        if url and (url.startswith("https://www.twitch.tv/") or url.startswith("https://twitch.tv/")):
            if url not in self.streamer_urls:
                self.streamer_urls.append(url)
                self.url_listbox.insert(tk.END, url)
                self.url_entry.delete(0, tk.END)
                self.save_streamers()
            else:
                messagebox.showerror("Duplicate URL", "This Twitch URL is already in the list.")
        elif url:
            full_url = "https://www.twitch.tv/" + url
            if full_url not in self.streamer_urls:
                self.streamer_urls.append(full_url)
                self.url_listbox.insert(tk.END, full_url)
                self.url_entry.delete(0, tk.END)
                self.save_streamers()
            else:
                messagebox.showerror("Duplicate URL", "This Twitch URL is already in the list.")
        else:
            messagebox.showerror("Invalid URL", "Please enter a valid Twitch URL.")

    def delete_streamer(self):
        selected_index = self.url_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            url = self.streamer_urls[index]
            del self.streamer_urls[index]
            self.url_listbox.delete(index)
            self.save_streamers()
            streamer_name = url.split('/')[-1]
            messagebox.showinfo("Streamer Deleted", f"The streamer {streamer_name} has been deleted.")
        else:
            messagebox.showerror("No Streamer Selected", "Please select a streamer to delete.")

    def start_checking(self):
        interval = self.interval_entry.get()
        try:
            interval = int(interval)
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Interval", "Please enter a valid interval in minutes.")
            return

        self.progress.pack()
        self.progress.start()
        threading.Thread(target=self.check_streamers, args=(interval,), daemon=True).start()
        self.update_status(f"Checking started. . .")
        self.update_status(f"Current information will be displayed here.")

    def check_if_live(self, driver, url):
        driver.get(url)
        try:
            wait = WebDriverWait(driver, 10)
            live_indicator = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'CoreText-sc-1txzju1-0 bfNjIO') and contains(text(), 'LIVE')]")))
            return True
        except:
            return False

    def check_streamers(self, interval):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        
        while True:
            driver = webdriver.Chrome(service=service, options=options)
            for url in self.streamer_urls:
                streamer_name = url.split('/')[-1]
                is_live = self.check_if_live(driver, url)
                if is_live and streamer_name not in self.live_streamers:
                    self.live_streamers[streamer_name] = True
                    self.update_status(f"The streamer {streamer_name} is live.")
                    webbrowser.open(url)
                elif not is_live and streamer_name in self.live_streamers:
                    self.live_streamers.pop(streamer_name)
                    self.update_status(f"The streamer {streamer_name} is not live.")
                    for handle in webbrowser._tryorder:
                        handle("about:blank")
                else:
                    self.update_status(f"The streamer {streamer_name} is {'still live' if is_live else 'not live'}.")

            driver.quit()
            time.sleep(interval * 60)

    def update_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)

    def save_streamers(self):
        with open(STREAMER_FILE, "w") as f:
            for url in self.streamer_urls:
                f.write(url + "\n")

    def load_streamers(self):
        if os.path.exists(STREAMER_FILE):
            with open(STREAMER_FILE, "r") as f:
                for line in f:
                    url = line.strip()
                    if url:
                        self.streamer_urls.append(url)
                        self.url_listbox.insert(tk.END, url)

root = tk.Tk()
app = TwitchCheckerApp(root)
root.mainloop()
