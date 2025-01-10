from flask import Flask, render_template, request, jsonify, request
import csv
import pandas as pd
import numpy as np

app = Flask(__name__)

received_data = []  # Global variable to store received data

def read_csv(file_path):
    players_data = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['Total lap 1'] = sum(int(row[f'{i}']) for i in range(1, 11))
            row['Total lap 2'] = sum(int(row[f'{i}']) for i in range(11, 21))
            row['Total lap 3'] = sum(int(row[f'{i}']) for i in range(21, 31))
            row['Total lap 4'] = sum(int(row[f'{i}']) for i in range(31, 41))
            row['Final Score'] = row['Total lap 1'] + row['Total lap 2'] + row['Total lap 3'] + row['Total lap 4']

            row["0's"] = sum(1 for i in range(1, 41) if row[f'{i}'] == '0')
            row["1's"] = sum(1 for i in range(1, 41) if row[f'{i}'] == '1')
            row["2's"] = sum(1 for i in range(1, 41) if row[f'{i}'] == '2')
            row["3's"] = sum(1 for i in range(1, 41) if row[f'{i}'] == '3')
            row["5's"] = sum(1 for i in range(1, 41) if row[f'{i}'] == '5')
    return players_data


def read_entries(file_path):
    entries = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['Total lap 1'] = 0
            row['Total lap 2'] = 0
            row['Total lap 3'] = 0
            row['Total lap 4'] = 0
            row['Final Score'] = 0
            row["0's"] = 0
            row["1's"] = 0
            row["2's"] = 0
            row["3's"] = 0
            row["5's"] = 0
            entries.append(row)
    return entries


def create_dataframe(file_path):
    df = pd.read_csv(file_path)
    for i in range(1, 41):
        df[str(i)] = np.nan
    #df = df.fillna("")
    return df

@app.route("/")
def home():
    classes = {}
    for _, player in df.iterrows():
        class_id = player['Class']
        if class_id not in classes:
            classes[class_id] = []
        classes[class_id].append(player.to_dict())
    
    return render_template('table.html', classes=classes)

@app.route("/dataframe", methods=["POST"])
def get_dataframe():
    df = create_dataframe('data/entries.csv')
    return jsonify(df.to_dict(orient="records"))


@app.route("/submit_score", methods=["POST"])
def submit_score():
    print("A")
    global df , received_data  # Use the DataFrame created at startup
    data = request.json
    print(f"Received data: {data}")
    
    player_id = int(data['player_id'])
    score = int(data['score'])

    # Add the received data to the global list
    received_data.append({"player_id": player_id, "score": score})
    
    #todo: add lap and section logic to the POST request and validate it and ensure we are adding the data to the correct cell

    # Find the row for the player
    player_row = df[df['ID'] == player_id]
    
    if player_row.empty:
        return jsonify({"error": "Player not found"}), 404
    
    # Find the next empty cell in the player's row
    for col in range(1, 41):
        if pd.isna(player_row.iloc[0][str(col)]):
            df.loc[df['ID'] == player_id, str(col)] = score
            break
    print(df)

    # Recalculate total and lap scores
    df['Total lap 1'] = df.loc[:, '1':'10'].sum(axis=1)
    df['Total lap 2'] = df.loc[:, '11':'20'].sum(axis=1)
    df['Total lap 3'] = df.loc[:, '21':'30'].sum(axis=1)
    df['Total lap 4'] = df.loc[:, '31':'40'].sum(axis=1)
    df['Final Score'] = df['Total lap 1'] + df['Total lap 2'] + df['Total lap 3'] + df['Total lap 4']
    #TODO add 0's, 1's, 2's, 3's, 5's



    return jsonify({"status": "Score updated"}), 200


@app.before_request
def log_request_info():
    print("\n--- Incoming Request ---")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data().decode('utf-8')}")
    print("-----------------------")


@app.route("/show_scores")
def show_scores():
    global received_data
    return render_template('scores.html', scores=received_data)

if __name__ == "__main__":
    df = create_dataframe('data/entries.csv')
    #print(df)
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)