from flask import Flask, request, jsonify, send_from_directory, session
from openai import OpenAI
import markdown
import time
import os

app = Flask(__name__, static_url_path='', static_folder='static')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure OpenAI API Key
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

# Secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure session to use filesystem (you can also use other session types)
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize session
from flask_session import Session
Session(app)

# Global variable to store the assistant ID
assistant_id = None

def initialize():
    global assistant_id
    assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    if not assistant_id:
        assistant = client.beta.assistants.create(
            instructions='''You are an assistant called "Play District chatbot" and your goal is to REFER TO THE DOCUMENTS to answer user questions in a friendly tone...''',
            model="gpt-4o-mini"
        )
        assistant_id = assistant.id

    # Create a new thread for the session
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "assistant",
                "content": "Welcome to The Play District! What city are you interested in for family events?"
            },
        ]
    )
    thread_id = thread.id  # Obtain the thread ID from the API response
    session['thread_id'] = thread_id  # Store thread ID in the session
    print(f"Thread initialized with ID: {session['thread_id']}")
    return thread_id

@app.route('/initialize', methods=['GET'])
def initialize_thread():
    if 'thread_id' not in session:
        print("No thread_id found in session; initializing a new thread.")
        initialize()  # Initialize if not already in session
    else:
        print(f"Using existing thread_id from session: {session['thread_id']}")
    return jsonify({'result': session['thread_id']})

@app.route('/chat', methods=['POST'])
def chat():
    # Retrieve thread_id from session
    thread_id = session.get('thread_id')

    if not thread_id:
        return jsonify({'error': 'Thread ID not found in session. Please refresh the page to start a new session.'}), 400

    # Process the message and thread as needed
    data = request.json
    user_message = data.get('message')

    # Add the user message to the thread
    message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=user_message,
    )

    # Generate a response from the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for the response
    runStatus = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run.id
    )
    while runStatus.status != "failed" and runStatus.status != "completed":
        print(runStatus.status)
        time.sleep(0.1)
        runStatus = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    print(runStatus.status)

    # Get the assistant's response message
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    chatbot_reply = messages.data[0].content[0].text.value
    html = markdown.markdown(chatbot_reply)
    print(html)
    return jsonify({'reply': html})

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)