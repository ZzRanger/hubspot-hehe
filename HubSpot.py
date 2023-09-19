# Get dependencies
import requests
import json

# Make get request
response = requests.get('https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=b67943574d0b7a9bb8e10a044532')

# Note: data is sorted by timestamp (ascending order)
data = response.json()['events']

# If future data isn't sorted by timestamp, create function to sort data

final_data = {}
TEN_SECONDS = 600000 # in miliseconds

for entry in data:
    # Get user id of entry
    entry_id = entry['visitorId']

    # Add to data if no data exists
    if entry_id not in final_data.keys():
        final_data[entry_id] = []
        final_data[entry_id].append({"duration": 0, "pages": [entry["url"]], 
        "startTime": entry['timestamp']})
    
    # Look at all entries in user id 
    else:
        
        first_entry = final_data[entry_id][0]
        last_entry = final_data[entry_id][-1]

        # Check if we append entry at beginning (doesn't run since data is sorted by timestamps)
        if first_entry["startTime"] - entry['timestamp'] > TEN_SECONDS:
            final_data[entry_id].insert(0, {"duration": 0, "pages": [entry["url"]], 
            "startTime": entry['timestamp']})   

        # Check if we append entry at end
        elif entry['timestamp']  - (last_entry["startTime"] + last_entry["duration"]) > TEN_SECONDS:
            final_data[entry_id].append({"duration": 0, "pages": [entry["url"]], 
            "startTime": entry['timestamp']})  
       
        # Iterate through code to find where to insert data
        else:
            index = 0
            for session in final_data[entry_id]:

                # Check if in bounds

                # If Entry before session (doesn't run because data sorted by timestamp)
                if session['startTime'] - entry['timestamp'] <= TEN_SECONDS and session['startTime'] > entry['timestamp']:
                    session['duration'] = session['duration'] + session['startTime'] - entry['timestamp'] 
                    session['startTime'] = entry['timestamp']
                    session['pages'].insert(0, entry['url'])
                    break

                # If entry after session
                elif entry['timestamp'] - session['startTime'] - session['duration'] <= TEN_SECONDS and entry['timestamp'] > (session['startTime'] + session['duration']):
                    session['duration'] = entry['timestamp'] - session['startTime'] 
                    session['pages'].append(entry['url'])
                    break

                # If entry in middle (broken rn; also won't run because data sorted by timestamp)
                elif session['startTime'] <= entry['timestamp'] <= session['startTime'] + session['duration']:
                    session['duration'] = entry['timestamp'] - session['startTime'] 
                    session['pages'].append(entry['url'])             
                    break

                # Check if smaller (doesn't do anything tbh)
                elif entry['timestamp'] > (session['duration'] + session['startTime']):
                    index += 1
                
                # Add new entry if between 2 session entries (doesn't run because data sorted by timestamp)
                else:
                    final_data[entry_id].insert(index, {"duration": 0, "pages": [entry["url"]], 
                    "startTime": entry['timestamp']})     
                    break 

formatted_data = {"sessionsByUser": final_data}
text = json.dumps(formatted_data)

# Make post request
tester = requests.post(data=text, url='https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=b67943574d0b7a9bb8e10a044532')
print(tester.content)
print(tester.status_code)