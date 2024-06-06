from flask import Flask, json, jsonify, render_template, request, url_for
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import language_tool_python
from nltk.corpus import wordnet
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('wordnet')
app = Flask(__name__, static_folder='static')

@app.route('/')
def home():  
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contactus.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

sid = SentimentIntensityAnalyzer()

tool = language_tool_python.LanguageTool('en-US')

sentence_pattern = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s')

@app.route('/process', methods=['GET', 'POST']) 
def process():
    try:
        data = request.get_json()
        ruleIdList = data.get('list3', [])
        eTokenList = data.get('list1', [])
        rTokenList = data.get('list2', [])

        with open("datalog.txt", "a") as f:
            f.write(json.dumps({
                "ruleIdList": ruleIdList,
                "eTokenList": eTokenList,
                "rTokenList": rTokenList
            }) + "\n\n")

        return jsonify(success=True)

    except (KeyError, TypeError) as e:
        errormessage = f"Error occurred: {str(e)}"
        return jsonify(error="Not received"), 400

@app.route('/index', methods=['GET', 'POST'])
def index():
    lenwords, lenchar, lensen, lenpar = 0, 0, 0, 0
    positive_score, negative_score, neutral_score, compound_score = 0, 0, 0, 0
    input_text = ""
    errors, synonyms = [], []

    if request.method == 'POST':
        input_text = request.form['input_text']
        lenchar = len(input_text)
        lenwords = len(input_text.split())
        lensen = len(sentence_pattern.split(input_text))
        lenpar = len(input_text.split('\n\n'))

        positive_score, negative_score, neutral_score, compound_score = sentiment(input_text)
        if lenchar != 0 and lenchar <= 3500:
            errors = grammar(input_text)
        elif lenchar == 0:
            open('datalog.txt', 'w').close()
            print("lenchar:", lenchar)
        else:
            errors = []
        synonyms = get_synonyms_for_text(input_text)

    return render_template('index.html', lenwords=lenwords, lenchar=lenchar, lensen=lensen, lenpar=lenpar,
                           positive_score=positive_score, negative_score=negative_score,
                           neutral_score=neutral_score, compound_score=compound_score,
                           input_text=input_text, errors = errors, synonyms = synonyms)

def grammar(text):
    try:
        file_name = "datalog.txt"
        rTokenList = []
    
        with open(file_name, "r") as f:
            lines = f.readlines()
            data_str = ""
            for line in lines:
                if line.strip() == "":
                    if data_str != "":
                        data = json.loads(data_str)
                        rTokenList.extend(data.get('rTokenList', []))
                        data_str = ""
                else:
                    data_str += line
            if data_str != "":
                data = json.loads(data_str)
                rTokenList.extend(data.get('rTokenList', []))
        matches = tool.check(text)
        errors = [{'rule_id': match.ruleId, 'message': match.message, 'replacements': match.replacements[:6],
                   'context': match.context, 'error_token': text[match.offset:match.offset + match.errorLength],'elenght':match.errorLength,'offset':match.offset }
                  for match in matches]
        if rTokenList:
            for error in errors:
                error['replacements'] = [replacement for replacement in error['replacements'] if replacement not in rTokenList]
                
    except Exception as e:
        print("An error occurred during grammar check:", e)
    return errors

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def get_synonyms_for_text(text):
    tokens = nltk.word_tokenize(text)
    synonyms_for_tokens = {}
    for token in tokens:
        synonyms = get_synonyms(token)
        synonyms_for_tokens[token] = synonyms
    return synonyms_for_tokens

def sentiment(text):
    try:
        scores = sid.polarity_scores(text)
        positive_score = scores['pos']
        negative_score = scores['neg']
        neutral_score = scores['neu']
        compound_score = scores['compound']
    except Exception as e:
        positive_score = negative_score = neutral_score = compound_score = 0
    return positive_score, negative_score, neutral_score, compound_score

if __name__ == "__main__":
    app.run(debug=True)