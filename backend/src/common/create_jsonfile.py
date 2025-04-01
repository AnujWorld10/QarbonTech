import json

#Method to write responses to json file
def create_response_json(unique_id, data_dict, file_location):
    try:
        with open(file_location, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError,Exception):
        existing_data = {}
    
    existing_data[unique_id] = data_dict
    
    try:
        with open(file_location, 'w') as file:
            json.dump(existing_data, file, indent=4)
        print(f"Data for unique ID {unique_id} has been written to {file_location}")
    except Exception as e:
        print(f"An error occurred while writing to {file_location}: {e}")

#Method to update responses to json file
def update_state(id,new_data, filename):
    
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data[id]["state"] = new_data
        file.seek(0)
        file.truncate()
        json.dump(file_data, file, indent = 4)

def update_subscription(id,new_data, filename):
     with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data[id]["subscription"] = new_data
        file.seek(0)
        file.truncate()
        json.dump(file_data, file, indent = 4) 