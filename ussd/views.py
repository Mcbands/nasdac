from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests

# Sample user balances and PINs (in practice, use a database)
user_data = {
    '0764336438': {'balance': 1000, 'pin': '1234', 'attempts': 0, 'locked': False},  # Example user data
}

@csrf_exempt
def ussd_view(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        service_code = request.POST.get('serviceCode')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text', '')

        response_text = process_ussd_request(session_id, service_code, phone_number, text)
        
        return HttpResponse(response_text)
    return HttpResponse("END Invalid Request Method")

def process_ussd_request(session_id, service_code, phone_number, text):
    user_response = text.split('*')

    if text == "":
        return main_menu()
    elif user_response[0] == "1":
        return send_money(session_id, service_code, phone_number, user_response[1:])
    elif user_response[0] == "2":
        return withdraw_money(session_id, service_code, phone_number, user_response[1:])
    elif user_response[0] == "3":
        return account_menu(session_id, service_code, phone_number, user_response[1:])
    elif user_response[0] == "4":
        return learn_more(session_id, service_code, phone_number, user_response[1:])
    else:
        return "END Invalid input. Please try again."

def main_menu():
    return "CON Welcome to NASDAC Money Global\n1. Send Money\n2. Withdraw Money\n3. Account\n4. Learn More"

def send_money(session_id, service_code, phone_number, user_response):
    if phone_number not in user_data:
        return "END User not found."

    user = user_data[phone_number]

    if user['locked']:
        return "END Your account is locked due to multiple failed PIN attempts."

    if len(user_response) == 0:
        return "CON Enter the recipient's phone number"
    elif len(user_response) == 1:
        return "CON Enter the amount to send"
    elif len(user_response) == 2:
        return "CON Enter your PIN to confirm"
    elif len(user_response) == 3:
        recipient_phone_number = user_response[0]
        amount = float(user_response[1])
        pin = user_response[2]

        # Check PIN and balance
        if pin != user['pin']:
            user['attempts'] = user.get('attempts', 0) + 1
            if user['attempts'] >= 3:
                user['locked'] = True
                return "END Incorrect PIN. Your account is locked due to multiple failed attempts."
            else:
                return "CON Incorrect PIN. Attempt {}/3".format(user['attempts'])
        
        # Reset attempts after successful PIN entry
        user['attempts'] = 0
        
        if user['balance'] < amount:
            return "END Insufficient balance."

        # Update balance
        user['balance'] -= amount

        # Send request to FLARES
        flares_response = send_request_to_flares(phone_number, recipient_phone_number, amount, pin, session_id)
        
        if flares_response.status_code == 200:
            return "END Transfer successful. New balance: ${:.2f}".format(user['balance'])
        else:
            # Revert balance on failure
            user['balance'] += amount
            return "END Transfer failed. Please try again."

def withdraw_money(session_id, service_code, phone_number, user_response):
    if phone_number not in user_data:
        return "END User not found."

    user = user_data[phone_number]

    if user['locked']:
        return "END Your account is locked due to multiple failed PIN attempts."

    if len(user_response) == 0:
        return "CON Enter the amount to withdraw"
    elif len(user_response) == 1:
        # Prompt for PIN
        user['attempts'] = user.get('attempts', 0) + 1
        return "CON Enter your PIN to confirm. Attempt {}/3".format(user['attempts'])
    elif len(user_response) == 2:
        amount = float(user_response[0])
        pin = user_response[1]

        # Check PIN and balance
        if pin != user['pin']:
            if user['attempts'] >= 3:
                # Lock the account and cancel transaction
                user['locked'] = True
                return "END Incorrect PIN. Your account is locked due to multiple failed attempts."

            user['attempts'] += 1
            return "CON Incorrect PIN. Attempt {}/3".format(user['attempts'])
        
        if user['balance'] < amount:
            return "END Insufficient balance."

        # Update balance
        user['balance'] -= amount

        # Reset attempts after successful transaction
        user['attempts'] = 0

        return "END Withdrawal successful. New balance: ${:.2f}".format(user['balance'])

def account_menu(session_id, service_code, phone_number, user_response):
    if phone_number not in user_data:
        return "END User not found."

    user = user_data[phone_number]

    if user['locked']:
        return "END Your account is locked due to multiple failed PIN attempts."

    if len(user_response) == 0:
        return "CON Account Menu\n1. Check Balance\n2. Change PIN"
    elif user_response[0] == "1":
        return "END Your balance is ${:.2f}".format(user['balance'])
    elif user_response[0] == "2":
        return "CON Enter current PIN"

    # Add PIN change logic here if needed

def learn_more(session_id, service_code, phone_number, user_response):
    return "END For more information, contact support."

def send_request_to_flares(msisdn, recipient_phone_number, amount, pin, session_id):
    url = "https://flares.example.com/api/endpoint"
    params = {
        'MSISDN': msisdn,
        'Recipient': recipient_phone_number,
        'Amount': amount,
        'PIN': pin,
        'SessionId': session_id,
        'NewRequest': 1,
        'ConnectionType': 0,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(url, params=params, headers=headers)
    return response
