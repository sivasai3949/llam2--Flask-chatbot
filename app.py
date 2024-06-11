from flask import Flask, render_template, request, session
from dotenv import load_dotenv
import os
import requests
import json

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
llm_endpoint = "https://api.replicate.ai/rpc/llm/v1/completion/complete"

# Initial questions
questions = [
    "Please provide your general information like name, city, state, country.",
    "Please provide your academic performance (grade, board, present percentage).",
    "What is your goal, financial position, and which places are you interested in?"
]

# Options to present after initial questions
options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

@app.route('/')
def home():
    session.clear()
    session['question_index'] = 0
    session['user_responses'] = []
    return render_template('chat.html', initial_question=questions[0])

@app.route('/process_chat', methods=['POST'])
def process_chat():
    user_input = request.form.get('user_input')
    if user_input:
        question_index = session.get('question_index', 0)
        if question_index < len(questions):
            session['user_responses'].append(user_input)
            question_index += 1
            session['question_index'] = question_index
            if question_index < len(questions):
                return questions[question_index]
            else:
                options_html = render_template('options.html', options=options)
                return options_html
        else:
            bot_response = get_llm_response(user_input)
            return bot_response
    return "Invalid input"

def get_llm_response(input_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    # Add all user responses
    for response in session.get('user_responses', []):
        messages.append({"role": "user", "content": response})
    
    messages.append({"role": "user", "content": input_text})
    
    headers = {
        "Authorization": "Bearer " + replicate_api_token,
        "Content-Type": "application/json"
    }

    data = {
        "prompt": messages,
        "max_tokens": 50
    }

    response = requests.post(llm_endpoint, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        bot_response = response_data['choices'][0]['text']
        return bot_response
    else:
        return "Error: Unable to generate response."

if __name__ == '__main__':
    app.run(debug=True)
