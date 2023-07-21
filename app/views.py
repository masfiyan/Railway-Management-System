from django.shortcuts import render, redirect
from django.views import View
from app.models import CustomUser, Feedback, ContactNumber, Train, Station, ClassType, Booking, BillingInfo, Payment, Ticket
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.forms import TrainForm
from datetime import timezone, datetime, timedelta
from icecream import ic
import sqlite3
from django.db import connection
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet


# Create your views here.

# homepage view

class QuerySetWrapper:
    def __init__(self, results, attributes):
        self.results = results
        self.attributes = attributes

    def __iter__(self):
        for row in self.results:
            yield self._create_object(row)

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        if isinstance(index, int):
            row = self.results[index]
            return self._create_object(row)
        elif isinstance(index, slice):
            return [self._create_object(row) for row in self.results[index]]

    def _create_object(self, row):
        obj_attrs = {}
        for i, attr in enumerate(self.attributes):
            value = row[i]
            if attr in ['departure_time', 'arrival_time']:
                # Convert time strings to datetime.time objects
                value = datetime.strptime(value, '%H:%M:%S').time()
            obj_attrs[attr] = value
        return type('Train', (), obj_attrs)

class Home(View):
    def get(self, request):
        form = TrainForm
        return render(request, 'home.html', {'form': form})

        
# available train page view

class AvailableTrain(View):
    def get(self, request):
        if request.GET:

            rfrom = request.GET.get('rfrom')
            to = request.GET.get('to')
            date = request.GET.get('date')
            ctype = request.GET.get('ctype')
            adult = request.GET.get('pa')
            child = request.GET.get('pc')
            ic(rfrom,to,ctype)
            #query = ('SELECT name FROM app_station where name = %?;,(rfrom)')  # Replace 'your_table' with the actual table name
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            

            adult = int(adult)
            child = int(child)

            if rfrom == '' or rfrom == 'Select' or to == '' or to == 'Select' \
                    or date == '' or date == 'mm//dd//yyyy' or ctype == '':
                messages.warning(request, 'Please fillup the form properly')
                return redirect('home')

            elif (adult + child) < 1:
                messages.warning(request, 'Please book minimum 1 seat')
                return redirect('home')

            elif (adult + child) > 5:
                messages.warning(request, 'You can book maximum 5 seat')
                return redirect('home')

            else:
                search = Train.objects.filter(source=rfrom, destination=to, class_type=ctype)
                #ic(search)
                #cursor.execute('SELECT app_train.name FROM app_train JOIN app_train_class_type ON app_train.id = app_train_class_type.train_idWHERE app_train_class_type.classtype_id = ?;' ,(ctype,))
                                      #and source_id = ? and destination_id = ?;',(ctype,rfrom,to,))
                query = """
                    SELECT *
                    FROM app_train
                    JOIN app_train_class_type ON app_train.id = app_train_class_type.train_id
                    WHERE app_train_class_type.classtype_id = :ctype and source_id = :rfrom and destination_id = :to;
                    """

                params = {
                    'ctype': ctype,
                    'rfrom': rfrom,
                    'to': to
                    }

                cursor.execute(query, params)
                results = cursor.fetchall()
                ic(results)
                attributes = [column[0] for column in cursor.description]
                search5 = QuerySetWrapper(results, attributes)
               
 
                #class_type = ClassType.objects.get(pk=ctype)
                #ic(class_type)
                cursor.execute('SELECT name,place FROM app_station where id = ?;',(rfrom,))
                source = cursor.fetchall()
                attributes = [column[0] for column in cursor.description]
                source4 = QuerySetWrapper(source,attributes)

                cursor.execute('SELECT name,place FROM app_station where id = ?;',(to,))
                destination2 = cursor.fetchall()
                attributes = [column[0] for column in cursor.description]
                destination3 = QuerySetWrapper(destination2,attributes)

                cursor.execute('select name,price from app_classtype where id = ?;',(ctype,))
                class_type2 = cursor.fetchall()
                attributes = [column[0] for column in cursor.description]
                class_type3 = QuerySetWrapper(class_type2,attributes)

                for i in class_type3:
                    ic(i.price*1)

                ic(len(search5))
                
                
                return render(request, 'available_train.html', {'search': search5, 'source':source4, 'destination':destination3, 'class_type':class_type3})

        else:
            messages.warning(request, 'Find train first to get available train')
            return redirect('home')


#Booking page view

