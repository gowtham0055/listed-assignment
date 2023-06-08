import os
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set up Gmail API client
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Path to the token.json file
TOKEN_PATH = 'token.json'

def get_credentials():
    if os.path.exists(TOKEN_PATH):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        return creds

    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

    return creds

creds = get_credentials()
service = build('gmail', 'v1', credentials=creds)


# Function to check for new emails and send auto-replies
def send_auto_replies():
    user_id = 'me'
    query = 'is:inbox'  # Modify this query as per your requirements

    try:
        # Get a list of unread emails
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get('messages', [])

        if not messages:
            print('No new emails found.')
        else:
            print(f'{len(messages)} new email(s) found.')

        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]

            # Check if the email has no prior replies
            if 'Re:' not in subject and 'Fwd:' not in subject:
                # Generate auto-reply message
                auto_reply = f"Thank you for your email. I'm currently on vacation and will reply to your message as soon as possible."

                # Send auto-reply
                reply = service.users().messages().send(
                    userId=user_id,
                    body={'raw': base64.urlsafe_b64encode(auto_reply.encode('utf-8')).decode('utf-8'), 'threadId': msg['threadId']}
                ).execute()

                print(f"Auto-reply sent to email with subject: {subject}")

                # Add label to the replied email and move it to the label
                label_id = 'Label_1'  # Modify this label ID as per your requirements
                service.users().messages().modify(
                    userId=user_id,
                    id=msg['id'],
                    body={'addLabelIds': [label_id], 'removeLabelIds': ['UNREAD']}
                ).execute()
                print("Email labeled and moved.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Main program loop
while True:
    send_auto_replies()

    # Random interval between 45 and 120 seconds
    interval = random.randint(45, 120)
    print(f"Waiting for {interval} seconds...")
    time.sleep(interval)
