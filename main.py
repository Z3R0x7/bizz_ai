import click
import openai
import requests
import webbrowser
import calendar

# Microsoft Graph API credentials
CLIENT_ID = '11a1c536-f7fc-4902-83a4-44dd3d7cdff1'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'your_redirect_uri'
SCOPE = ['offline_access', 'user.read', 'mail.send']

# OpenAI API key
OPENAI_API_KEY = ' '
openai.api_key = OPENAI_API_KEY

# Microsoft Graph API endpoints
AUTHORITY = 'https://login.microsoftonline.com/common'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/'

# Microsoft Graph API authentication
def get_access_token(auth_code):
    token_url = f"{AUTHORITY}{TOKEN_ENDPOINT}"
    token_payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPE),
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(token_url, data=token_payload)
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    return access_token

def list_files(access_token):
    list_url = f"{GRAPH_API_ENDPOINT}me/drive/root/children"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(list_url, headers=headers)
    if response.status_code == 200:
        files = response.json().get('value', [])
        if files:
            click.echo("Files in OneDrive:")
            for file in files:
                click.echo(file['name'])
        else:
            click.echo("No files found in OneDrive.")
    else:
        raise Exception("Failed to list files")

def upload_file(access_token, file_path, folder_id):
    upload_url = f"{GRAPH_API_ENDPOINT}me/drive/items/{folder_id}/children/{file_path}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        # Implement file upload data
    }
    response = requests.put(upload_url, headers=headers, data=data)
    if response.status_code == 201:
        click.echo(f"File {file_path} uploaded successfully.")
    else:
        raise Exception("Failed to upload file")

def download_file(access_token, file_id, destination_path):
    download_url = f"{GRAPH_API_ENDPOINT}me/drive/items/{file_id}/content"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        with open(destination_path, 'wb') as f:
            f.write(response.content)
        click.echo(f"File downloaded successfully to {destination_path}.")
    else:
        raise Exception("Failed to download file")

def create_folder(access_token, folder_name, parent_folder_id):
    create_url = f"{GRAPH_API_ENDPOINT}me/drive/items/{parent_folder_id}/children"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': folder_name,
        'folder': { }
    }
    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 201:
        click.echo(f"Folder '{folder_name}' created successfully.")
    else:
        raise Exception("Failed to create folder")

def delete_file(access_token, file_id):
    delete_url = f"{GRAPH_API_ENDPOINT}me/drive/items/{file_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.delete(delete_url, headers=headers)
    if response.status_code == 204:
        click.echo(f"File deleted successfully.")
    else:
        raise Exception("Failed to delete file")

def get_upcoming_events(access_token):
    events_url = f"{GRAPH_API_ENDPOINT}me/calendar/events"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(events_url, headers=headers)
    events = response.json().get('value', [])
    return events


def draw_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    print(f"  {month_name} {year}")
    print("---------------------------")
    print(" Mo Tu We Th Fr Sa Su")
    
    for week in cal:
        week_str = " ".join(str(day) if day != 0 else "  " for day in week)
        print(week_str)


def add_calendar_event(access_token, event_details):
    create_event_url = f"{GRAPH_API_ENDPOINT}me/calendar/events"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    event_payload = {
        'subject': event_details['subject'],
        'start': {'dateTime': event_details['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': event_details['end'], 'timeZone': 'UTC'},
    }
    response = requests.post(create_event_url, headers=headers, json=event_payload)
    return response.status_code

# Compose and send email using Microsoft Graph API
def send_email(access_token, to_email, subject, body):
    send_url = f'{GRAPH_API_ENDPOINT}me/sendMail'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    message = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body,
            },
            'toRecipients': [{'emailAddress': {'address': to_email}}],
        }
    }
    response = requests.post(send_url, headers=headers, json=message)
    return response.status_code

