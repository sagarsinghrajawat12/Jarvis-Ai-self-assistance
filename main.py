import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import google.generativeai as genai
import os
import subprocess
import json
import fnmatch


# Set up Gemini API
GEMINI_API_KEY = "AIzaSyDSsDGFKSe2gAJa1RbO01EsCxOrBGzW-CQ"
genai.configure(api_key=GEMINI_API_KEY)

# WeatherAPI.com (Free API Key required)
WEATHER_API_KEY = "271e6f0c33db4d5bac4102257250203"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

# Initialize speech engine
r = sr.Recognizer()
engine = pyttsx3.init()

# News API
NEWS_API_KEY = "efc697e2a9dc4fc6bc10679b0e271a6c"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# Dictionary of music links
music = {
    "afsos": "https://youtu.be/2FhgKp_lfJQ?si=DM39iVkbdgzl7A5E",
    "bulleya": "https://youtu.be/_51KXfwcPMs?si=F-0i8K2K8_nqGJ-r",
    "enjoy": "https://youtu.be/9XXGCb4Eev8?si=U7l5YsdgA3xsj1IY",
    "zimedari": "https://youtu.be/eJCK2E6ocT0?si=O8SVvLtmW60iSMnC",
    "SAUDEBAZI" :    "https://youtu.be/W4sHmzMCo8s?si=OSG66BWHU7E9d6zy",
    "Katto Gilehri" :   "https://youtu.be/KAkATnYbpbs?si=4k63_zGbLQ_kYAwe",
    "Laila Main Laila" : "https://youtu.be/jE4-tKSYScQ?si=HUhOHwJky3X1akBa",
    "Afghan Jalebi" :  "https://youtu.be/zC3UbTf4qrM?si=HtVYWV7NRXnLo1EM",
    "Hookah Bar" :    "https://youtu.be/b4b1cMVZOUU?si=-BygN8meQuSZn5C8",
    "Dupatta Tera" : "https://youtu.be/W2mjfazc9eM?si=zpCU_bA2ZCroCXUz",
    "Yeh Dil Deewana"  : "https://youtu.be/_4Ft9UIKzwk?si=ZTBATfGq8m3wSap6",
    "Ghagra"     :     "https://youtu.be/caoGNx1LF2Q?si=acLe61gVcehaz5iW",
    "TERE MAST"  : "https://youtu.be/QWaXpiQwtpI?si=7VNi9qNwTpcu7pJp"


}

# File to store recently opened files
MEMORY_FILE = "recent_files.json"

# Function to speak output
def speak(text):
    engine.say(text)
    engine.runAndWait()

#saying developer name 
def teller():
    speak("i am developed by sagar singh")
    

# Load recent file memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

# Save memory back to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# Search for a file or folder anywhere on PC
def find_path(name, search_directory="C:\\"):
    for root, dirs, files in os.walk(search_directory):  
        for filename in files:
            if fnmatch.fnmatch(filename.lower(), f"*{name.lower()}*"):
                return os.path.join(root, filename)
        for dirname in dirs:
            if fnmatch.fnmatch(dirname.lower(), f"*{name.lower()}*"):
                return os.path.join(root, dirname)
    return None  # Return None if not found

# Open a file or folder with memory check
def open_file_or_folder(name):
    memory = load_memory()
    
    # Check if the file is already in memory
    if name in memory:
        path = memory[name]
        if os.path.exists(path):  
            subprocess.run(["start", "", path], shell=True)
            return f"Opening {name} from memory."
        else:
            del memory[name]  # Remove invalid entry
            save_memory(memory)
    
    # If not found in memory, search the PC
    path = find_path(name)
    
    if path:
        memory[name] = path  # Save found path to memory
        save_memory(memory)
        subprocess.run(["start", "", path], shell=True)
        return f"Opening {name}."
    else:
        return "File or folder not found."
