from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class USSDView(View):
    def post(self, request, *args, **kwargs):
        # Log the incoming request
        logger.info(f"Incoming request: {request.POST}")

        # Parse incoming request data
        session_id = request.POST.get('sessionId', '')
        service_code = request.POST.get('serviceCode', '')
        phone_number = request.POST.get('phoneNumber', '')
        text = request.POST.get('text', '')

        # Generate response based on user input
        response = self.handle_ussd(session_id, service_code, phone_number, text)
        
        # Log the response
        logger.info(f"Response: {response}")

        # Return the response
        return HttpResponse(response, content_type='text/plain')

    def handle_ussd(self, session_id, service_code, phone_number, text):
        text_array = text.split('*')
        user_response = text_array[-1]

        if text == '':
            return 'CON Welcome to NASDAC Money Global\n1. Send Money\n2. Receive Money\n3. Account\n4. Learn More'
        elif user_response == '1':  # Send Money
            return self.handle_send_money(text_array)
        elif user_response == '2':  # Receive Money
            return self.handle_receive_money(text_array)
        elif user_response == '3':  # Account
            return self.handle_account(text_array)
        elif user_response == '4':  # Learn More
            return self.handle_learn_more(text_array)
        else:
            return 'END Invalid option'

    def handle_send_money(self, text_array):
        steps = len(text_array)
        if steps == 1:
            return 'CON Enter the recipient\'s phone number'
        elif steps == 2:
            return 'CON Enter the amount to send'
        elif steps == 3:
            return 'CON Enter your PIN to confirm'
        elif steps == 4:
            phone = text_array[1]
            amount = text_array[2]
            return f'CON You are sending ${amount} to {phone}\n1. Confirm\n2. Cancel'
        elif steps == 5:
            if text_array[4] == '1':
                return 'END Transfer successful'
            elif text_array[4] == '2' or text_array[4] == '#':
                return 'END Transfer canceled'
            else:
                return 'END Invalid option'
        else:
            return 'END Invalid option'

    def handle_receive_money(self, text_array):
        if len(text_array) == 1:
            return 'CON Enter the agent\'s number'
        elif len(text_array) == 2:
            agent_number = text_array[1]
            return f'END Agent {agent_number} is ready to send you money.'
        else:
            return 'END Invalid option'

    def handle_account(self, text_array):
        if len(text_array) == 1:
            return 'CON 1. Check Balance\n2. Change PIN\n3. View Transactions\n4. Set Balance Alert\n5. Set Transaction Limit\n6. Manage Subscriptions\n7. Select Account'
        elif len(text_array) == 2:
            if text_array[1] == '1':
                return 'END Your balance is $100'
            elif text_array[1] == '2':
                return 'CON Enter current PIN'
            elif text_array[1] == '3':
                return 'END Your last transactions: [List of recent transactions]'
            elif text_array[1] == '4':
                return 'CON Set balance alert threshold (e.g., $50)'
            elif text_array[1] == '5':
                return 'CON Set transaction limit (e.g., $1000)'
            elif text_array[1] == '6':
                return 'CON Manage subscriptions: 1. View subscriptions 2. Cancel subscription'
            elif text_array[1] == '7':
                return 'CON Select account: 1. Account 1 2. Account 2'
            else:
                return 'END Invalid option'
        elif len(text_array) == 3:
            return 'CON Enter new PIN'
        elif len(text_array) == 4:
            return 'CON Confirm new PIN'
        elif len(text_array) == 5:
            return 'END PIN change successful'
        else:
            return 'END Invalid option'

    def handle_learn_more(self, text_array):
        if len(text_array) == 1:
            return 'CON 1. Contact Support\n2. FAQs'
        elif len(text_array) == 2:
            if text_array[1] == '1':
                return 'END Contact customer support at 123-456-7890 or visit our website for more help.'
            elif text_array[1] == '2':
                return 'END FAQs: 1. How to send money? 2. How to receive money? 3. How to change PIN?'
            else:
                return 'END Invalid option'
        else:
            return 'END Invalid option'