# ChatGPT function
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@click.command()
def main():
    click.echo("Welcome to the Email Composer CLI!")

    while True:
        # Display menu options
        click.echo("\nMenu:")
        click.echo("1. Send email to Microsoft account")
        click.echo("2. Send email to a new user")
        click.echo("3. Add calendar event")
        click.echo("4. View upcoming events")
        click.echo("5. List Files")
        click.echo("6. Upload File")
        click.echo("7. Download File")
        click.echo("8. Create Folder")
        click.echo("9. Delete File")
        click.echo("10. Exit")

        # Get user choice
        choice = click.prompt("Enter your choice (1-10)", type=int)

        if choice == 1:
            # Send email to Microsoft account
            send_email_to_microsoft()
        elif choice == 2:
            # Send email to a new user
            send_email_to_new_user()
        elif choice == 3:
            add_calendar_event()
        elif choice == 4:
            view_upcoming_events()
        elif choice == 5:
            auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'
            click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
            webbrowser.open(auth_url)

            auth_code = click.prompt('Enter the authorization code from the URL:')
            access_token = get_access_token(auth_code)

            list_files(access_token)
        elif choice == 6:
            auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'
            click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
            webbrowser.open(auth_url)

            auth_code = click.prompt('Enter the authorization code from the URL:')
            access_token = get_access_token(auth_code)

            file_path = click.prompt('Enter file path:')
            folder_id = click.prompt('Enter folder ID:')
            upload_file(access_token, file_path, folder_id)
        elif choice == 7:
            auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'
            click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
            webbrowser.open(auth_url)
        
            auth_code = click.prompt('Enter the authorization code from the URL:')
            access_token = get_access_token(auth_code)
        
            file_id = click.prompt('Enter file ID:')
            destination_path = click.prompt('Enter destination path:')
            download_file(access_token, file_id, destination_path)
        
        elif choice == 8:
            auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'
            click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
            webbrowser.open(auth_url)
        
            auth_code = click.prompt('Enter the authorization code from the URL:')
            access_token = get_access_token(auth_code)
        
            folder_name = click.prompt('Enter folder name:')
            parent_folder_id = click.prompt('Enter parent folder ID:')
            create_folder(access_token, folder_name, parent_folder_id)
        
        elif choice == 9:
            auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'
            click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
            webbrowser.open(auth_url)
        
            auth_code = click.prompt('Enter the authorization code from the URL:')
            access_token = get_access_token(auth_code)
        
            file_id = click.prompt('Enter file ID:')
            delete_file(access_token, file_id)
        
        elif choice == 10:
            click.echo("Exiting. Goodbye!")
            break
        else:
            click.echo("Invalid choice. Please enter a valid option.")

def send_email_to_microsoft():
    # Get Microsoft Graph API access token
    auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'

    click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
    webbrowser.open(auth_url)

    auth_code = click.prompt('Enter the authorization code from the URL:')
    access_token = get_access_token(auth_code)

    # ChatGPT generates the email body based on user input
    to_email = click.prompt('Recipient Email')
    subject = click.prompt('Email Subject')
    prompt = f"Compose an email to {to_email} with the subject: '{subject}'. Content:"
    body = chat_with_gpt(prompt)

    # Send the email
    send_status = send_email(access_token, to_email, subject, body)

    if send_status == 202:
        click.echo('Email sent successfully!')
    else:
        click.echo('Email sending failed.')

def send_email_to_new_user():
    # Get user input for a new email
    to_email = click.prompt('Recipient Email')
    subject = click.prompt('Email Subject')
    body = click.prompt('Email Body')
    auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'

    click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
    webbrowser.open(auth_url)

    auth_code = click.prompt('Enter the authorization code from the URL:')
    access_token = get_access_token(auth_code)
    # Send the email (You can customize this logic as needed)
    send_status = send_email(access_token, to_email, subject, body)

    if send_status == 202:
        click.echo('Email sent successfully!')
    else:
        click.echo('Email sending failed.')
def view_upcoming_events():
    auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'

    click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
    webbrowser.open(auth_url)

    auth_code = click.prompt('Enter the authorization code from the URL:')
    access_token = get_access_token(auth_code)

    events = get_upcoming_events(access_token)

    click.echo("\nUpcoming Events:")
    for event in events:
        click.echo(f"Subject: {event.get('subject')}, Start Time: {event.get('start').get('dateTime')}")

    # Get current year and month
    current_year, current_month = events[0].get('start').get('dateTime')[:7].split('-')

    # Draw the calendar for the current month
    draw_calendar(int(current_year), int(current_month))

def add_calendar_event():
    auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={" ".join(SCOPE)}'

    click.echo(f'Open the following URL in your browser to log in and authorize the app:\n{auth_url}')
    webbrowser.open(auth_url)

    auth_code = click.prompt('Enter the authorization code from the URL:')
    access_token = get_access_token(auth_code)

    event_details = {
        'subject': click.prompt("Enter event title:"),
        'start': click.prompt("Enter event start time (YYYY-MM-DDTHH:mm:ss):"),
        'end': click.prompt("Enter event end time (YYYY-MM-DDTHH:mm:ss):"),
    }

    status_code = add_calendar_event(access_token, event_details)

    if status_code == 201:
        click.echo('Event added successfully!')
    else:
        click.echo(f'Failed to add event. Status Code: {status_code}')


if __name__ == '__main__':
    main()