# Function to get weather updates
def get_weather(city):
    params = {
        "key": WEATHER_API_KEY,
        "q": city,
        "aqi": "yes"  # Disable air quality index to keep it simple
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()

    if "current" in data:
        weather = data["current"]
        temp = weather["temp_c"]
        condition = weather["condition"]["text"]
        return f"The weather in {city} is {condition} with a temperature of {temp}°C."
    else:
        return "Could not fetch weather data. Please check the city name."

# Function to fetch and speak news headlines
def get_news():
    params = {"apiKey": NEWS_API_KEY, "country": "us", "category": "general"}
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()

    if "articles" in data:
        headlines = [article["title"] for article in data["articles"][:5]]  # Get top 5 news headlines
        news_report = "Here are the latest news headlines: " + " ... ".join(headlines)
        return news_report
    else:
        return "Sorry, I couldn't fetch the news at the moment."
    
# Function to confirm and execute system commands
def confirm_and_execute(command, action):
    speak(f"Are you sure you want to {action}? Say 'ok' to proceed or 'no' to cancel.")
    speak(f"Are you sure you want to {action}? Say 'ok' to proceed or 'no' to cancel.")
    print(f"Are you sure you want to {action}? (ok/no)")
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            confirmation = r.recognize_google(audio).lower()
            if confirmation == "ok":
                speak(f"Proceeding to {action}.")
                os.system(command)
            else:
                speak(f"{action.capitalize()} cancelled.")
        except sr.UnknownValueError:
            speak("I didn't understand. Cancelling operation.")
        except sr.RequestError:
            speak("Could not process request. Cancelling operation.")

# Function to process user commands using Gemini API
def processCommand(command):
    command = command.lower()  # Convert to lowercase for consistency

    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open facebook" in command:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "open pandit ji" in command:
        speak("opening pandit ji ki chut")
        webbrowser.open("https://xhamster1.desi/search/xhamester+desi+porn?page=8")

    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")

    elif command.startswith("play "):  # Check if command starts with "play"
        song_name = command.split("play ", 1)[1].strip().lower()
        music_lower = {key.lower(): value for key, value in music.items()}  # Extract song name
        if song_name in music_lower:
            speak(f"Playing {song_name}")
            webbrowser.open(music_lower[song_name])
        else:
            speak("Sorry, this song is not in the library.")

    elif "what's the weather in" in command or "what is the weather in" in command  or "tell me weather condtion in" in command  or "current weather " in command:
        city = command.split("in")[-1].strip()
        weather_info = get_weather(city)
        speak(weather_info)

    elif "tell me the news" in command or "what's the news" in command:
        news_info = get_news()
        speak(news_info)

    elif command.startswith("open "):  # Open a file or folder
        item = command.replace("open ", "").strip()
        response = open_file_or_folder(item)
        speak(response)

    elif "who developed you jarvis" in command or "who developed you" in command or "who is your developer" in command or "who is your developer" in command:
        teller()   

    elif "shutdown" in command:
        confirm_and_execute("shutdown /s /t 5", "shut down the system")

    elif "restart" in command:
        confirm_and_execute("shutdown /r /t 5", "restart the system")
        
    else:
        # Let Gemini generate a smart response
        speak("Thinking...")
        response = get_gemini_response(command)
        speak(response)

# Function to get response from Gemini AI
def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text  # Return AI-generated response

# Main function
if __name__ == "__main__":
    speak("Initializing jarvis....")
    print("Waiting for wake word (Jarvis)...")
    is_listening = False  # Assistant starts in listening mode

while True:
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            text = r.recognize_google(audio).lower()
            print("Heard:", text)
            if text == "jarvis":
               speak("Welcome back, sir.")
               print("Listening for command...")
               is_listening = True  # Activate listening mode

            elif text == "stop":
               speak("bye sir, call me if you need")
               is_listening = False  # Deactivate listening mode

            elif is_listening:
                processCommand(text)
                if not is_listening:
                    print("Waiting for wake word (Jarvis)...")
            else:
                print("Listening for command...") 

    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError:
        print("Could not request results, please check your internet connection.")
    except Exception as e:
        print(f"Error: {e}")

