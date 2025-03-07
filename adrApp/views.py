from django.core.cache import cache
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg') 
from django.db.models import Count
import io
from .decorators import check_status 
from twilio.rest import Client
from django.conf import settings
import qrcode
from django.http import HttpResponse
import requests
from datetime import datetime
import json
# Create your views here.
from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPDigestAuth
import json
import logging
load_dotenv()

# Setting up the logger
logger = logging.getLogger(__name__)

def call_another_api(auth_code, number):
    api_url = "http://192.168.157.120:80/api/send_sms"  # The actual URL of the API

    # Digest Authentication credentials
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")

    # Request body
    request_body = {
        "text": f"ADR \nKodi PIN per Verifikimin tuaj : {auth_code}",
        "param": [{"number": number}]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Sending the POST request with Digest Authentication
        response = requests.post(api_url, json=request_body, headers=headers, auth=HTTPDigestAuth(username, password))

        if response.status_code == 200:
            logger.info(f">>>>>O.o GENERALWEBAPI {response.status_code} Requesting for access to web code sent successfully")
            # Process the response if needed
            response_body = response.json()  # If response is in JSON format
            # Handle the response body as needed
        else:
            logger.error(f">>>>>O.o GENERALWEBAPI {response.status_code} Error calling another API: {response.status_code} - {response.reason}")
            print(f"Error calling another API: {response.status_code} - {response.reason}")
    except Exception as e:
        logger.error(f">>>>>O.o GENERALWEBAPI Error occurred: {str(e)}")
        print(f"Error occurred: {str(e)}")


def generate_qr_code(request, guid):
    # Ensure that the URL is correctly formatted with the actual GUID
    url = f"http://192.168.10.215:8000/{guid}/"  # The GUID is now part of the actual URL

    # Generate the QR code
    qr = qrcode.make(url)

    # Define the directory to save the QR code images
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_code_anetaret')  # Save to media/qr_code_anetaret
    if not os.path.exists(qr_code_dir):  # Create the directory if it doesn't exist
        os.makedirs(qr_code_dir)

    # Define the file path for the QR code image (save as GUID.png)
    qr_image_path = os.path.join(qr_code_dir, f'{guid}.png')

    # Save the generated QR code image to the file system
    qr.save(qr_image_path)

    # Return the path where the QR code is saved (for debugging or further use)
    return HttpResponse(f"QR Code for GUID {guid} saved at: {qr_image_path}", content_type="text/plain")


def login_view(request, guid=None):  # Capture GUID from URL if provided
    if not request.user.is_authenticated:  # Check if the user is logged in
        if request.method == 'POST':
            user_id = request.POST.get('id')  # Get user ID (to check the OTP)
            otp_entered = request.POST.get('otp')  # Get the OTP entered by the user

            if otp_entered:  # If OTP is entered, check it
                try:
                    user = Anetaret.objects.get(id=user_id)
                    if user.otp_code and int(otp_entered) == user.otp_code:
                        # OTP is correct, log in the user
                        request.session['user_id'] = user_id  # Store user ID in session
                        user.otp_code = None  # Clear OTP code after successful login
                        user.save()  # Save user without OTP code
                        messages.success(request, "Login successful!")
                        return redirect('home')  # Redirect to home if OTP is correct
                    else:
                        messages.error(request, "Invalid OTP. Try again.")
                        return render(request, 'login.html', {'show_otp': True, 'user_id': user_id})

                except Anetaret.DoesNotExist:
                    messages.error(request, 'User not found.')
                    return redirect('login')  # Redirect if the user does not exist

            return render(request, 'login.html', {'show_otp': True, 'user_id': user_id})

        else:  # If the request method is GET, initiate the OTP process
            try:
                user = Anetaret.objects.get(guid=guid)  # Get the user by GUID

                # Generate a random 6-digit OTP
                otp = random.randint(100000, 999999)
                user.otp_code = otp  # Save OTP to the database
                user.save()  # Save OTP code to user

                # Send OTP to the user's phone using the external API
                call_another_api(otp, user.nr_tel)  # Send OTP using your own API

                messages.success(request, "OTP has been sent to your phone.")
                return render(request, 'login.html', {'show_otp': True, 'user_id': user.id})  # Show the OTP input form

            except Anetaret.DoesNotExist:
                messages.error(request, 'Invalid login link.')
                return redirect('login')  # Redirect if GUID is invalid

    else:  # If the user is already logged in, redirect to home
        return redirect('home')



def home(request):

    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # If the user ID doesn't exist, we can handle it gracefully

       
    context = {"user": user}
    return render(request, "home.html", context)








@check_status
def propozimet(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            user = None  # If the user ID doesn't exist, handle it gracefully

    if request.method == "POST" and user:
        text_input = request.POST.get("textInput")
        category = request.POST.get("choice1")
        cv = request.FILES.get("cv") if category == "option1" else None


        if text_input and category:
            Propozimet.objects.create(user=user, text=text_input, category=category, cv=cv)
            
            return redirect("propozimet")  # Redirect to avoid form resubmission issues

    context = {"user": user}
    return render(request, "propozimet.html", context)





@check_status 
def statuti(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # If the user ID doesn't exist, we can handle it gracefully

       
    context = {"user": user}
    return render(request,"statuti.html",context)

@check_status
def propozimet1(request):
    user = None
    user_id = request.session.get('user_id')
    if user_id:
        user = Anetaret.objects.filter(id=user_id).first()  # More efficient lookup

    category_filter = request.GET.get('category', '')  # Get selected category

    # Use select_related to optimize foreign key lookups
    propozimet_list = Propozimet.objects.all()
    if category_filter:
        propozimet_list = propozimet_list.filter(category=category_filter)

    # Preload vote counts to avoid repeated queries
    vote_counts = Propozimet_per_Aprovim.objects.filter(propozim__in=propozimet_list).values(
        'propozim_id', 'choice'
    ).annotate(count=Count('choice'))

    # Structure vote data in a dictionary
    vote_data = {}
    for vote in vote_counts:
        propozim_id = vote['propozim_id']
        choice = vote['choice']
        count = vote['count']
        if propozim_id not in vote_data:
            vote_data[propozim_id] = {'Po': 0, 'Jo': 0}
        vote_data[propozim_id][choice] = count

    # Generate vote chart only when needed
    def generate_vote_chart(propozim_id):
        votes = vote_data.get(propozim_id, {'Po': 0, 'Jo': 0})
        po_votes, jo_votes = votes['Po'], votes['Jo']

        fig, ax = plt.subplots()
        ax.bar(['Po', 'Jo'], [po_votes, jo_votes], color=['green', 'red'])
        ax.set_title(f'Rezultatet e votave ')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return img_data

    # Handle voting form submission
    if request.method == "POST":
        propozim_id = request.POST.get("propozim_id")
        choice = request.POST.get(f"agree_{propozim_id}")

        if propozim_id and choice:
            propozim = Propozimet.objects.get(id=propozim_id)

            time_difference = timezone.now() - propozim.created_at

            if time_difference <= timedelta(hours=48):
                existing_vote = Propozimet_per_Aprovim.objects.filter(propozim = propozim,user= user).exists()
                if not existing_vote:

                    Propozimet_per_Aprovim.objects.update_or_create(propozim=propozim,user=user,defaults={"choice": choice})
            return redirect("propozimet1")
        else:
            return redirect("propozimet1")


    # Prepare proposals for rendering
    for propozim in propozimet_list:
        propozim.vote_chart = generate_vote_chart(propozim.id)
        propozim.vote_submitted = Propozimet_per_Aprovim.objects.filter(propozim=propozim, user=user).exists()


        time_difference = timezone.now() - propozim.created_at
        propozim.can_vote = time_difference <= timedelta(hours=48) and not propozim.vote_submitted

    # If voting is still possible, calculate the remaining time in seconds
        if propozim.can_vote:
            time_left_seconds = (timedelta(hours=48) - time_difference).total_seconds()
            propozim.time_left_seconds = time_left_seconds  # Pass remaining time in seconds
        else:
            propozim.time_left_seconds = 0  # Time has expired

    context = {
        "user": user,
        "propozimet_list": propozimet_list,
        "selected_category": category_filter,
    }

    return render(request, "propozimet1.html", context)





# Add this in the propozimet2 view
def generate_vote_chart1(propozim):
    # Get all votes for the given proposal
    votes = Propozimet_per_Votim.objects.filter(propozim=propozim)

    # Count the votes for each choice
    vote_counts = {
        'Po': votes.filter(choice='Po').count(),
        'Jo': votes.filter(choice='Jo').count(),
        'Abstenim': votes.filter(choice='Abstenim').count(),
    }

    total_votes = sum(vote_counts.values())
    if total_votes == 0:
        return None  # No votes yet

    # Calculate percentages
    percentages = {choice: (count / total_votes) * 100 for choice, count in vote_counts.items()}

    # Create a bar chart
    fig, ax = plt.subplots()
    ax.bar(percentages.keys(), percentages.values(), color=['green', 'red', 'gray'])

    ax.set_title("Voting Results")
    ax.set_xlabel("Choices")
    ax.set_ylabel("Percentage (%)")
    ax.set_ylim(0, 100)  # Limit the y-axis from 0 to 100%

    # Save the chart as a PNG image in memory
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convert the image to base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    return img_base64

@check_status
def propozimet2(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully

    current_time = timezone.now()
    propozimet_per_aprovim_list = Propozimet_per_Aprovim.objects.all()
    propozimet_data = {}

    for propozim in propozimet_per_aprovim_list:
        time_difference = current_time - propozim.propozim.created_at

        is_expired = time_difference > timedelta(hours=120)



        # Get vote counts for each choice
        vote_counts = Propozimet_per_Aprovim.objects.filter(propozim=propozim.propozim).values('choice').annotate(count=Count('choice'))

        po_votes = next((vote['count'] for vote in vote_counts if vote['choice'] == 'Po'), 0)
        jo_votes = next((vote['count'] for vote in vote_counts if vote['choice'] == 'Jo'), 0)
        total_votes = po_votes + jo_votes

        if total_votes == 0:
            continue  # Skip proposals with no votes

        po_percentage = (po_votes / total_votes) * 100

        if po_percentage > 50:  # Only show proposals with >50% "Po" votes
            has_voted = Propozimet_per_Votim.objects.filter(propozim=propozim.propozim, user=user).exists() if user else False

            chart_img_base64 = generate_vote_chart1(propozim.propozim)

            propozimet_data[propozim.propozim.id] = {
                'propozim': propozim.propozim,
                'po_percentage': po_percentage,
                'jo_percentage': (jo_votes / total_votes * 100),
                'chart_img_base64': chart_img_base64,
                'has_voted': has_voted,
                'can_vote': False,  # Voting is finished
                'is_expired': is_expired,
            }

    if request.method == "POST":
        propozim_id = request.POST.get("propozim_id")
        choice = request.POST.get(f"agree_{propozim_id}")

        if propozim_id and choice and user:
            propozim = Propozimet.objects.get(id=propozim_id)

            if not Propozimet_per_Votim.objects.filter(propozim=propozim, user=user).exists():
                vote = Propozimet_per_Votim.objects.create(propozim=propozim, user=user, choice=choice)
                vote.save()

            return redirect("propozimet2")

    context = {
        "user": user,
        "propozimet_data": propozimet_data,  # Include only valid proposals
    }
    return render(request, "propozimet2.html", context)



@check_status
def propozimet3(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully

    current_time = timezone.now()
    propozimet_per_aprovim_list = Propozimet_per_Votim.objects.all()
 
    
    expired_proposals_po = []
    expired_proposals_jo = []

    unique_proposals = {}

    for propozim in propozimet_per_aprovim_list:
        time_difference = current_time - propozim.propozim.created_at

        # Skip proposals that are not expired yet
        if time_difference <= timedelta(hours=120):
            continue

        # Get vote counts for "Po", "Jo", and "Abstenim"
        vote_counts = Propozimet_per_Aprovim.objects.filter(propozim=propozim.propozim).values('choice').annotate(count=Count('choice'))

        po_votes = next((vote['count'] for vote in vote_counts if vote['choice'] == 'Po'), 0)
        jo_votes = next((vote['count'] for vote in vote_counts if vote['choice'] == 'Jo'), 0)
        abstenim_votes = next((vote['count'] for vote in vote_counts if vote['choice'] == 'Abstenim'), 0)

        # Only add the proposal if it's not already in the dictionary (to avoid duplicates)
        if propozim.propozim.id not in unique_proposals:
            if po_votes != jo_votes:
            # If "Po" or "Jo" is greater, group them accordingly
                if po_votes > jo_votes and (po_votes > 0 or jo_votes > 0):
                    expired_proposals_po.append(propozim)
                elif jo_votes > po_votes and (po_votes > 0 or jo_votes > 0):
                    expired_proposals_jo.append(propozim)

            # Store the proposal in the unique_proposals dictionary
            unique_proposals[propozim.propozim.id] = propozim
    context = {
        "user":user,
        "expired_proposals_po": expired_proposals_po,
        "expired_proposals_jo": expired_proposals_jo,
    }
    return render(request, "propozimet3.html", context)




@check_status
def programi(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully
    context ={"user":user,}
    return render(request,"programi.html",context)




def axhendaeventeve(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully

    events = Event.objects.all()  # Fetch all events from the database

    context = {
        "user": user,
        "events": events,
    }

    return render(request, "axhenda_e_eventeve.html", context)


def kandidatdeputet(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully

    kandidet = KandidatPerDeputet.objects.all() 

    context = {
        "user": user,
        "kandidet":kandidet,
    }

    return render(request, "kandidatdeputet.html", context)




def organigrama(request):
    user = None

    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully


    context = {
        "user": user,
    }

    return render(request, "organigrama.html", context)


def asambleja(request):
    user = None
    anetaret_aktive = Anetaret.objects.filter(status_i_kartës='Aktiv')
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully


    context = {
        "user": user,
        "anetaret_aktive": anetaret_aktive,
    }
    return render(request,"asambleja.html",context)    


def sekretaria(request):
    user = None

    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully


    context = {
        "user": user,

    }
    return render(request,"sekretaria.html",context) 


def koordinatori(request):
    user = None

    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully


    context = {
        "user": user,

    }
    return render(request,"koordinatori.html",context)   


def komunikimezyrtare(request):
    user = None
    komunikimezyrtare= Komunikime_Zyrtare.objects.all()
    if 'user_id' in request.session:
        try:
            user = Anetaret.objects.get(id=request.session['user_id'])
        except Anetaret.DoesNotExist:
            pass  # Handle missing user gracefully



    context = {
        "user": user,
        "komunikimezyrtare":komunikimezyrtare,
    }
    return render(request,"komunikimezyrtare.html",context)   