class Bookings(View):
    def get(self, request):
        if request.GET:

            user = request.user
            if user.is_authenticated:
                
                train = request.GET.get('train')
                source = request.GET.get('source')
                destination = request.GET.get('destination')
                date = request.GET.get('date')
                departure = request.GET.get('departure')
                arrival = request.GET.get('arrival')
                tp = request.GET.get('tp')
                pa = request.GET.get('pa')
                pc = request.GET.get('pc')
                ctype = request.GET.get('ctype')
                total_fare = request.GET.get('total_fare')

                #fare_each = ClassType.objects.get(name=ctype)
                conn = sqlite3.connect('db.sqlite3')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM app_classtype where name = ?;',(ctype,))
                fare_each1 = cursor.fetchall()
                attributes = [column[0] for column in cursor.description]
                fare_each2 = QuerySetWrapper(fare_each1,attributes)

                # this is for booking seat according to train seat capacity

                ticket = Ticket.objects.filter(train_name=train, travel_date=date)
                cursor.execute('SELECT count(*) FROM app_ticket where train_name = ? and travel_date = ?;',(train,date,))
                ticket1 = cursor.fetchall()
                

                available_seat = 30 - (ticket1[0])[0]
                print(available_seat)
                tp = int(tp)
                if available_seat >= tp:

                    return render(request, 'booking.html', {'train':train, 'source':source, 'destination':destination, 'date':date, 'departure':departure, 'arrival':arrival, 'tp':tp, 'range_tp':range(tp),'pa':pa, 'pc':pc, 'ctype':ctype, 'total_fare':total_fare, 'fare_each':fare_each2})
                else:
                    messages.warning(request, f"sorry! {available_seat} seat is available for this train. Try again!")
                    return redirect('home')
                
                # this is for booking seat according to train seat capacity (end)
                # else:
                #     messages.warning(request, "sorry! enough seat is not available for this train. Try again!")
                #     return redirect('home')
            else:
                messages.warning(request, "login first to book train")
                return redirect('login')
        else:
            messages.warning(request, 'find a train first!')
            return redirect('home')

    def post(self, request):
        user = request.user
        user_id = request.user.id

        train = request.POST['train']
        source = request.POST['source']
        destination = request.POST['destination']
        travel_date = request.POST['travel_date']
        travel_time = request.POST['departure']
        arrival = request.POST['arrival']
        nop = request.POST['tp']
        adult = request.POST['pa']
        child = request.POST['pc']
        class_type = request.POST['ctype']
        fpp = request.POST['fpp']
        total_fare = request.POST['total_fare']

        email = request.POST['email']
        phone = request.POST['phone']

        pay_method = request.POST['ptype']
        pay_phone = request.POST['pay_phone']
        trxid = request.POST['trxid']
        value = request.POST.getlist('passenger_name[]')
        ic(value)

        # time = Train.objects.get(departure_time=travel_time)
        # travel_time = int(travel_time)
        # time = datetime.strftime(time, "HH:MM[:ss[.uuuuuu]][TZ]")

        # logic for travel_time to store in proper format
        if travel_time == 'midnight':
            travel_time = '0 a.m.'
            time = travel_time.split()
            x = time[0]
            y = time[1]
            x = int(x)
            if not y == 'a.m.':
                x = x + 12
            travel_time = timedelta(hours = x)

        elif travel_time == 'noon':
            travel_time = '12 p.m.'
            time = travel_time.split()
            x = time[0]
            y = time[1]
            x = int(x)
            travel_time = timedelta(hours = x)

        else:
            time = travel_time.split()
            x = time[0]
            y = time[1]
            x = int(x)
            if not y == 'a.m.':
                x = x + 12
            travel_time = timedelta(hours = x)        
        # travel_time logic end
        
        # dt = datetime.strftime("YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]", '2022-04-10 14:30:20')
        # print(dt)
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        #current_date = timezone.localtime(timezone.now(), timezone=timezone.get_current_timezone())
        current_date_str = current_date.strftime('%Y-%m-%d')
        #current_time = timezone.localtime(timezone.now(), timezone=timezone.get_current_timezone()).time()
        current_time_str = current_time.strftime('%H:%M:%S')

        #booking = Booking(user=user, travel_dt=str(travel_date)+ ' ' + str(travel_time), travel_date=travel_date)
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('insert into app_booking (status,booking_date,booking_time,user_id,travel_dt,travel_date) values (?,?,?,?,?,?)',('Confirmed',current_date_str,current_time_str,user_id,str(travel_date)+ ' ' + str(travel_time),travel_date,))
        booking_id = cursor.lastrowid
        conn.commit()

        #booking_detail = BookingDetail(booking=booking, train=train, source=source, destination=destination, travel_date=travel_date, nop=nop, adult=adult, child=child, class_type=class_type, fpp=fpp, total_fare=total_fare, travel_time=str(travel_time), travel_dt=str(travel_date)+ ' ' + str(travel_time))
        
        #billing_info = BillingInfo(booking=booking, user=user, email=email, phone=phone)

        cursor.execute('insert into app_billinginfo (email,phone,booking_id,user_id) values (?,?,?,?)',(email,phone,booking_id,user_id,))
        conn.commit()
        
        #payment = Payment(booking=booking, user=user, pay_amount=total_fare, pay_method=pay_method, phone=pay_phone, trxid=trxid)
        cursor.execute('insert into app_payment (status,pay_amount,pay_method,phone,trxid,booking_id,user_id) values (?,?,?,?,?,?,?)',('Paid',total_fare,pay_method,phone,trxid,booking_id,user_id,))
        conn.commit()
        #booking.save()
        #booking_detail.save()
        #billing_info.save()
        #payment.save()

        # logic to generate ticket
        nop = int(nop)
 
        for i in value:
            cursor.execute('SELECT price FROM app_classtype where name = ?;',(class_type,))
            price = cursor.fetchall()
            cursor.execute('insert into app_ticket(booking_id,class_type,departure,destination,fare,phone,source,train_name,travel_date,user_id,passenger) values (?,?,?,?,?,?,?,?,?,?,?)',(booking_id,class_type,str(travel_time),destination,(price[0])[0],phone,source,train,travel_date,user_id,i,))
            conn.commit()
        # ticket generate logic end
            
        messages.success(request, 'Congratulation! Your booking is successfull')
        return redirect('booking_history')


