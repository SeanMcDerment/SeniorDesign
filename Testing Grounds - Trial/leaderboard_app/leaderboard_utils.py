import csv
from collections import defaultdict

def read_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def create_leaderboard(data):
    return sorted(data, key=lambda x: int(x['score']), reverse=True)

def calculate_department_averages(data):
    department_scores = defaultdict(list)

    for entry in data:
        department_scores[entry['department']].append(int(entry['score']))

    department_averages = {department: sum(scores) / len(scores) for department, scores in department_scores.items()}

    return department_averages
