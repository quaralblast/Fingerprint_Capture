import json
import hashlib
import numpy as np

def list_to_8_char_string(input_list):
    """
    Convert a 64-item list of numbers to an 8-character string.
    
    Parameters:
    - input_list: List of 64 numerical values.

    Returns:
    - An 8-character string generated using a hash of the list.
    """
    if len(input_list) != 64:
        raise ValueError("Input list must contain exactly 64 items.")
    
    # Convert the list to a string representation
    list_string = ",".join(map(str, input_list))
    
    # Create an MD5 hash of the string
    hash_object = hashlib.md5(list_string.encode())
    
    # Return the first 8 characters of the hash
    return hash_object.hexdigest()[:8]

def save_feature_vector(feature_vector, FILE_PATH):
    """
    Save a feature vector and its randomly generated label to a JSON file.

    Parameters:
    - feature_vector: Nested list representing the feature vector.
    - FILE_PATH: Path to the JSON file where the data will be saved.
    """
    
    # Convert NumPy array to list before saving
    feature_vector_as_list = feature_vector.tolist() if isinstance(feature_vector, np.ndarray) else feature_vector
    
    label = list_to_8_char_string(feature_vector_as_list)
    
    new_entry = {
        "label": label,
        "feature_vector": feature_vector_as_list
    }

    try:
        # Load existing data if the file exists
        try:
            with open(FILE_PATH, 'r') as json_file:
                data = json.load(json_file)
                # Ensure data is a list
                if not isinstance(data, list):
                    raise ValueError("JSON file does not contain a list. Resetting to an empty list.")
        except (FileNotFoundError, ValueError):
            # If file does not exist or contains invalid data, initialize an empty list
            data = []

        # Append the new entry to the data
        data.append(new_entry)

        # Save updated data back to the file
        with open(FILE_PATH, 'w') as json_file:
            json.dump(data, json_file)
        print(f"Entry added successfully to {FILE_PATH}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def terminate_feature_vector(label_to_delete,FILE_PATH):
    try:
        # Load existing data if the file exists
        try:
            with open(FILE_PATH, 'r') as json_file:
                data = json.load(json_file)
                # Ensure data is a list
                if not isinstance(data, list):
                    raise ValueError("JSON file does not contain a list. Resetting to an empty list.")
        except (FileNotFoundError, ValueError):
            # If file does not exist or contains invalid data, initialize an empty list
            data = []

        filtered_data = [item for item in data if item["label"] != label_to_delete]
       
        # Save updated data back to the file
        with open(FILE_PATH, 'w') as json_file:
            json.dump(filtered_data, json_file)
        print(f"Entry terminated in {FILE_PATH}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def calculate_distance(vector1, vector2):
    """
    Calculate the Euclidean distance between two vectors.

    Parameters:
    - vector1: First feature vector (list or NumPy array).
    - vector2: Second feature vector (list or NumPy array).

    Returns:
    - The Euclidean distance as a float.
    """
    # Convert to NumPy arrays for easy manipulation
    vec1 = np.array(vector1)
    vec2 = np.array(vector2)
    
    # Compute Euclidean distance
    return np.linalg.norm(vec1 - vec2)

def compare_feature_vector(new_vector, FILE_PATH):
    """
    Compare a new feature vector against all saved feature vectors in the JSON file,
    and return a dictionary with distance scores.

    Parameters:
    - new_vector: The feature vector to compare (list of 64 numerical values).
    - FILE_PATH: Path to the JSON file containing saved feature vectors.

    Returns:
    - A dictionary where keys are labels and values are distance scores.
    """
    try:
        # Load existing data from the JSON file
        with open(FILE_PATH, 'r') as json_file:
            data = json.load(json_file)
        
        # Ensure the data is a list
        if not isinstance(data, list):
            raise ValueError("JSON file does not contain a list.")
        
        # Prepare output dictionary
        distance_scores = {}
        
        # Calculate distance for each saved feature vector
        for entry in data:
            label = entry.get("label")
            saved_vector = entry.get("feature_vector")
            
            # Ensure both label and vector exist
            if label is not None and saved_vector is not None:
                distance = calculate_distance(new_vector, saved_vector)
                distance_scores[label] = distance
        
        return distance_scores
    
    except FileNotFoundError:
        print("JSON file not found.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}