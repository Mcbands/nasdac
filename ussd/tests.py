from django.test import TestCase, Client
from django.urls import reverse

class USSDTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_welcome_screen(self):
        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('CON Welcome to NASDAC Money Global', response.content.decode())

    def test_send_money_flow(self):
        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('CON Enter the recipient\'s phone number', response.content.decode())

        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': '1*1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('CON Enter the amount to send', response.content.decode())

        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': '1*1234567890*50'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('CON Enter your PIN to confirm', response.content.decode())

        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': '1*1234567890*50*1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('CON You are sending $50 to 1234567890', response.content.decode())

        response = self.client.post(reverse('ussd_view'), {
            'sessionId': '12345',
            'serviceCode': '*123#',
            'phoneNumber': '1234567890',
            'text': '1*1234567890*50*1234*1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('END Transfer successful', response.content.decode())

    # Add more tests for other flows like Receive Money, Account, Learn More, etc.
