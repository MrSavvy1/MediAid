import random
import json
import torch

import math
import geocoder

from model_chat import RNNModel  # Import the RNN model
from nltk_utils import bag_of_words, tokenize
import webbrowser

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data) #loads dataset for response

FILE = "data_rnn.pth"  # Update this file name
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
num_layers = data["num_layers"]  # Add the number of layers used in your RNN model
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def open_google_maps(location):
    """Open Google Maps with the specified location."""
    url = f"https://www.google.com/maps/search/?api=1&query={location}"
    webbrowser.open(url)


def get_response(msg):
    sentence = tokenize(msg)
    if ("name" in sentence) or ("this is" in msg.lower()) :
        for wor in sentence:
            if (wor.lower() != "my") and (wor.lower() != "is") and (wor.lower() != "name") and (wor.lower() != "i") and (wor.lower() != "am") and (wor.lower() != "this"):
                user_name = wor.capitalize()
                res = "Hi " + user_name + " please what is your age."
                return ["name", res]
    if ("age" in sentence) or ("I" in sentence and "am" in sentence) or ("I'm" in sentence):
        for wor in sentence:
            if wor.isnumeric():
                user_age = wor
                res = "What is your gender?"
                return ["age", res]
    if ("male" in sentence) or ("female" in sentence) or ("Male" in sentence) or ("Female" in sentence):
        for wor in sentence:
            if (wor.lower() == "male") or (wor.lower() == "female"):
                user_gender = wor.lower()
                res = "state the symptoms you have, for potential diagnosis."
                return ["gender", res]
    if ("yes" in sentence) or (("medical" in sentence) and "center" in sentence) or ("hospital" in sentence) or ("hospitals" in sentence):
        # You can specify a location or use the user's current location here.
        location = "Opening Google Maps for nearby hospitals..."  # Example location
        open_google_maps(location)  # Call the Google Maps function
        return ["redirect", location, "map"]


    X = bag_of_words(sentence, all_words)
    X = torch.tensor(X).unsqueeze(0).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    #topk_values, topk_indices = torch.topk(output, k=3, dim=1)

    tag = tags[predicted.item()]
    #tag = [tags[i] for i in topk_indices[0]]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    """
    if prob.item() > 0.5:
        l = []
        for intent in intents['intents']:
            for a in tag:
                if intent["tag"] == a:
                    l.append([intent['tag'], intent['responses']])
        return l
    """
    
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if intent["tag"] == tag:
                if tag in ["greeting", "goodbye","work","who","Thanks","joke", "name", "age", "gender"]:
                    return [intent['tag'], intent['responses']]
                return [intent['tag'], intent['responses'], intent['Precaution']]

    return ["not_understand","I do not understand. Can you please rephrase the sentence?"]


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print("Bot:", resp)
