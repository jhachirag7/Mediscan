from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
import boto3
from django.contrib.auth.decorators import login_required
import io
from PIL import Image
from PIL import Image, ImageDraw
import threading
from .token import generateToken, TokenGenerator
from uuid import uuid4
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from Mediscan import settings
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
import os
import json
from validate_email import validate_email
from .models import Profile,Medicine,Billing,order
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .hashFile import compute_sha256
from .imageEnhancer import imageEnhance
from .medicalWords import MedicalWords
from .gcp import gcp

from .amazonscrap import amzscrap
from .mgscrap import mgscrap

from gensim.models import Word2Vec
from nltk.util import ngrams

# load the saved model from disk

import nltk
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
#nltk.download('stopwords')

import spacy
from spacy.vocab import Vocab

nlp = spacy.load('en_ner_bionlp13cg_md')

#pre processing
# file_path = os.path.join(settings.BASE_DIR, 'medicine_data.xlsx')
# df=pd.read_excel(file_path)

# df = df.reset_index()

# df['AWS']=df['AWS'].str.lower()
# df['GCP']=df['GCP'].str.lower()
# df['Corrected/original']=df['Corrected/original'].str.lower()

# for index, row in df.iterrows():
#     exists= Medicine.objects.filter(wrong_val=row['AWS']).exists()
#     if not exists:
#         Medicine.objects.create(wrong_val=row['AWS'],right_val=row['Corrected/original'])
#     exists= Medicine.objects.filter(wrong_val=row['GCP']).exists()
#     if not exists:
#         Medicine.objects.create(wrong_val=row['GCP'],right_val=row['Corrected/original'])


medlist=Medicine.objects.all().values_list('right_val')
medlist=set(medlist)
Actual_medlist=[]
for i in medlist:
    Actual_medlist.append(i[0])


def process_text_detection(bucket, document, region):

    #Get the document from S3
    s3_connection = boto3.resource('s3')
                          
    s3_object = s3_connection.Object(bucket,document)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

   
    client = boto3.client('textract', region_name=region)

    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    blocks=response['Blocks']
    image=image.convert('RGB')
    width, height =image.size    
    print ('Detected Document Text')

    medlist=[]
   
    for block in blocks:
        if block['BlockType']!='PAGE':
            #DisplayBlockInformation(block)

            if block['BlockType']=='WORD':

                if 'Text' in block:
                    medlist.append(block['Text'])
    #print(medlist)
    return medlist,image,blocks



def DrawBoundingBox(image,blocks,medlist):
    width, height =image.size
    for block in blocks:
        if block['BlockType']!='PAGE':
        #DisplayBlockInformation(block)

            if block['BlockType']=='WORD':

                if 'Text' in block:
                    if block['Text'].lower() in medlist:
                        draw = ImageDraw.Draw(image)
                        box=block['Geometry']['BoundingBox']
                        left = width * box['Left']
                        top = height * box['Top']
                        draw.rectangle([left,top, left + (width * box['Width']), top +(height * box['Height'])],outline='black',width=3)
    image.show()


def Uploadfile(bucket,document,name):
    s3 = boto3.client("s3")
    s3.upload_file(Filename=document,Bucket=bucket,Key=name,)


def jaccard_similarity(str1, str2, n):
    str1_bigrams = list(ngrams(str1, n))
    str2_bigrams = list(ngrams(str2, n))

    intersection = len(list(set(str1_bigrams).intersection(set(str2_bigrams))))
    union = (len(set(str1_bigrams)) + len(set(str2_bigrams))) - intersection

    return float(intersection) / union


def custom_similarity(word1, word2):
    # Check if the words are in the vocabulary
    if word1 in nlp.vocab and word2 in nlp.vocab:
        # Get the tokens for the words
        token1 = nlp(word1)
        token2 = nlp(word2)

        # Calculate the similarity between the tokens
        similarity = token1.similarity(token2)
        return similarity
    return 0.0




def helper(med_list,MedDict,Medwords):
     for i in med_list:
            i=i.lower()
            exists= Medicine.objects.filter(wrong_val=i).exists() 
            if exists:
                value=Medicine.objects.filter(wrong_val=i).values()
                Medwords.append(i)
                MedDict.append(value[::1][0]['right_val'])
            else:
                exists=Medicine.objects.filter(right_val=i).exists()
                if exists:
                    value=Medicine.objects.filter(right_val=i).values()
                    Medwords.append(i)
                    MedDict.append(value[::1][0]['right_val'])
            if not exists:
                wrd=""
                mx=0.0
                wrd2=""
                mx2=0.0
                for med in Actual_medlist:
                    acc=custom_similarity(i,med)
                    if acc>=mx:
                        mx=acc
                        wrd=med
                    acc2=jaccard_similarity(i,med,1)
                    if acc2>=mx2:
                        mx2=acc2
                        wrd2=med
                if mx>=0.8:
                    MedDict.append(wrd)
                    Medwords.append(i)
                elif mx2>=0.8:
                    MedDict.append(wrd2)
                    Medwords.append(i)


