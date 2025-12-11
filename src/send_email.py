import resend
from dotenv import load_dotenv
import os

load_dotenv()

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

resend.api_key = RESEND_API_KEY

def send_email(to_email: str, subject: str, html_content: str):
    params: resend.Emails.SendParams = {
        "from": "lucascaixeta02@gmail.com",
        "to": to_email,
        "subject": subject,
        "html": html_content
    }

if __name__=="__main__":
    params = send_email("lucas.abner2000@gmail.com", "Teste de envio de email com Resend", "<strong>Este é um email de teste enviado usando Resend!</strong>")
    response = resend.Emails.send(params)
    print(response.status_code)

    print(response.body)

    print(response.headers)
    print("Email enviado com sucesso!")