"""Module providing a Petzi request example."""
import datetime
import hmac

# Replace with the actual secret
secret = b"secret"

# Replace with the actual body
body = '''
{
   "event":"ticket_created",
   "details":{
      "ticket":{
         "number":"XXXX2941J6SY",
         "type":"online_presale",
         "title":"My Parent Ticket",
         "category":"My Category",
         "eventId":12345,
         "event":"Event name",
         "cancellationReason":"",
         "sessions":[
            {
               "name":"Session name",
               "date":"2023-04-28",
               "time":"19:00:00",
               "doors":"20:00:00",
               "location":{
                  "name":"location",
                  "street":"2960 Curtis Course Suite 823",
                  "city":"East Monicaborough",
                  "postcode":"84458"
               }
            }
         ],
         "promoter":"Member name",
         "price":{
            "amount":"10.00",
            "currency":"CHF"
         }
      },
      "buyer":{
         "role":"customer",
         "firstName":"Jane",
         "lastName":"Doe",
         "postcode":"1234"
      }
   }
}
'''

# Replace with the actual Petzi-Signature header value
signature_with_timestamp = "t=1679476923,v1=638c968c5ebfb7542e08c3fda7fea77be59e5517b18a89e8c9906ed6b9a3deb9"

# Step 1: split the header
signature_parts = dict(part.split("=") for part in signature_with_timestamp.split(","))

# Step 2: prepare the signed body string
body_to_sign = f'{signature_parts["t"]}.{body}'.encode()

# Step 3: compute the expected signature
expected_signature = hmac.new(secret, body_to_sign, "sha256").hexdigest()

# Step 4: compare the signatures
assert hmac.compare_digest(expected_signature, signature_parts["v1"])

# Step 5: reject old messages
time_delta = datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(int(signature_parts["t"]))
assert time_delta.total_seconds() <= 30