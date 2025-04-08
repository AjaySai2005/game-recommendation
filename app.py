from flask import Flask, render_template, request, redirect, session, jsonify
import openai
import secrets
from users import USERS

# Setup Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ✅ Set up OpenAI client with new SDK format
client = openai.OpenAI(api_key="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")
# Store chat history per user
chat_histories = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['user'] = username
            if username not in chat_histories:
                chat_histories[username] = []
            return redirect('/chat')
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect('/login')
    return render_template('chat.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if 'user' not in session:
        return jsonify({'reply': 'Unauthorized'}), 401

    user_input = request.json.get('message')
    username = session['user']

    # Initialize user chat history if not present
    history = chat_histories.get(username, [])

    # Format messages for OpenAI
    messages = [{"role": "system", "content": "You are a helpful assistant that recommends games."}]
    for item in history:
        messages.append({"role": "user", "content": item['user']})
        messages.append({"role": "assistant", "content": item['bot']})
    messages.append({"role": "user", "content": user_input})

    try:
        # ✅ Updated API call with new SDK (v1.0+)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        bot_reply = response.choices[0].message.content.strip()
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Save new interaction
    history.append({'user': user_input, 'bot': bot_reply})
    chat_histories[username] = history

    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
