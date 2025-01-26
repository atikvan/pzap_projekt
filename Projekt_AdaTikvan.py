import pandas as pd
import sqlite3
from flask import Flask, jsonify
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.use('TkAgg')

csv_data = pd.read_csv("C:\\Users\\Ada\\Desktop\\pzap_projekt\\medals.csv")
xlsx_data = pd.read_excel("C:\\Users\\Ada\\Desktop\\pzap_projekt\\athletes.xlsx")


csv_data = csv_data[['Team/Country', 'Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total', 'Continent']]
xlsx_data = xlsx_data[['Name', 'Country', 'Discipline']]

csv_data.rename(columns={'Team/Country': 'Country'}, inplace=True)

merged_data = pd.merge(csv_data, xlsx_data, on='Country', how='left')


conn = sqlite3.connect('olympics_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS olympics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT,
    gold_medals INTEGER,
    silver_medals INTEGER,
    bronze_medals INTEGER,
    total_medals INTEGER,
    continent TEXT,
    athlete_name TEXT,
    discipline TEXT
)
''')

merged_data.to_sql('olympics', conn, if_exists='replace', index=False)
conn.commit()

app = Flask(__name__)

def get_data_from_db(query):
    conn = sqlite3.connect('olympics_data.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/medals', methods=['GET'])
def get_medals():
    query = "SELECT * FROM olympics"
    data = get_data_from_db(query)
    result = []
    for row in data:
        result.append({
            'Country': row[1],
            'Gold Medal': row[2],
            'Silver Medal': row[3],
            'Bronze Medal': row[4],
            'Total Medals': row[5],
            'Continent': row[6],
            'Athlete': row[7],
            'Discipline': row[8]
        })
    return jsonify(result)

if __name__ == '__main__':
    query = '''
    SELECT Continent, 
           SUM("Gold Medal") as Gold, 
           SUM("Silver Medal") as Silver, 
           SUM("Bronze Medal") as Bronze 
    FROM olympics 
    GROUP BY Continent
'''
    continent_data = pd.read_sql(query, conn)
    continent_data.set_index('Continent').plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title("Medals by Continent")
    plt.ylabel("Number of Medals")
    plt.show()
    plt.close()

    # Spremanje podataka u .xlsx datoteku
    output_file = "C:\\Users\\Ada\\Desktop\\medals_by_continent.xlsx"
    continent_data.to_excel(output_file, index=False)

    print(f"Podaci o medaljama po kontinentima spremljeni su u {output_file}")

athletes_with_medals = merged_data[merged_data['Total'] > 0][['Name', 'Discipline', 'Country', 'Total']].dropna()

    # Spremanje popisa sportaša u novu .xlsx datoteku
athletes_output_file = "C:\\Users\\Ada\\Desktop\\athletes_with_medals.xlsx"
athletes_with_medals.to_excel(athletes_output_file, index=False)

print(f"Popis sportaša s osvojenim medaljama spremljen je u {athletes_output_file}")

    # Pokretanje Flask servera
app.run(debug=True)
