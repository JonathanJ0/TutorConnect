from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from web3 import Web3
import os
import random
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Blockchain setup
w3 = Web3(Web3.HTTPProvider('https://rpc.open-campus-codex.gelato.digital'))
contract_address = '0x97E4751e69E51a764f4F96412B00e2adADbB6EA3'  # From Remix
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_sessionId",
				"type": "uint256"
			}
		],
		"name": "completeSession",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_tutor",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_subject",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_payment",
				"type": "uint256"
			}
		],
		"name": "createSession",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "sessionId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "payment",
				"type": "uint256"
			}
		],
		"name": "SessionCompleted",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "sessionId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "tutor",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "learner",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "subject",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "payment",
				"type": "uint256"
			}
		],
		"name": "SessionCreated",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "sessionCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "sessions",
		"outputs": [
			{
				"internalType": "address",
				"name": "tutor",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "learner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "subject",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "payment",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "completed",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]  # From Remix
tutoring_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

score_contract_address = '0xbe7294900463A7eA163dfd148F6b2446176a17c9'  # Replace with your deployed address
score_contract_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_user",
				"type": "address"
			}
		],
		"name": "getScore",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "scores",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_score",
				"type": "uint256"
			}
		],
		"name": "updateScore",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
] 
score_contract = w3.eth.contract(address=score_contract_address, abi=score_contract_abi)

account = '0x39453e69dB0144028dCa360D3Bf2B4F5fe81521A'  # MetaMask
private_key = '2a9ee4270c8faa7c1453a836fcc8f4951b08b6467f6adb4d5a5a2dbb5042b85a'  # MetaMask

reward_contract_address = 'YOUR_REWARD_CONTRACT_ADDRESS'
reward_contract_abi = [...]  # From Remix
reward_contract = w3.eth.contract(address=reward_contract_address, abi=reward_contract_abi)


# LangChain-Groq setup
llm = ChatGroq(
    groq_api_key=os.getenv('GROQ_API_KEY'),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful tutor creating quiz questions. Generate a simple quiz question for a student in the subject of {subject}. Provide the question and the correct answer in the format: 'Question: [question] Answer: [answer]'"),
    ("user", "Generate a quiz question for {subject}")
])
chain = prompt | llm | StrOutputParser()

# In-memory user storage
users = []

# Static questions (fallback)
static_questions = [
    {"q": "What's 2+2?", "a": "4", "subject": "Math"},
    {"q": "What's the capital of France?", "a": "Paris", "subject": "Geography"},
    {"q": "What's Python?", "a": "A programming language", "subject": "Science"}
]

# Generate quiz question using LangChain-Groq
def generate_quiz_question(subject):
    try:
        result = chain.invoke({"subject": subject})
        question_part = result.split("Answer:")[0].replace("Question:", "").strip()
        answer_part = result.split("Answer:")[1].strip()
        return {"q": question_part, "a": answer_part, "subject": subject}
    except Exception as e:
        print(f"Error generating question: {e}")
        subject_questions = [q for q in static_questions if q['subject'] == subject]
        return random.choice(subject_questions) if subject_questions else None

# Existing routes (abridged)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        address = request.form['address']
        subjects = request.form['subjects'].split(',')
        availability = request.form['availability']
        users.append({'role': role, 'address': address, 'subjects': subjects, 'availability': availability})
        return render_template('register.html', message="Registration successful!")
    return render_template('register.html')

@app.route('/match', methods=['GET', 'POST'])
def match():
    if request.method == 'POST':
        learner_subjects = request.form['subjects'].split(',')
        learner_availability = request.form['availability']
        for user in users:
            if user['role'] == 'tutor':
                if any(subject in user['subjects'] for subject in learner_subjects) and user['availability'] == learner_availability:
                    return render_template('match.html', tutor=user['address'], subjects=learner_subjects, availability=learner_availability)
        return render_template('match.html', message="No matching tutor found.")
    return render_template('match.html')

@app.route('/create_session', methods=['POST'])
def create_session():
    tutor_address = request.form['tutor']
    subject = request.form['subject']
    payment = int(request.form['payment'])
    nonce = w3.eth.get_transaction_count(account)
    tx = tutoring_contract.functions.createSession(tutor_address, subject, payment).build_transaction({
        'from': account, 'nonce': nonce, 'value': payment, 'gas': 200000, 'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return render_template('session.html', tx_hash=tx_hash.hex())

# Quiz routes
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    subjects = ["Math", "Geography", "Science"]
    if request.method == 'POST':
        subject = request.form['subject']
        question_data = generate_quiz_question(subject)
        if not question_data:
            return render_template('quiz.html', subjects=subjects, message="No quizzes available for this subject.")
        return render_template('quiz.html', subjects=subjects, question=question_data['q'], subject=subject, answer=question_data['a'])
    return render_template('quiz.html', subjects=subjects)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    user_answer = request.form['answer']
    question = request.form['question']
    correct_answer = request.form['correct_answer']
    subject = request.form['subject']
    result = "Correct!" if user_answer.lower() == correct_answer.lower() else "Wrong!"
    score = 1 if result == "Correct!" else 0

    # Log score on blockchain
    nonce = w3.eth.get_transaction_count(account)
    tx = score_contract.functions.updateScore(score).build_transaction({
        'from': account, 'nonce': nonce, 'gas': 200000, 'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Distribute reward if score is positive
    reward_tx_hash = None
    if score > 0:
        nonce = w3.eth.get_transaction_count(account)
        reward_tx = reward_contract.functions.rewardStudent(account, score).build_transaction({
            'from': account, 'nonce': nonce, 'gas': 200000, 'gasPrice': w3.to_wei('50', 'gwei')
        })
        signed_reward_tx = w3.eth.account.sign_transaction(reward_tx, private_key)
        reward_tx_hash = w3.eth.send_raw_transaction(signed_reward_tx.raw_transaction)

    # Get token balance
    token_balance = reward_contract.functions.getBalance(account).call()

    return render_template('quiz_result.html', result=result, score=score, tx_hash=tx_hash.hex(), reward_tx_hash=reward_tx_hash.hex() if reward_tx_hash else None, token_balance=token_balance, subject=subject)

# Add new API endpoints
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    try:
        sessions = []
        session_count = tutoring_contract.functions.sessionCount().call()
        for i in range(session_count):
            session = tutoring_contract.functions.sessions(i).call()
            sessions.append({
                'id': i,
                'tutor': session[0],
                'learner': session[1],
                'subject': session[2],
                'payment': session[3],
                'completed': session[4]
            })
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        data = request.json
        tutor = data.get('tutor')
        subject = data.get('subject')
        payment = data.get('payment')
        
        # Create session on blockchain
        tx_hash = tutoring_contract.functions.createSession(
            tutor, subject, payment
        ).transact({'from': account, 'private_key': private_key})
        
        return jsonify({'tx_hash': tx_hash.hex()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    try:
        tx_hash = tutoring_contract.functions.completeSession(
            session_id
        ).transact({'from': account, 'private_key': private_key})
        
        return jsonify({'tx_hash': tx_hash.hex()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        subject = data.get('subject')
        difficulty = data.get('difficulty', 'medium')
        
        # Generate quiz using AI
        prompt = f"Generate a {difficulty} difficulty quiz about {subject}"
        response = llm.invoke(prompt)
        
        return jsonify({'quiz': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)