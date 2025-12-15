import resend
from dotenv import load_dotenv
import os

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

params: resend.Emails.SendParams = {
  "from": "Acme <onboarding@resend.dev>",
  "to": ["lucascaixeta02@gmail.com"],
  "subject": "hello world",
  "html": "<p>it works!</p>"
}


if __name__=="__main__":
    email = resend.Emails.send(params)
    print(email)