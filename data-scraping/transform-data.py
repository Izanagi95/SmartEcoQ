import json

# Input file containing the text data
input_file = 'data.txt'
# Output file to save the JSON data
output_file = 'events.json'

def parse_event_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # Splitting data into individual events
    events = data.strip().split("\n\n")
    parsed_events = []

    for event in events:
        lines = event.split("\n")
        warning = None
        if "Evento su prenotazione" in lines[1]:
            warning = lines[1].strip()
            start_time, end_time = lines[5].split("/")
        else:
            start_time, end_time = lines[4].split("/")
        event_data = {
            "date": lines[0].strip(),
            "title": lines[1].strip() if warning is None else lines[2].strip(),
            "location": lines[2].strip() if warning is None else lines[3].strip(),
            "start_time": start_time.strip(),
            "end_time": end_time.strip(),
            "warning": warning
        }
        parsed_events.append(event_data)

    return parsed_events

def save_as_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    events = parse_event_data(input_file)
    save_as_json(events, output_file)
    print(f"Events have been successfully saved to {output_file}")
