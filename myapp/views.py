from django.shortcuts import render , redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime

# Create your views here.
def home(request):
    return render(request, 'home.html')


def auth(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
       
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user dose not exist')  
         
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request , user)
            return redirect('home')

    context = {'page' : page}
    return render(request, 'auth.html' , context)

def logoutuser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request , 'An error occurred during registration')
    return render(request , 'reg.html', {'form':form})


# ==================== دوال API للواتساب ====================

@require_http_methods(["GET"])
def api_workers(request):
    """جلب بيانات الصنايعية"""
    # جلب البيانات من session (مؤقت)
    workers = request.session.get('barber_workers', {
        'محمد': {
            'status': 'available',
            'currentCustomer': None,
            'queue': [],
            'skills': ['حلاقة', 'لحية', 'حلاقة ولحية']
        },
        'أحمد': {
            'status': 'available', 
            'currentCustomer': None,
            'queue': [],
            'skills': ['حلاقة', 'حلاقة وتصفيف', 'حلاقة كاملة']
        },
        'خالد': {
            'status': 'available',
            'currentCustomer': None,
            'queue': [],
            'skills': ['لحية', 'حلاقة ولحية', 'حلاقة كاملة']
        }
    })
    
    return JsonResponse(workers, safe=False)


@require_http_methods(["GET"])
def api_queue(request):
    """جلب قائمة الانتظار"""
    customers = request.session.get('barber_customers', [])
    waiting = [c for c in customers if c.get('status') == 'waiting']
    return JsonResponse(waiting, safe=False)


@require_http_methods(["GET"])
def api_worker_queue(request):
    """جلب قائمة انتظار صنايعي محدد"""
    worker_name = request.GET.get('name')
    workers = request.session.get('barber_workers', {})
    customers = request.session.get('barber_customers', [])
    
    if worker_name and worker_name in workers:
        queue_ids = workers[worker_name].get('queue', [])
        queue_customers = [c for c in customers if c.get('id') in queue_ids]
        return JsonResponse(queue_customers, safe=False)
    
    return JsonResponse([], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_add_customer(request):
    """إضافة عميل جديد"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        service = data.get('service')
        phone = data.get('phone')
        preferred_worker = data.get('preferred_worker')
        
        # جلب البيانات الحالية
        workers = request.session.get('barber_workers', {})
        customers = request.session.get('barber_customers', [])
        
        # حساب رقم الدور
        waiting_count = len([c for c in customers if c.get('status') == 'waiting'])
        queue_number = waiting_count + 1
        
        # تعيين صنايعي
        assigned_worker = preferred_worker
        if assigned_worker == 'أول متاح':
            for worker_name, worker_data in workers.items():
                if worker_data.get('status') == 'available' and service in worker_data.get('skills', []):
                    assigned_worker = worker_name
                    break
        
        # إنشاء عميل جديد
        new_customer = {
            'id': int(datetime.now().timestamp() * 1000),
            'name': name,
            'phone': phone,
            'service': service,
            'worker': assigned_worker,
            'queueNumber': queue_number,
            'status': 'waiting',
            'bookingTime': datetime.now().isoformat(),
            'originalOrder': int(datetime.now().timestamp() * 1000)
        }
        
        customers.append(new_customer)
        
        # إضافة لقائمة انتظار الصنايعي
        if assigned_worker in workers:
            if 'queue' not in workers[assigned_worker]:
                workers[assigned_worker]['queue'] = []
            workers[assigned_worker]['queue'].append(new_customer['id'])
        
        # حفظ البيانات في session
        request.session['barber_workers'] = workers
        request.session['barber_customers'] = customers
        request.session.modified = True  # تأكيد حفظ session
        
        return JsonResponse({
            'success': True,
            'customer': new_customer,
            'queueNumber': queue_number
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_customer_status(request):
    """تحديث حالة عميل"""
    try:
        data = json.loads(request.body)
        customer_id = data.get('customerId')
        status = data.get('status')
        
        customers = request.session.get('barber_customers', [])
        
        for customer in customers:
            if customer.get('id') == customer_id:
                customer['status'] = status
                break
        
        request.session['barber_customers'] = customers
        request.session.modified = True
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_send_notification(request):
    """إرسال إشعار واتساب"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        message = data.get('message')
        customer_name = data.get('customerName')
        
        # هنا ستضيف كود إرسال واتساب الفعلي
        # يمكنك استخدام Twilio أو WhatsApp Business API
        
        # تسجيل للإشعار (يمكنك إرسال إشعار حقيقي هنا)
        print(f"📱 إرسال واتساب إلى {phone}: {message}")
        
        # TODO: أضف كود إرسال واتساب الحقيقي هنا
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال الإشعار',
            'phone': phone
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_sync_data(request):
    """مزامنة البيانات (للاختبار)"""
    workers = request.session.get('barber_workers', {})
    customers = request.session.get('barber_customers', [])
    
    return JsonResponse({
        'workers': workers,
        'customers': customers,
        'total_customers': len(customers),
        'waiting_count': len([c for c in customers if c.get('status') == 'waiting'])
    })


@require_http_methods(["POST"])
def api_clear_session(request):
    """مسح جميع البيانات (للاختبار)"""
    request.session.flush()
    return JsonResponse({'success': True, 'message': 'تم مسح جميع البيانات'})


@require_http_methods(["GET"])
def api_stats(request):
    """إحصائيات سريعة"""
    workers = request.session.get('barber_workers', {})
    customers = request.session.get('barber_customers', [])
    
    available_workers = len([w for w in workers.values() if w.get('status') == 'available'])
    busy_workers = len([w for w in workers.values() if w.get('status') == 'busy'])
    waiting_customers = len([c for c in customers if c.get('status') == 'waiting'])
    completed_customers = len([c for c in customers if c.get('status') == 'completed'])
    
    return JsonResponse({
        'total_workers': len(workers),
        'available_workers': available_workers,
        'busy_workers': busy_workers,
        'waiting_customers': waiting_customers,
        'completed_customers': completed_customers,
        'total_customers': len(customers)
    })
