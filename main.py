
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import sys
from AppOpener import open as app_open
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initialize the pyttsx3 engine
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    else:
        engine.setProperty('voice', voices[0].id)
except Exception as e:
    print(f"Error initializing text-to-speech engine: {e}")
    engine = None

def speak(audio):
    """Speaks the audio string passed to it."""
    if engine:
        print(f"Sofia: {audio}")
        engine.say(audio)
        engine.runAndWait()
    else:
        print(f"Sofia: {audio}")



def process_query(query):
    """Processes the specified query and returns a text response."""
    # Web Speech API adds capitalization and periods. Clean it up.
    import string
    query = query.lower().strip()
    query = query.translate(str.maketrans('', '', string.punctuation)).strip()
    
    response = "I did not understand that command."

    if query == "none" or not query:
        return "Please say that again."

    elif 'wikipedia' in query:
        query = query.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(query, sentences=2)
            response = f"According to Wikipedia: {results}"
        except wikipedia.exceptions.DisambiguationError:
            response = "There are multiple results for this query. Please be more specific."
        except wikipedia.exceptions.PageError:
            response = "I could not find a page for that query."
        except Exception:
            response = "An error occurred while searching Wikipedia."

    elif query.startswith('play '):
        song = query.replace('play ', '').strip()
        response = f"Playing {song} on YouTube..."
        import urllib.parse
        search_query = urllib.parse.quote(song)
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")


    elif query.startswith('open '):
        target = query.replace('open ', '', 1).strip()
        
        # 1. Hardcoded popular sites/apps
        if target in ['google', 'youtube']:
            response = f"Opening {target.title()}..."
            webbrowser.open(f"https://{target}.com")
        elif 'gpt' in target or 'chatgpt' in target:
            response = "Opening ChatGPT..."
            webbrowser.open("https://chatgpt.com")
        elif target == 'camera':
            response = "Opening the camera..."
            speak(response)
            try:
                app_open("camera", match_closest=True)
            except Exception:
                os.system("start microsoft.windows.camera:")
        else:
            # 2. Try opening as an installed application
            response = f"Attempting to open {target}..."
            speak(response)
            try:
                # Some AppOpener versions don't throw, we will assume it attempts it
                app_open(target, match_closest=True)
                response = f"Executed open command for {target}."
            except Exception:
                pass
                
            # Note: Because AppOpener might not throw an exception on failure in all versions, 
            # we also do a quick targeted file search if they explicitly use the word "file" 
            # or if we want to fallback. To avoid freezing the system for 10 seconds every time 
            # AppOpener fails, we only search files if they say 'file' or if it looks like a filename.
            if 'file' in query or '.' in target:
                clean_target = target.replace('file ', '').strip()
                search_path = os.path.expanduser("~") 
                found = False
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if clean_target.lower() in file.lower():   
                            file_path = os.path.join(root, file)
                            try:
                                os.startfile(file_path)
                                response = f"Found file {file}. Opening it now."
                                found = True
                            except Exception:
                                pass
                            break
                    if found:
                        break

    elif 'the time' in query:
        str_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The time is {str_time}"

    elif 'the date' in query:
        str_date = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today's date is {str_date}"

    elif 'who are you' in query:
        response = "I am Sofia, your virtual assistant. I can help you with basic tasks like checking the time, date, searching Wikipedia, and opening websites."

    elif 'shutdown' in query or 'turn off' in query or 'sortdown' in query:
        response = "Shutting down the system. Goodbye!"
        speak(response)
        os.system("shutdown /s /t 5")
        
    elif 'restart' in query and ('system' in query or 'pc' in query or 'computer' in query):
        response = "Restarting the system..."
        speak(response)
        os.system("shutdown /r /t 5")
        
    elif 'sleep' in query and ('system' in query or 'pc' in query or 'computer' in query):
        response = "Putting the system to sleep..."
        speak(response)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    elif 'lock' in query and ('system' in query or 'pc' in query or 'computer' in query):
        response = "Locking the system..."
        speak(response)
        os.system("rundll32.exe user32.dll,LockWorkStation")
        
    elif query.startswith('close app '):
        app_name = query.replace('close app ', '').strip()
        response = f"Attempting to close {app_name}..."
        speak(response)
        os.system(f"taskkill /f /im {app_name}.exe")

    elif 'exit' in query or 'quit' in query or 'stop' in query or 'bye' in query:
        response = "Goodbye! Have a great day!"
        
    # --- Daily Work Tools (No "open" needed) ---
    elif query in ['file explorer', 'explorer', 'open file explorer', 'open explorer']:
        response = "Opening File Explorer..."
        speak(response)
        os.system("explorer")
    elif query in ['calculator', 'calc', 'open calculator']:
        response = "Opening Calculator..."
        speak(response)
        os.system("calc")
    elif query in ['notepad', 'open notepad']:
        response = "Opening Notepad..."
        speak(response)
        os.system("notepad")
    elif 'task manager' in query:
        response = "Opening Task Manager..."
        speak(response)
        os.system("taskmgr")
    elif 'settings' in query and ('open' in query or query == 'settings'):
        response = "Opening Settings..."
        speak(response)
        os.system("start ms-settings:")
        
    else:
         # Final fallback: if it's just one or two words, try opening it as an app
         if len(query.split()) <= 2:
             try:
                 app_open(query, match_closest=True)
                 response = f"Attempted to quick-launch {query}."
             except Exception:
                 response = f"I heard you say: {query}. However, I do not have a specific command for that."
         else:
             response = f"I heard you say: {query}. However, I do not have a specific command for that."

    speak(response)
    return response

# --- Flask Routes ---

from flask import send_from_directory

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sofia.ico")
def serve_icon():
    return send_from_directory(os.path.dirname(__file__), 'sofia.ico')

@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json()
    query = data.get("command", "")
    
    if not query:
        return jsonify({"response": "No command provided."})
        
    response_text = process_query(query)
    return jsonify({"response": response_text})



if __name__ == "__main__":
    print("====================================")
    print("          SOFIA WEB ASSISTANT       ")
    print("====================================")
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning! System ready.")
    elif 12 <= hour < 18:
        speak("Good Afternoon! System ready.")
    else:
        speak("Good Evening! System ready.")
        
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
