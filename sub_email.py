import smtplib
import pymongo
from bson import ObjectId
from datetime import datetime


def send_expiry_email(user_email):
    gmail_user = 'jennifermorphy8@gmail.com'
    gmail_password = 'zzyk zccc hxwo jrrx'

    sent_from = gmail_user
    to = user_email
    subject = 'Membership Expiry Notification'
    body = 'Dear user,\n your membership is expiring soon. Renew now to continue enjoying our services.'
    message = 'Subject: {}\n\n{}'.format(subject, body)
   
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, message)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)

try:
    mongo = pymongo.MongoClient(
        host="localhost",
        port=27017,
        serverSelectionTimeoutMS=1000
    )
    db = mongo.sonic_bilss
    mongo.server_info()
    users = db['user']

except:
    print("ERROR - cannot connect to db")

# user_id = ObjectId(session.get('user_id'))

def check(user_id):
    print("checking userid:",user_id)
    # user_id = ObjectId("654ec8ed2bb4dab2321bc7d6")
    updated_user = users.find_one({'_id': user_id})
    end_date= updated_user['end_date']
    membership = updated_user['membership']
    user_email = updated_user['user_email']

    if membership != 'no membership':
        days_until_expiry = (end_date - datetime.utcnow()).days
        print(days_until_expiry)

        if 0 <= days_until_expiry <= 7:
            send_expiry_email(user_email)
        else :
            print("time")

