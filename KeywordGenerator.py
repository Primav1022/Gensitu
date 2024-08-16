from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

API_KEY = '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'

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        return response

@app.route('/api/generate-keywords', methods=['POST'])
def gpt_request():
    data = request.json
    if data is None or 'message' not in data:
        return jsonify({'error': 'Invalid request format'}), 400
    message=data['message']
    print("这是传过来的消息",message)

    response = call_gpt_api(message)
    print("获取到的回答",response)
    association = associate_word(response, message);
    print("发散的关键词", association)
    example = example_word(association);
    print("举例的关键词", example)
    return jsonify({'responseText': response, 'associationText': association, 'exampleText': example});
 


def call_gpt_api(message_input):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

    systemMessage= '''Raw data is the data related to physical objects or spaces. Physical referent is a physical entity or a group of physical entities to which the data refers. Environment is the space and all physical entities around the immediate physical referent.
 Extract the most 3 related {keywords} from the provided design proposal's description and visual encoding, considering raw data or physical referent or environment angle. 
 Make sure to response in following format, no \n, {,} is the delimiter, only 3 keywords, capitalize the first letter: xxxxx, xxxxx, xxxxx'''
   
    message=[
        {'role':'system',
         'content': systemMessage},
        {'role':'user',
         'content': "The design proposal's description and visual encoding is" + message_input},
        ]

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': message,
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']

    else:
        print('Error calling GPT API:', response.status_code, response.text)
        return 'Error'


 # 对keyword进行发散
def associate_word(message_input, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

    # systemMessage= '''Which {character, organization, location, object, action} would you associate with given keywords? Each keyword produces 3 associations. Make sure to response in following format: keyword 1: its 3 associations\n keyword 2: its 3 associations\n.....'''
    systemMessage = '''Time means temporal perspective (when).
                        Place means paying attention to a location while breaking away from a purely spatial perspective and representational approach. A place is shaped by its history, its local identity and the meaning it has for its inhabitants (where).
                        Activity means connecting to a wider set of human activities of target audiences (what).
                        User means the audience for and/or co-creators of visualizations centered around local issues and shared concerns (who).
                        Goal means the design goal of the situated visualization (why).
                        Presentation means the way to show data and its visualization (how).

                        Take an example word museum. Its association words: student (user), education (goal), exhibition (presentation).
                        
                        Which other words would you associate with given 3 keywords in {time, place, activity, user, goal, presentation} these six dimensions? 
                        Involve as many dimensions as possible. Capitalize the first letter and say your answer in the pair format of “keyword 1: association 1 (dimension), association 2 (dimension), association 3 (dimension) \n keyword 2: association 1 (dimension), association 2 (dimension), association 3 (dimension) \n keyword 3: association 1 (dimension), association 2 (dimension), association 3 (dimension)”, i.e. 
                        Generate 3 association words for each keyword and specify the dimensions in parentheses. The answer is only three lines'''
    message=[
        {'role':'system',
         'content': 'The Design scheme:'+message+systemMessage},
        {'role':'user',
         'content': 'Keywords:'+ message_input},
        ]

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': message,
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']

    else:
        print('Error calling GPT API:', response.status_code, response.text)
        return 'Error'

def example_word(message_input):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

    systemMessage= '''You are a designer who is finding ideas of situated visualization. The given data format is "keyword: association (dimension)", the task is to give two related words of each association word. Physical referent and concrete noun are better.
    Step 1: Analyze the relevant characteristics of the association word, which should be based on their own characteristics (color, material, size, sound, touch, social significance, etc.)
    Step 2: Give two related words sharing similar characteristics of the association word without considering the dimension in parentheses.
    Take an example. The association word is pulse, its related words can be blinking lights and stethoscope.The reason is: The pulse and the blinking lights share the common nature of pulsing rhythmically; A stethoscope can detect heartbeat.
    Make sure to capitalize the first letter and continue the response in following format: keyword 1: association 1 (dimension) + related word1, related word2 \n keyword 1: association 2 (dimension) + related word1, related word2 \n keyword 2: association 1 (dimension) + related word1, related word2 \n ... keyword 3: association 3 (dimension) + related word1, related word2
    For example, the given data is 'War: soldier (user)', you should output 'War: soldier (user) + flower, gun'''
    message=[
        {'role':'system',
         'content': systemMessage},
        {'role':'user',
         'content': 'The given data' + message_input},
        ]

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': message,
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']

    else:
        print('Error calling GPT API:', response.status_code, response.text)
        return 'Error'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002,debug=True)
