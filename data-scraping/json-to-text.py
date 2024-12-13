import json

def format_event(event):
    """
    Format a single event dictionary into a structured text format.

    Parameters:
        event (dict): A dictionary containing event details.

    Returns:
        str: Formatted string representing the event.
    """
    warning_text = f"Warning: {event['warning']}" if event['warning'] else "No warnings"
    return (
        f"Date: {event['date']}\n"
        f"Title: {event['title']}\n"
        f"Location: {event['location']}\n"
        f"Start Time: {event['start_time']}\n"
        f"End Time: {event['end_time']}\n"
        f"{warning_text}\n"
        f"{'-' * 40}"
    )

def read_json(file_path):
    """
    Read JSON file and return a list of dictionaries.

    Parameters:
        file_path (str): Path to the input JSON file.

    Returns:
        list: List of dictionaries representing rows.
    """
    with open(file_path, mode='r', encoding='utf-8') as file:
        return json.load(file)

def write_text(file_path, data):
    """
    Write a list of formatted event strings to a text file.

    Parameters:
        file_path (str): Path to the output text file.
        data (list): List of formatted event strings to write.
    """
    with open(file_path, mode='w', encoding='utf-8') as file:
        file.write("\n\n".join(data))

# Example usage
if __name__ == "__main__":
    input_file = "events-3-11.json"  # Input JSON file path
    output_file = "events-3-11.txt"  # Output TXT file path

    # Read data from the JSON file
    events = read_json(input_file)

    # Format each event
    formatted_events = [format_event(event) for event in events]

    # Write the formatted events to a text file
    write_text(output_file, formatted_events)

    print(f"Formatted program saved to {output_file}")
