import tkinter as tk
from datetime import datetime
import requests

class ClockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Black Clock Window")

        # Make the window full screen and black background
        self.root.configure(bg="black")
        self.root.attributes('-fullscreen', True)  # Fullscreen
        
        # City Entry
        #self.city_label = tk.Label(self.root, text="Enter city name:", fg="white", bg="black",)
        #self.city_label.pack()

        #self.city_entry = tk.Entry(self.root)
        #self.city_entry.bind("<KeyPress>", self.shortcut)
        #self.city_entry.pack()

        # Frame to hold time and weather side by side
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(fill="both", expand=True)

        # TIME LABEL - LEFT SIDE
        self.label = tk.Label(
            self.top_frame,
            font=("Roboto", 48),
            fg="white",
            bg="black",
            anchor="n",
            justify="left"
        )
        self.label.pack(side="left", fill="both", expand=True, padx=50, pady=50)

        # WEATHER LABEL - RIGHT SIDE
        self.result_label = tk.Label(
            self.top_frame,
            font=("Roboto", 48),
            fg="white",
            bg="black",
            anchor="n",
            justify="right"
        )
        self.result_label.pack(side="right", fill="both", expand=True, padx=50, pady=50)

        # NEWS LABEL BELOW BOTH
        self.news_label = tk.Label(
            self.root,
            text="Fetching news...",
            fg="white",
            bg="black",
            font=("Roboto", 24),
            justify="center",
            wraplength=self.root.winfo_screenwidth() - 100
        )
        self.news_label.pack(pady=100)

        self.update_news()  # Start news updates
        
        
        
        
        self.update_clock()
        
        self.update_weather()
        # Start the clock update
        
        # Allow exiting fullscreen with Escape key
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()
    
    def get_weather(self, city):
        api_key = "db8fd169db191e8decb6156f55c6edb9"  # Replace with your actual API key
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

#     def update_clock(self):
#         now = datetime.now().strftime("%B %d, %Y \n %I:%M %p")
#         self.label.config(text=now)
#         self.root.after(1000, self.update_clock)  # update every second
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
        news_api_key = "730d002191ca462c9f97a6172bc8b170"  # Replace with your actual NewsAPI key
        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={news_api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json()["articles"]
                headlines = [f"{article['title']}" for article in articles]
                return "\n\n".join(headlines)
            else:
                return "Failed to fetch news."
        except Exception as e:
            return f"Error: {str(e)}"
        
        
    def update_news(self):
        headlines = self.get_news()
        self.news_label.config(text=headlines)
        self.root.after(3600000, self.update_news)  # Update every hour

ClockApp()

