import json

def delete_objects_by_date(data, date_to_delete):
    """
    Remove objects from the list with the specified date.

    Parameters:
        data (list): List of dictionaries representing events.
        date_to_delete (str): Date to filter out (format: DD/MM/YYYY).

    Returns:
        list: Updated list with objects matching the specified date.
    """
    return [obj for obj in data if obj['date'] == date_to_delete]

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

def write_json(file_path, data):
    """
    Write a list of dictionaries to a JSON file.

    Parameters:
        file_path (str): Path to the output JSON file.
        data (list): List of dictionaries to write.
    """
    with open(file_path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":
    input_file = "events2-11.json"  # Input JSON file path
    output_file = "events-2-11.json"  # Output JSON file path

    # Read data from the JSON file
    events = read_json(input_file)

    # Specify the date to keep and discard all the other dates
    date_to_keep = "02/11/2024"

    # Delete objects with the specified date
    updated_events = delete_objects_by_date(events, date_to_keep)

    # Write the updated list back to a new JSON file
    write_json(output_file, updated_events)

    print(f"Updated program saved to {output_file}")