def Pre(doc,name):
    bucket = 'textract-sample2'
    document = doc
    region='ap-south-1'
    Uploadfile(bucket,document,name)
    return process_text_detection(bucket,name,region)


def home(request):
    return render(request,'prescribtion_system/home.html')


@login_required(login_url='/login')
def results(request):
    return render(request,'prescribtion_system/product.html',{"context":""})


''' Image Verify '''

def is_image(img):
    try:
        img.verify()
        return True
    except:
        return False
    

@login_required(login_url='/login')
def history(request):
    if request.method=="GET":
        files=Profile.objects.filter(user=request.user)
        #print(files)
        return render(request,'prescribtion_system/history.html',{'context':files})
    
@login_required(login_url='/login')
def Order(request):
    if request.method=="GET":
        bill=Billing.objects.filter(user=request.user).values_list('uuid')
        bil=[]
        for i in bill:
            bil.append(i[0])
        Bill_price=dict()
        bill_prod=dict()
        for i in bil:
            p=order.objects.filter(uuid=i,user=request.user)
            price=[]
            quantity=[]
            name=[]
            img=[]
            tprice=0
            prod=[]
            pr=p.values_list('price')
            for j in pr:
                price.append(j[0])
            quan=p.values_list('quantity')
            for j in quan:
                quantity.append(j[0])
            naam=p.values_list('name')
            for j in naam:
                name.append(j[0])
            img_url=p.values_list('image')
            for j in img_url:
                img.append(j[0])
            print(price)
            print(quantity)
            print(name)
            print(img)

            for j in range(0,len(price)):
                tprice=tprice+int(price[j])*int(quantity[j])
                prod.append([price[j],quantity[j],name[j],img[j]])
            print(prod)
            bill_prod[i]=prod
            Bill_price[i]=tprice
        print(bill_prod)

        return render(request,'prescribtion_system/order.html',{'context':Bill_price,'data':bill_prod})
    
@login_required(login_url='/login')
def dashboard(request):
    if request.method=="GET":
        bill=Billing.objects.all().values_list('uuid')
        bil=[]
        for i in bill:
            bil.append(i[0])

        Bill_price=dict()
        
        for i in bil:
            p=order.objects.filter(uuid=i)
            price=[]
            quantity=[]
            tprice=0
            pr=p.values_list('price')
            for j in pr:
                price.append(j[0])
            quan=p.values_list('quantity')
            for j in quan:
                quantity.append(j[0])
            for j, (price, quantity) in enumerate(zip(price, quantity)):
                tprice=tprice+price*quantity
            Bill_price[i]=tprice
        print(Bill_price)

        
        return render(request,'prescribtion_system/dashboard.html',{'context':Bill_price})
    
@login_required(login_url='/login')
def payment(request):
    if request.method=="GET":
        return render(request,'prescribtion_system/payment.html')



@login_required(login_url='/login')
def dropbox(request):
    if request.method=="GET":
        return render(request,'prescribtion_system/dropbox_new.html')
    else:
        image = request.FILES["files"]
        #image Enhancement
        if is_image(image):
            image=imageEnhance(image)

        # computing hash
        hsh=compute_sha256(image)

        ext =image.name.split('.')[-1]
        image.name=f'{hsh}.{ext}'
        
        exists = Profile.objects.filter(user=request.user,hash_val=str(hsh)).exists()
        if not exists:
            Profile.objects.create(user=request.user,image=image,hash_val=hsh)

        name=str(image)
        path=os.path.join(settings.BASE_DIR, 'media\pics\\'+name)
        medlist,img,blocks=Pre(path,name)
        textlist=gcp(path)

        med_list=[]

        gcp_list=[]

        stops = set(stopwords.words('english'))
        for i in range(len(medlist)):
            if medlist[i] not in stops and medlist[i].isalpha():
                med_list.append(medlist[i])
        

        for i in range(len(textlist)):
            if textlist[i] not in stops and textlist[i].isalpha():
                gcp_list.append(textlist[i])
        

        #print(med_list)
        #print(gcp_list)
        MedDict=[]

        Medwords=[]

        helper(med_list,MedDict,Medwords)
        helper(gcp_list,MedDict,Medwords)


       

        Medwords=set(Medwords)

        #print(Medwords)

        d={"title":[], "price":[],'links':[],'product':[]}
        df = pd.DataFrame.from_dict(d)
        df['title'].replace('', np.nan, inplace=True)
        df = df.dropna(subset=['title'])

        HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
        for key in MedDict:
            URL="https://www.amazon.in/s?k="+key
            d1=amzscrap(URL,HEADERS)
            URL="https://www.1mg.com/search/all?name="+key
            d2=mgscrap(URL,HEADERS)
            df=pd.concat([df,d1]).drop_duplicates().reset_index(drop=True)
            df=pd.concat([df,d2]).drop_duplicates().reset_index(drop=True)

        #print(df['links'])
        

        #DrawBoundingBox(img,blocks,Medwords)

        return render(request, "prescribtion_system/product.html",{'context':df})


# Login Signup

'''   Multi Threading  '''

class EmailTread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


