from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import io
import csv

app = Flask(__name__)

# Function to process the CSV files and allocate rooms
def allocate_rooms(groups_df, hostels_df):
    # Prepare data structures
    boys_hostels = hostels_df[hostels_df['Gender'] == 'Boys']
    girls_hostels = hostels_df[hostels_df['Gender'] == 'Girls']
    
    allocated_rooms = []
    
    for _, group in groups_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']
        
        if gender == 'Boys':
            available_rooms = boys_hostels
        else:
            available_rooms = girls_hostels
        
        for _, room in available_rooms.iterrows():
            room_capacity = room['Capacity']
            if room_capacity >= members:
                allocated_rooms.append({
                    'Group ID': group_id,
                    'Hostel Name': room['Hostel Name'],
                    'Room Number': room['Room Number'],
                    'Members Allocated': members
                })
                if gender == 'Boys':
                    boys_hostels = boys_hostels[~((boys_hostels['Hostel Name'] == room['Hostel Name']) & (boys_hostels['Room Number'] == room['Room Number']))]
                else:
                    girls_hostels = girls_hostels[~((girls_hostels['Hostel Name'] == room['Hostel Name']) & (girls_hostels['Room Number'] == room['Room Number']))]
                break
    
    return allocated_rooms

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            groups_df = pd.read_csv(file1)
            hostels_df = pd.read_csv(file2)
            
            allocated_rooms = allocate_rooms(groups_df, hostels_df)
            
            # Prepare the CSV output for download
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=['Group ID', 'Hostel Name', 'Room Number', 'Members Allocated'])
            writer.writeheader()
            writer.writerows(allocated_rooms)
            output.seek(0)
            
            # Prepare the data for the result page
            return render_template('result.html', allocated_rooms=allocated_rooms)
    
    return render_template('index.html')

@app.route('/download')
def download():
    # Download the CSV file with allocation details
    allocated_rooms = request.args.get('allocated_rooms', '')
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['Group ID', 'Hostel Name', 'Room Number', 'Members Allocated'])
    writer.writeheader()
    writer.writerows(eval(allocated_rooms))
    output.seek(0)
    
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='allocated_rooms.csv')

if __name__ == '__main__':
    app.run(debug=True)
