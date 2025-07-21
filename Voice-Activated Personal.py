pip install pyttsx3 SpeechRecognition requests NewsAPI-python plyer

import speech_recognition as sr
import pyttsx3
import datetime
import requests
import time
from newsapi import NewsApiClient
from plyer import notification

NEWS_API_KEY = "4f7d23b80d0b49e5b1d7ac7c2d9e4cde"
WEATHER_API_KEY = "b6907d289e10d714a6e88b30761fae22"
CITY = 'PUNE'

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 175)

listener = sr.Recognizer()

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source, phrase_time_limit=5)
            command = listener.recognize_google(voice)
            print(f"You said: {command}")
            return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, the speech service is unavailable.")
        return ""

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            speak("Could not get the weather right now.")
            return
        temp = response["main"]["temp"]
        description = response["weather"][0]["description"]
        speak(f"The temperature in {CITY} is {temp} degrees Celsius with {description}.")
    except Exception as e:
        speak("Failed to retrieve weather.")
        print("Weather Error:", e)

def read_news():
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        headlines = newsapi.get_top_headlines(language='en', country='in')
        articles = headlines.get('articles', [])[:5]
        if not articles:
            speak("I couldn't find any news.")
            return
        speak("Here are the top news headlines:")
        for i, article in enumerate(articles, 1):
            speak(f"{i}. {article['title']}")
    except Exception as e:
        speak("Unable to fetch news right now.")
        print("News Error:", e)

def set_reminder(message, delay_seconds):
    speak(f"Setting reminder: {message}")
    time.sleep(delay_seconds)
    speak(f"Reminder: {message}")
    notification.notify(
        title="Reminder",
        message=message,
        timeout=10
    )

def parse_time_to_seconds(time_str):
    try:
        parts = time_str.split()
        number = int(parts[0])
        unit = parts[1]
        if "minute" in unit:
            return number * 60
        elif "second" in unit:
            return number
        elif "hour" in unit:
            return number * 3600
        else:
            return 60
    except Exception as e:
        print("Time Parse Error:", e)
        return 60

def run_assistant():
    speak("Hi, I am your assistant. What would you like to do?")
    while True:
        command = listen()

        if not command:
            continue

        elif "weather" in command:
            get_weather()

        elif "news" in command:
            read_news()

        elif "remind me" in command or "set reminder" in command:
            speak("What should I remind you about?")
            message = listen()
            speak("In how much time? For example: say '1 minute' or '10 seconds'")
            time_str = listen()
            delay = parse_time_to_seconds(time_str)
            set_reminder(message, delay)

        elif "time" in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            speak(f"The time is {current_time}")
        
        elif "exit" in command or "stop" in command or "quit" in command:
            speak("Goodbye!")
            break

        else:
            speak("Sorry, I didn't understand that.")

if __name__ == "__main__":
    run_assistant()