''' Login '''
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('dashboard')
            return redirect('dropbox')
        return render(request, "prescribtion_system/Sign-Login.html")

    def post(self, request):
        username = request.POST['username']
        passwaord = request.POST['password']

        user = auth.authenticate(username=username, password=passwaord)

        if user:
            if user.is_active:
                auth.login(request, user)
                if user.is_superuser:
                    return redirect('dashboard')
                messages.success(request, 'Welcome ' +
                                 user.username+' you are now logged in')
                return redirect('dropbox')

            messages.error(request, 'Account is not verified')
            return render(request, 'prescribtion_system/Sign-Login.html')
        messages.error(request, 'Inavlid credentials')
        return render(request, 'prescribtion_system/Sign-Login.html')



'''  Logout   '''
class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out")
        return redirect('login')

'''      Usr Validate     '''
class UsernameValidate(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'usernme should only conatin alphanumeric'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username already taken'}, status=409)
        return JsonResponse({'username_valid': True})
    


class billing(View):
    def post(self, request):
        data = json.loads(request.body)
        cardbill = data['cardbill']
        Medlist=data['Medlist']
        print(cardbill);
        print(Medlist);
        uuid=str(uuid4())
        Billing.objects.create(user=request.user,name=cardbill[0]['name'],email=cardbill[0]['email'],
                               address=cardbill[0]['addr'],city=cardbill[0]['city'],state=cardbill[0]['state'],
                               zip=cardbill[0]['zip'],namecard=cardbill[0]['namecard'],cardnumber=cardbill[0]['cardnum'],month=cardbill[0]['month'],
                               year=cardbill[0]['year'],cvv=cardbill[0]['cvv'],uuid=uuid)

        
        for i in range(0,len(Medlist)):
            order.objects.create(user=request.user,uuid=uuid,image=Medlist[i]['image'],name=Medlist[i]['name'],price=Medlist[i]['price'],quantity=Medlist[i]['quantity'])

        
        return JsonResponse({'username_valid': True})


''' Email validate '''
class EmailValidate(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Mail format is not correct'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'email already taken'}, status=409)
        return JsonResponse({'email_valid': True})

'''     Register      '''
class RegistrationView(View):
    def get(self, request):
        return render(request, 'prescribtion_system/Sign-Login.html')

    def post(self, request):

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldVal': request.POST,
        }
        user = User.objects.create_user(
            username=username, password=password, email=email)
        user.is_active = False
        user.save()

        # mail sending

        current_site = get_current_site(request)
        email_subject = "Confirm Your email @MediScan!!"

        message = render_to_string('prescribtion_system/email_confirmation.html', {
            'name': user.username,
            'emai': user.email,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generateToken.make_token(user),
        })
        emails = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        EmailTread(emails).start()
        messages.success(
            request, "Account successfully created for activation confirm your mail from your accounts")
        return render(request, 'prescribtion_system/Sign-Login.html')


'''      Email '''
class EmailActivation(View):
    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generateToken.check_token(user, token):
            user.is_active = True
            user.save()
            # user.auth.login(request, user)
            return render(request, "prescribtion_system/Sign-Login.html")
        else:
            return render(request, "prescribtion_system/actiavtion_failed.html")

'''    Reset Password         '''
class ResetPassword(View):
    def get(self, request):
        return render(request, 'prescribtion_system/reset_password.html')

    def post(self, request):
        email = request.POST["email"]
        context = {
            'fieldVal': request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Provide valid email address')
            return render(request, 'prescribtion_system/reset_password.html', context)
        user = User.objects.filter(email=email)
        if user.exists():
            current_site = get_current_site(request)
            email_subject = "Reset Password @MediScan!!"

            message = render_to_string('prescribtion_system/password_confirmation.html', {
                'name': user[0],
                'emai': email,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            })
            email = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user[0].email],
            )
            EmailTread(email).start()
            messages.warning(request, 'Reset link has been sent to your email')
            return render(request, 'prescribtion_system/reset_password.html', context)
        messages.error(request, 'No user with this email address')
        return render(request, 'prescribtion_system/reset_password.html', context)

'''      Password          '''
class PasswordConfirm(View):
    def get(self, request, uid64, token):
        context = {}
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
            context = {
                "uid64": uid64,
                "token": token
            }
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            return render(request, "prescribtion_system/set_new_password.html", context=context)
        else:
            messages.error(request, "link is expired")
            return render(request, "prescribtion_system/reset_password.html")

    def post(self, request, uid64, token):
        password = request.POST['password']
        password1 = request.POST['password1']
        context = {
            "uid64": uid64,
            "token": token
        }
        if password != password1:
            messages.error(request, "Password do not match")
            return render(request, "prescribtion_system/set_new_password.html", context)
        if len(password) < 8:
            messages.error(request, 'Password too short')
            return render(request, "prescribtion_system/set_new_password.html", context)
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None:
            user.set_password(password)
            user.save()
            messages.success(request, "Password changed successfully")
            return render(request, "prescribtion_system/Sign-Login.html")
        messages.error(request, "something went wrong")
        return redirect("reset-password")