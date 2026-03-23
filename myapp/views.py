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
import os
from datetime import datetime

# Create your views here.

# ==================== دوال مساعدة للتخزين ====================

def get_storage_path():
    """الحصول على مسار ملف التخزين المؤقت"""
    # على Vercel، استخدم /tmp للتخزين المؤقت
    # محلياً، استخدم المجلد الحالي
    if os.path.exists('/tmp'):
        return '/tmp/barber_data.json'
    else:
        return 'barber_data.json'

def load_local_storage():
    """تحميل البيانات من ملف JSON"""
    storage_path = get_storage_path()
    try:
        if os.path.exists(storage_path):
            with open(storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading storage: {e}")
    
    # البيانات الافتراضية
    return {
        'barber_workers_final': {
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
        },
        'barber_customers_final': []
    }

def save_local_storage(data):
    """حفظ البيانات في ملف JSON"""
    storage_path = get_storage_path()
    try:
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving storage: {e}")
        return False

# ==================== دوال الصفحات الرئيسية ====================

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
    """جلب بيانات الصنايعية من localStorage"""
    data = load_local_storage()
    workers = data.get('barber_workers_final', {})
    return JsonResponse(workers, safe=False)


@require_http_methods(["GET"])
def api_queue(request):
    """جلب قائمة الانتظار من localStorage"""
    data = load_local_storage()
    customers = data.get('barber_customers_final', [])
    waiting = [c for c in customers if c.get('status') == 'waiting']
    return JsonResponse(waiting, safe=False)


@require_http_methods(["GET"])
def api_worker_queue(request):
    """جلب قائمة انتظار صنايعي محدد"""
    worker_name = request.GET.get('name')
    data = load_local_storage()
    workers = data.get('barber_workers_final', {})
    customers = data.get('barber_customers_final', [])
    
    if worker_name and worker_name in workers:
        queue_ids = workers[worker_name].get('queue', [])
        queue_customers = [c for c in customers if c.get('id') in queue_ids]
        return JsonResponse(queue_customers, safe=False)
    
    return JsonResponse([], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_add_customer(request):
    """إضافة عميل جديد - يحفظ في localStorage"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        service = data.get('service')
        phone = data.get('phone')
        preferred_worker = data.get('preferred_worker')
        
        # تحميل البيانات الحالية
        storage = load_local_storage()
        workers = storage.get('barber_workers_final', {})
        customers = storage.get('barber_customers_final', [])
        
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
        
        # تحديث قائمة انتظار الصنايعي
        if assigned_worker in workers:
            if 'queue' not in workers[assigned_worker]:
                workers[assigned_worker]['queue'] = []
            workers[assigned_worker]['queue'].append(new_customer['id'])
        
        # حفظ البيانات
        storage['barber_workers_final'] = workers
        storage['barber_customers_final'] = customers
        save_local_storage(storage)
        
        print(f"✅ تم إضافة عميل جديد: {name} - الدور {queue_number} عند {assigned_worker}")
        
        return JsonResponse({
            'success': True,
            'customer': new_customer,
            'queueNumber': queue_number
        })
        
    except Exception as e:
        print(f"❌ خطأ في إضافة عميل: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_customer_status(request):
    """تحديث حالة عميل"""
    try:
        data = json.loads(request.body)
        customer_id = data.get('customerId')
        status = data.get('status')
        
        storage = load_local_storage()
        customers = storage.get('barber_customers_final', [])
        
        for customer in customers:
            if customer.get('id') == customer_id:
                customer['status'] = status
                break
        
        storage['barber_customers_final'] = customers
        save_local_storage(storage)
        
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
        
        # تسجيل للإشعار
        print(f"📱 إرسال واتساب إلى {phone}: {message}")
        
        # TODO: أضف كود إرسال واتساب الحقيقي هنا
        # يمكنك استخدام:
        # - Twilio API
        # - WhatsApp Business API
        # - أو أي خدمة أخرى
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال الإشعار',
            'phone': phone
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_sync_data(request):
    """مزامنة البيانات - يعرض جميع البيانات الحالية"""
    storage = load_local_storage()
    workers = storage.get('barber_workers_final', {})
    customers = storage.get('barber_customers_final', [])
    
    return JsonResponse({
        'workers': workers,
        'customers': customers,
        'total_customers': len(customers),
        'waiting_count': len([c for c in customers if c.get('status') == 'waiting']),
        'completed_count': len([c for c in customers if c.get('status') == 'completed'])
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_sync_save(request):
    """حفظ البيانات المرسلة من الواجهة"""
    try:
        data = json.loads(request.body)
        workers = data.get('workers')
        customers = data.get('customers')
        
        storage = load_local_storage()
        
        if workers is not None:
            storage['barber_workers_final'] = workers
        if customers is not None:
            storage['barber_customers_final'] = customers
            
        save_local_storage(storage)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def api_clear_data(request):
    """مسح جميع البيانات (للاختبار)"""
    try:
        storage = {
            'barber_workers_final': {
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
            },
            'barber_customers_final': []
        }
        save_local_storage(storage)
        return JsonResponse({'success': True, 'message': 'تم مسح جميع البيانات'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_stats(request):
    """إحصائيات سريعة"""
    storage = load_local_storage()
    workers = storage.get('barber_workers_final', {})
    customers = storage.get('barber_customers_final', [])
    
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


@require_http_methods(["GET"])
def api_debug(request):
    """نقطة نهاية للتصحيح - تعرض مسار الملف وحجم البيانات"""
    storage_path = get_storage_path()
    exists = os.path.exists(storage_path)
    size = 0
    if exists:
        size = os.path.getsize(storage_path)
    
    storage = load_local_storage()
    
    return JsonResponse({
        'storage_path': storage_path,
        'file_exists': exists,
        'file_size': size,
        'workers_count': len(storage.get('barber_workers_final', {})),
        'customers_count': len(storage.get('barber_customers_final', [])),
        'storage_data': storage
    })
