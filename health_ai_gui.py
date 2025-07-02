# health_ai_gui.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import requests
import json
import threading
import queue # Used for safe communication between threads

class HealthAIGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Health AI Assistant (IBM Granite)")
        self.geometry("700x550") # Set a default size
        self.resizable(True, True) # Allow resizing

        # Configure grid for responsive layout
        self.grid_rowconfigure(0, weight=1) # Chat area expands vertically
        self.grid_rowconfigure(1, weight=0) # Input area fixed height
        self.grid_columnconfigure(0, weight=1) # Column expands horizontally

        self.ibm_api_key = os.getenv("IBM_API_KEY")
        self.ibm_project_id = os.getenv("IBM_PROJECT_ID")
        # Ensure WATSONX_AI_ENDPOINT matches your region, default to eu-de as specified
        self.watsonx_ai_endpoint = os.getenv("WATSONX_AI_ENDPOINT", "https://eu-de.ml.cloud.ibm.com")

        self.iam_token = None # Will store the IBM IAM token

        self.setup_ui()
        self.check_env_and_authenticate()

        # Queue for AI responses to update GUI safely from background thread
        self.response_queue = queue.Queue()
        self.after(100, self.check_queue) # Check queue every 100ms

    def setup_ui(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled',
                                                    font=('Inter', 10), bg='#f0f2f5', padx=10, pady=10)
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Input frame
        input_frame = tk.Frame(self, padx=10, pady=10)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1) # Input field expands

        # User input entry
        self.user_input = tk.Text(input_frame, height=3, font=('Inter', 10), wrap=tk.WORD)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", self.on_enter_pressed) # Bind Enter key

        # Send button
        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message,
                                     font=('Inter', 10, 'bold'), bg='#3b82f6', fg='white',
                                     activebackground='#2563eb', activeforeground='white',
                                     relief=tk.RAISED, bd=2)
        self.send_button.grid(row=0, column=1, sticky="e")

        # Status label (e.g., "AI is thinking...")
        self.status_label = tk.Label(self, text="", font=('Inter', 9, 'italic'), fg='#64748b')
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))


    def check_env_and_authenticate(self):
        """Checks environment variables and attempts to get IAM token."""
        if not self.ibm_api_key or not self.ibm_project_id:
            messagebox.showerror(
                "Configuration Error",
                "IBM_API_KEY or IBM_PROJECT_ID environment variables are not set.\n"
                "Please set them in your terminal before running this script.\n"
                "Example: export IBM_API_KEY=\"...\""
            )
            self.send_button.config(state=tk.DISABLED) # Disable button if config missing
            self.user_input.config(state=tk.DISABLED)
            return

        # Start token retrieval in a separate thread to avoid freezing GUI at startup
        self.status_label.config(text="Authenticating with IBM Cloud...")
        threading.Thread(target=self._get_token_in_background, daemon=True).start()

    def _get_token_in_background(self):
        """Helper to get token and update GUI via queue."""
        token = self.get_iam_token(self.ibm_api_key)
        self.response_queue.put(('token_result', token))

    def get_iam_token(self, api_key):
        """Synchronously gets IAM token (meant to be run in a thread)."""
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"
        try:
            response = requests.post(iam_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get IBM IAM token: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nError Response: {e.response.text}"
            print(error_msg) # Print to console for debugging
            return None

    def insert_message(self, message, sender):
        """Inserts a message into the chat display."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END) # Auto-scroll to bottom

    def on_enter_pressed(self, event=None):
        """Handles Enter key press in the input field."""
        if not self.user_input.compare("end-1c", "==", "insert"): # Check if cursor is at the end
            return "break" # Allow multiline if not at end

        # If Enter is pressed and cursor is at the end, simulate send button click
        self.send_message()
        return "break" # Prevent default newline insertion after sending

    def send_message(self):
        user_query = self.user_input.get("1.0", tk.END).strip() # Get all text from Text widget
        if not user_query:
            messagebox.showinfo("Empty Input", "Please enter a health question.")
            return

        self.insert_message(user_query, "You")
        self.user_input.delete("1.0", tk.END) # Clear input field

        if not self.iam_token:
            messagebox.showerror("Authentication Error", "Not authenticated with IBM Cloud. Please restart and check environment variables.")
            return

        self.status_label.config(text="AI is thinking...")
        self.send_button.config(state=tk.DISABLED) # Disable button
        self.user_input.config(state=tk.DISABLED)   # Disable input

        # Start AI call in a separate thread
        threading.Thread(target=self._call_ai_in_background, args=(user_query,), daemon=True).start()

    def _call_ai_in_background(self, prompt):
        """Helper to call AI model and put result on queue (runs in a separate thread)."""
        ai_response = self.call_granite_model(prompt, self.iam_token, self.ibm_project_id)
        self.response_queue.put(('ai_result', ai_response))

    def check_queue(self):
        """Checks the queue for messages from background threads."""
        try:
            while True:
                message_type, data = self.response_queue.get_nowait()
                if message_type == 'token_result':
                    self.iam_token = data
                    if self.iam_token:
                        self.status_label.config(text="Authentication successful. Ready to chat!")
                        self.send_button.config(state=tk.NORMAL)
                        self.user_input.config(state=tk.NORMAL)
                        self.insert_message("Hello! I'm your Health AI Assistant (powered by IBM Granite). How can I help you today?", "AI")
                    else:
                        self.status_label.config(text="Authentication failed. Check console for errors.")
                        self.send_button.config(state=tk.DISABLED)
                        self.user_input.config(state=tk.DISABLED)
                elif message_type == 'ai_result':
                    self.insert_message(data, "AI")
                    self.status_label.config(text="")
                    self.send_button.config(state=tk.NORMAL)
                    self.user_input.config(state=tk.NORMAL)
                    self.user_input.focus_set() # Set focus back to input
                self.response_queue.task_done()
        except queue.Empty:
            pass # No messages in queue, continue checking later
        finally:
            self.after(100, self.check_queue) # Schedule next check

    def call_granite_model(self, prompt, token, project_id):
        """Synchronously calls the IBM Granite model (meant to be run in a thread)."""
        if not token:
            return "ERROR: Authentication failed. IAM token is missing or invalid."

        granite_url = f"{self.watsonx_ai_endpoint}/ml/v1-beta/generation/text?version=2023-05-29"

        system_instruction = (
            "You are a helpful and knowledgeable Health AI assistant. "
            "Your primary goal is to provide general health information and answer common health-related questions. "
            "Always advise users to consult a qualified healthcare professional for personalized medical advice, diagnosis, or treatment. "
            "DO NOT provide medical diagnoses. DO NOT act as a doctor. "
            "Respond clearly and concisely based on the health topic."
        )
        full_prompt = f"{system_instruction}\n\nUser: {prompt}\nAI:"

        payload = {
            "model_id": "ibm/granite-13b-instruct-v2", # Make sure this Model ID is valid for your Watsonx instance
            "input": full_prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 50,
                "temperature": 0.5,
                "repetition_penalty": 1.1
            },
            "project_id": project_id
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        try:
            response = requests.post(granite_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            watsonx_response = response.json()

            if "results" in watsonx_response and watsonx_response["results"]:
                generated_text = watsonx_response["results"][0].get("generated_text", "No text generated.")
                if generated_text.startswith("AI:"):
                    generated_text = generated_text[len("AI:"):].strip()
                return generated_text
            else:
                print(f"--- WARNING: Unexpected Watsonx AI response structure ---")
                print(f"Raw Response: {json.dumps(watsonx_response, indent=2)}")
                return "I received an unexpected response from IBM Watsonx AI."

        except requests.exceptions.Timeout:
            return "The request to IBM Watsonx AI timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Failed to connect to IBM Watsonx AI. Please check your internet connection."
        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred communicating with IBM Watsonx AI: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nIBM Watsonx AI Error: {e.response.text}"
            print(error_message) # Print to console for debugging
            return "An error occurred while processing your request. Check console for details."
        except Exception as e:
            print(f"--- ERROR: An unexpected error occurred in call_granite_model: {e} ---")
            return "An unexpected internal error occurred."

# --- Main Execution ---
if __name__ == "__main__":
    app = HealthAIGUI()
    app.mainloop()