# booking history page view

class BookingHistory(View):
    def get(self, request):
        user = request.user
        user_id = request.user.id
        if user.is_authenticated:
            #booking = Booking.objects.filter(user=user).order_by('-id')
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM app_booking WHERE user_id = ? ORDER BY id DESC',(user_id,))
            booking1 = cursor.fetchall()
            attributes = [column[0] for column in cursor.description]
            booking2 = QuerySetWrapper(booking1,attributes)
            current_date = datetime.now(timezone.utc)
            
            return render(request, 'booking_history.html', {'booking':booking2, 'current_date':current_date})
        else:
            return redirect('login')


# booking detail page view




# ticket page view

class Tickets(View):
    def get(self, request, pk):
        user = request.user
        user_id = request.user.id
        if user.is_authenticated:
            bookings = Booking.objects.get(id=pk)
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM app_booking WHERE id = ?;',(pk,))
            booking1 = cursor.fetchall()
            attributes = [column[0] for column in cursor.description]
            booking2 = QuerySetWrapper(booking1,attributes)
            if user_id == (booking1[0])[0]:
                #ticket = Ticket.objects.filter(booking=bookings)
                cursor.execute('SELECT * FROM app_ticket WHERE booking_id = ?;',(pk,))
                ticket1 = cursor.fetchall()
                attributes = [column[0] for column in cursor.description]
                ticket2 = QuerySetWrapper(ticket1,attributes)
    

                return render(request, 'ticket.html', {'ticket':ticket2, 'bookings':booking2})
            else:
                messages.warning(request, 'Invalid booking id!')
                return redirect('booking_history')
        else:
            return redirect('login')





# signup for user
from django.contrib.auth.hashers import make_password
def signup(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    else:
        if request.method=="POST":
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            phone = request.POST['phone']        
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            password3 = make_password(password1)

            if password1 != password2:
                messages.warning(request,"Password didn't matched")
                return redirect('signup')
        
            #new_user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone=phone, password=password1)
            #new_user.is_superuser=False
            #new_user.is_staff=False
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO app_customuser (password, is_superuser, username, first_name,is_staff, is_active, date_joined,email, phone, last_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?, ?);',(password3, 0, username, first_name, 0, 1,datetime.now(),email,phone,last_name,))
            conn.commit()
            #new_user.save()
            messages.success(request,"Registration Successfull")
            return redirect("login")
        return render(request, 'signup.html')


# login for admin and user

def user_login(request):
    check = request.user
    if check.is_authenticated:
        return redirect('home')
    else:
            
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username,password=password)
            
            if user is not None:
                login(request,user)
                messages.success(request,"successful logged in")
                return redirect('home')
            else:
                messages.warning(request,"Incorrect username or password")
                return redirect('login')

    response = render(request, 'login.html')
    return HttpResponse(response)


# contact page view

class Contact(View):
    def get(self, request):
        contact = ContactNumber.objects.all()
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM app_contactnumber')
        booking1 = cursor.fetchall()
        attributes = [column[0] for column in cursor.description]
        booking2 = QuerySetWrapper(booking1,attributes)
        return render(request, 'contact.html', {'contact': contact})



# feedback page view

class Feedbacks(View):
    def get(self, request):
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        feedback = Feedback.objects.all().order_by('-id')
        return render(request, 'feedback.html', {'feedback': feedback})

    def post(self, request):
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        user = request.user
        if user.is_authenticated:
            comment = request.POST['feedback']

            if comment == '':
                messages.warning(request, "please write something first and then submit feedback.")
                return redirect('feedback')
            
            else:
                feedback = Feedback(name=user.first_name + ' ' + user.last_name, feedback=comment)
                feedback.save()
                cursor.execute('INSERT INTO app_feedback (name, feedback) VALUES (?, ?);',(user.first_name + ' ' + user.last_name, comment))
                conn.commit()
                messages.success(request, 'Thanks for your feedback!')
                return redirect('feedback')

        else:
            messages.warning(request, "Please login first to post feedback.")
            return redirect('feedback')


# verify ticket page view




# profile page view for user

class Profile(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return render(request, 'profile.html')
        else:
            return redirect('login')
        


