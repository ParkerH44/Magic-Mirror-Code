import tkinter as tk
from datetime import datetime
import requests
from gpiozero import Button

# Initialize button connected to GPIO pin 17
button = Button(17)


class ClockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.config(cursor="none")
        self.root.title("Black Clock Window")
        self.root.configure(bg="black")
        self.root.attributes('-fullscreen', True)

        self.darkscreen = True
        self.button_was_pressed = False


        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # MAIN FRAME (optional container)
        self.main_frame = tk.Frame(self.root, bg="black", width=screen_width, height=screen_height)
        self.main_frame.place(x=0, y=0)

        # Time Label - Top Left
        self.label = tk.Label(
            self.main_frame,
            font=("Roboto", 48),
            fg="white",
            bg="black",
            anchor="nw",
            justify="left"
        )
        self.label.place(x=50, y=50)
        
        self.todo_title = tk.Label(
        self.main_frame,
        text="Reminders",
        fg="white",
        bg="black",
        font=("Roboto", 28, "bold"),
        anchor="nw",
        justify="left"
        )
        self.todo_title.place(x=50, y=250)

        # Tasks Label - Below Time
        self.todo_label = tk.Label(
            self.main_frame,
            text="Fetching tasks...",
            fg="white",
            bg="black",
            font=("Roboto", 24),
            justify="left",
            anchor="nw",
            wraplength=screen_width // 2
        )
        self.todo_label.place(x=50, y=300)

        # Weather Label - Top Right
        self.result_label = tk.Label(
            self.main_frame,
            font=("Roboto", 48),
            fg="white",
            bg="black",
            anchor="ne",
            justify="right"
        )
        self.result_label.place(x=screen_width - 50, y=50, anchor="ne")

        # News Label - Bottom Middle
        self.news_label = tk.Label(
            self.main_frame,
            text="Fetching news...",
            fg="white",
            bg="black",
            font=("Roboto", 24),
            justify="center",
            wraplength=screen_width - 100
        )
        self.news_label.place(x=screen_width // 2, y=screen_height - 100, anchor="s")




        self.update_todoist()
        self.update_news()
        self.update_clock()
        self.update_weather()

        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Begin button monitoring
        self.check_button_press()

        self.root.mainloop()

    def check_button_press(self):
        if button.is_pressed:
            if not self.button_was_pressed:  # Just pressed
                self.darkscreen = not self.darkscreen
                self.toggle_display()
                self.button_was_pressed = True
        else:
            self.button_was_pressed = False  # Reset when released

        self.root.after(100, self.check_button_press)

    def toggle_display(self):
        widgets = [self.label, self.result_label, self.news_label, self.todo_label, self.todo_title]
        if self.darkscreen:
            for widget in widgets:
                widget.place_forget()
        else:
            self.label.place(x=50, y=50)
            self.todo_title.place(x=50, y=250)
            self.todo_label.place(x=50, y=300)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.result_label.place(x=screen_width - 50, y=50, anchor="ne")
            self.news_label.place(x=screen_width // 2, y=screen_height - 100, anchor="s")
    
    def get_weather(self, city):
        api_key = "enter api key here"  # Replace with your actual API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            weather = data['weather'][0]
            temp = main['temp']
            humidity = main['humidity']
            description = weather['description']
            return temp, humidity, description
        else:
            return None, None, "City not found"


    def update_clock(self):
        now = datetime.now()
        day_of_week = now.strftime("%A")
        date_str = f"{day_of_week} {now.strftime('%B')} {now.day}, {now.year}"
        
        # Manually format the hour to remove leading zero
        hour = now.hour % 12
        hour = 12 if hour == 0 else hour  # handle midnight/noon
        time_str = f"{hour}:{now.strftime('%M:%S %p ')}"
        
        self.label.config(text=f"{date_str}\n{time_str}")
        self.root.after(1000, self.update_clock)
        
        
    def update_weather(self):
        #self.city = self.city_entry.get()
        #print(self.city)
        temp, humidity, description = self.get_weather("Polson")
        
        if temp is not None:
            self.result_label.config(text=f"Polson\n {temp:.0f}°F\n {humidity}% Humidity\n {description.capitalize()}")
        else:
            self.result_label.config(text=f"Error: {description}")
        self.root.after(3600000, self.update_weather)
    
    
    def get_news(self):
        news_api_key = "enter api key here"

        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={news_api_key}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json()["articles"]
                headlines = [article.get("title", "") for article in articles if article.get("title")]
                return "\n\n".join(headlines[:3])
            else:
                return "Failed to fetch news."
        except Exception as e:
            return f"Error: {str(e)}"
        
        
    def update_news(self):
        headlines = self.get_news()
        self.news_label.config(text=headlines)
        self.root.after(3600000, self.update_news)  # Update every hour
        
        
    def get_todoist_tasks(self):
        api_token = "enter api key here"  # Replace with your actual Todoist API token
        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        # Step 1: Get list of projects and find "MagicMirror"
        projects_url = "https://api.todoist.com/rest/v2/projects"
        try:
            projects_response = requests.get(projects_url, headers=headers)
            if projects_response.status_code != 200:
                return "Failed to fetch projects."

            projects = projects_response.json()
            magic_mirror_project = next((p for p in projects if p['name'].lower() == 'magicmirror'), None)

            if not magic_mirror_project:
                return "Project 'MagicMirror' not found."

            project_id = magic_mirror_project['id']

            # Step 2: Fetch tasks from the specific project
            tasks_url = f"https://api.todoist.com/rest/v2/tasks?project_id={project_id}"
            tasks_response = requests.get(tasks_url, headers=headers)
            if tasks_response.status_code != 200:
                return "Failed to fetch tasks."

            tasks = tasks_response.json()

            if not tasks:
                return "No tasks to do"

            return "\n".join([f"• {task['content']}" for task in tasks])

        except Exception as e:
            return f"Error: {str(e)}"


    def update_todoist(self):
        tasks_text = self.get_todoist_tasks()
        self.todo_label.config(text=tasks_text)
        self.root.after(60000, self.update_todoist)  # Update every minute

ClockApp()
