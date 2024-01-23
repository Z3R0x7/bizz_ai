import click
import openai
import requests
import webbrowser

# Microsoft Graph API credentials
CLIENT_ID = 'your_client_id'
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
        click.echo("3. Exit")

        # Get user choice
        choice = click.prompt("Enter your choice (1-3)", type=int)

        if choice == 1:
            # Send email to Microsoft account
            send_email_to_microsoft()
        elif choice == 2:
            # Send email to a new user
            send_email_to_new_user()
        elif choice == 3:
            # Exit the program
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

    # Send the email (You can customize this logic as needed)
    send_status = send_email(access_token, to_email, subject, body)

    if send_status == 202:
        click.echo('Email sent successfully!')
    else:
        click.echo('Email sending failed.')


if __name__ == '__main__':
    main()
