from fastapi import APIRouter
from config.db import conn,get_db
from models.models import USER
from schemas.schemas import *
from fastapi import Depends,status
from sqlalchemy.orm.session import Session
from fastapi import WebSocket , FastAPI, Form, Response, status, HTTPException,Depends, APIRouter
from datetime import datetime
import os
from passlib.context import CryptContext
from Token import create_access_token
from oauth2 import get_current_user
import bcrypt
from sqlalchemy import update

from sqlalchemy.sql import select
from datetime import datetime, timedelta
from fastapi import HTTPException

import os
from dotenv import load_dotenv

load_dotenv('.env')


current_datetime = datetime.now()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user =APIRouter(tags=['REGISTRATION'])
userupdate =APIRouter(tags=['USER UPDATE'])
reset =APIRouter(tags=['RESET PASSWORD'])
Login = APIRouter(tags=["LOGIN"])


# from fastapi.security import OAuth2PasswordRequestForm
# @auth_router.post("/login")
# async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     existing_user = db.query(USER).filter(USER.c.email == user.username).first()
    
#     if existing_user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     if not pwd_context.verify(user.password, existing_user.password):
#         raise HTTPException(status_code=401, detail="Incorrect password")
#     access_token = create_access_token(
#         data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
 



from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import smtplib
import random
import string

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):
    smtp_server = os.getenv('smtp_server')
    smtp_port = os.getenv('smtp_port')
    smtp_username = os.getenv('smtp_username')
    smtp_password = os.getenv('smtp_password')
    sender_email = os.getenv('sender_email')

    subject = "OTP Verification"
    message = f"Your OTP for email verification is: {otp}"
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
    server.quit()



@user.post("/register/")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(USER).filter(USER.c.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Generate an OTP
    emailotp = generate_otp()
    send_otp_email(user.email, emailotp)
    hashed_password = pwd_context.hash(user.password)
    # Create a new instance of the User model for the new user
    new_user = {
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email,
        "phone_number":user.phone_number,
        "password":hashed_password,
        "emailotp":emailotp,
    }

    db.execute(USER.insert().values(new_user))
    db.commit()
    return {"message": "Registration successful. Check your email for OTP"}



from fastapi import HTTPException, Path, Query
from fastapi import HTTPException, Query

@user.post("/verify-emailotp/")
async def EmailVerification(email: str = Query(..., title="User's email"), emailotp: str = Query(..., title="Email OTP"), db: Session = Depends(get_db)):

    user = db.query(USER).filter(USER.c.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    stored_emailotp = user.emailotp

    
    if emailotp != stored_emailotp:
        raise HTTPException(status_code=400, detail="Invalid email OTP")

    db.execute(USER.update().values(is_verified=True).where(USER.c.email == email))
    db.commit()

    return {"message": "Email OTP verified successfully"}




@userupdate.put("/update-user/{email}")
async def update_user_data(email: str, user: UpdateUserData, db: Session = Depends(get_db)):
    # Check if the user with the provided email exists
    existing_user = db.query(USER).filter(USER.c.email == email).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="email not found")
    
    if user.password:
        hashed_password = pwd_context.hash(user.password)
    else:
        hashed_password = existing_user.password
        
    update_query = (
        update(USER).where(USER.c.email == email).values(
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            password=hashed_password,
        )
    )

    
    db.execute(update_query)
    db.commit()

    return {"message": "User data updated successfully"}



@reset.post("/reset-password/")
async def reset_password(email: str, db: Session = Depends(get_db)):
    existing_user = db.query(USER).filter(USER.c.email == email).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    otp = generate_otp()
    
    send_otp_email(email, otp)
    usr = update(USER).where(USER.c.email == email).values(reset_otp=otp)
    db.execute(usr)
    db.commit()

    return {"message": "Password reset OTP sent to your email"}

@reset.post("/reset-password/verify-otp")
async def reset_password_verify_otp(
    email: str,
    otp: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    
    stored_otp = db.query(USER.c.reset_otp).filter(USER.c.email == email).scalar()
    if stored_otp is None:
        raise HTTPException(status_code=404, detail="User not found")

    if otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    
    hashed_password = pwd_context.hash(new_password)
    db.execute(
        USER.update()
        .values(password=hashed_password)
        .where(USER.c.email == email)
    )

    db.commit()

    return {"message": "Password reset successful"}




from twilio.rest import Client
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def send_otp_sms(phone_number, otp):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to='+'+phone_number,
        from_=TWILIO_PHONE_NUMBER,
        body=f"Your OTP for login is: {otp}"
    )
    
    
@Login.post("/send-otp/")
async def request_otp(phone_number: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(USER).filter(USER.c.phone_number == phone_number).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    otp = generate_otp()
    send_otp_sms(phone_number, otp)


    return {"message": "OTP sent successfully"}
    
@Login.post("/login/")
async def login(phone_number: str = Form(...), login_otp: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(USER).filter(USER.c.phone_number == phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="invalid phone number")

    
    stored_login_otp = user.login_otp

    
    if login_otp != stored_login_otp:
        raise HTTPException(status_code=400, detail="Invalid email OTP")

    
    return {"message": "Login successful"}