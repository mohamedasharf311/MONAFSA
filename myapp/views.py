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
from django.utils import timezone
from django.db import transaction
import json
import os
from datetime import datetime

# استيراد الموديلات
from .models import BarberWorker, BarberCustomer, BarberSettings

# Create your views here.

# ==================== دوال مساعدة ====================

def init_default_workers():
    """تهيئة الصنايعية الافتراضيين إذا لم يكونوا موجودين"""
    default_workers = [
        {'name': 'محمد', 'skills': ['حلاقة', 'لحية', 'حلاقة ولحية']},
        {'name': 'أحمد', 'skills': ['حلاقة', 'حلاقة وتصفيف', 'حلاقة كاملة']},
        {'name': 'خالد', 'skills': ['لحية', 'حلاقة ولحية', 'حلاقة كاملة']}
    ]
    
    for worker_data in default_workers:
        BarberWorker.objects.get_or_create(
            name=worker_data['name'],
            defaults={
                'skills': worker_data['skills'],
                'status': 'available',
                'queue': []
            }
        )

def get_workers_dict():
    """جلب بيانات الصنايعية كـ dict (للتوافق مع الكود الحالي)"""
    workers = {}
    for w in BarberWorker.objects.all():
        workers[w.name] = {
            'status': w.status,
            'currentCustomer': w.current_customer_id,
            'queue': w.queue or [],
            'skills': w.skills
        }
    return workers

def get_customers_list():
    """جلب بيانات العملاء كـ list"""
    return list(BarberCustomer.objects.values())

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


# ==================== دوال API للواتساب (باستخدام قاعدة البيانات) ====================

@require_http_methods(["GET"])
def api_workers(request):
    """جلب بيانات الصنايعية من قاعدة البيانات"""
    init_default_workers()
    workers = get_workers_dict()
    return JsonResponse(workers, safe=False)


@require_http_methods(["GET"])
def api_queue(request):
    """جلب قائمة الانتظار من قاعدة البيانات"""
    waiting = BarberCustomer.objects.filter(status='waiting').order_by('queue_number')
    return JsonResponse(list(waiting.values()), safe=False)


@require_http_methods(["GET"])
def api_worker_queue(request):
    """جلب قائمة انتظار صنايعي محدد"""
    worker_name = request.GET.get('name')
    try:
        worker = BarberWorker.objects.get(name=worker_name)
        queue_ids = worker.queue or []
        customers = BarberCustomer.objects.filter(customer_id__in=queue_ids, status='waiting').order_by('queue_number')
        return JsonResponse(list(customers.values()), safe=False)
    except BarberWorker.DoesNotExist:
        return JsonResponse([], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_add_customer(request):
    """إضافة عميل جديد - يحفظ في قاعدة البيانات"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        service = data.get('service')
        phone = data.get('phone')
        preferred_worker = data.get('preferred_worker')
        
        with transaction.atomic():
            # جلب الصنايعية
            workers = {w.name: w for w in BarberWorker.objects.all()}
            
            # حساب رقم الدور
            waiting_count = BarberCustomer.objects.filter(status='waiting').count()
            queue_number = waiting_count + 1
            
            # تعيين صنايعي
            assigned_worker = preferred_worker
            if assigned_worker == 'أول متاح':
                for name, worker in workers.items():
                    if worker.status == 'available' and service in worker.skills:
                        assigned_worker = name
                        break
            
            # إنشاء معرف فريد
            customer_id = int(datetime.now().timestamp() * 1000)
            
            # إنشاء عميل جديد
            new_customer = BarberCustomer.objects.create(
                customer_id=customer_id,
                name=name,
                phone=phone,
                service=service,
                worker=assigned_worker,
                queue_number=queue_number,
                status='waiting',
                original_order=customer_id
            )
            
            # تحديث قائمة انتظار الصنايعي
            if assigned_worker in workers:
                worker = workers[assigned_worker]
                queue = worker.queue or []
                queue.append(customer_id)
                worker.queue = queue
                worker.save()
            
            # تحديث أرقام الأدوار لجميع العملاء
            all_waiting = BarberCustomer.objects.filter(status='waiting').order_by('queue_number')
            for idx, customer in enumerate(all_waiting, 1):
                customer.queue_number = idx
                customer.save()
        
        print(f"✅ تم إضافة عميل: {name} - الدور {queue_number} عند {assigned_worker}")
        
        return JsonResponse({
            'success': True,
            'customer': {
                'id': new_customer.customer_id,
                'name': new_customer.name,
                'queueNumber': queue_number
            },
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
        
        with transaction.atomic():
            customer = BarberCustomer.objects.get(customer_id=customer_id)
            old_status = customer.status
            
            # تحديث وقت الإكمال
            if status == 'completed' and old_status != 'completed':
                customer.completed_time = timezone.now()
            
            customer.status = status
            customer.save()
            
            # إذا تم إنهاء الخدمة، أزل من قائمة انتظار الصنايعي
            if status == 'completed':
                try:
                    worker = BarberWorker.objects.get(name=customer.worker)
                    if worker.queue:
                        worker.queue = [q for q in worker.queue if q != customer_id]
                        worker.save()
                    
                    # إذا كان الصنايعي مشغول بهذا العميل
                    if worker.current_customer_id == customer_id:
                        worker.current_customer_id = None
                        worker.status = 'available'
                        worker.save()
                        
                        # استدعاء العميل التالي
                        if worker.queue:
                            next_id = worker.queue[0]
                            next_customer = BarberCustomer.objects.get(customer_id=next_id)
                            worker.current_customer_id = next_id
                            worker.status = 'busy'
                            next_customer.status = 'in_service'
                            next_customer.save()
                            worker.save()
                except BarberWorker.DoesNotExist:
                    pass
        
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
    workers = get_workers_dict()
    customers = list(BarberCustomer.objects.values())
    
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
        workers_data = data.get('workers')
        customers_data = data.get('customers')
        
        with transaction.atomic():
            if workers_data:
                for name, worker_info in workers_data.items():
                    worker, created = BarberWorker.objects.update_or_create(
                        name=name,
                        defaults={
                            'status': worker_info.get('status', 'available'),
                            'current_customer_id': worker_info.get('currentCustomer'),
                            'queue': worker_info.get('queue', []),
                            'skills': worker_info.get('skills', [])
                        }
                    )
            
            if customers_data:
                # مسح العملاء الحاليين وإعادة إنشائهم
                BarberCustomer.objects.all().delete()
                for customer_info in customers_data:
                    BarberCustomer.objects.create(
                        customer_id=customer_info.get('id', int(datetime.now().timestamp() * 1000)),
                        name=customer_info.get('name'),
                        phone=customer_info.get('phone', ''),
                        service=customer_info.get('service'),
                        worker=customer_info.get('worker'),
                        queue_number=customer_info.get('queueNumber', 1),
                        status=customer_info.get('status', 'waiting'),
                        original_order=customer_info.get('originalOrder', int(datetime.now().timestamp() * 1000)),
                        booking_time=datetime.fromisoformat(customer_info.get('bookingTime', datetime.now().isoformat())) if customer_info.get('bookingTime') else timezone.now(),
                        completed_time=datetime.fromisoformat(customer_info.get('completedTime')) if customer_info.get('completedTime') else None
                    )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def api_clear_data(request):
    """مسح جميع البيانات (للاختبار)"""
    try:
        with transaction.atomic():
            BarberCustomer.objects.all().delete()
            BarberWorker.objects.all().delete()
            
            # إعادة إنشاء الصنايعية الافتراضيين
            init_default_workers()
        
        return JsonResponse({'success': True, 'message': 'تم مسح جميع البيانات'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_stats(request):
    """إحصائيات سريعة"""
    total_workers = BarberWorker.objects.count()
    available_workers = BarberWorker.objects.filter(status='available').count()
    busy_workers = BarberWorker.objects.filter(status='busy').count()
    waiting_customers = BarberCustomer.objects.filter(status='waiting').count()
    completed_customers = BarberCustomer.objects.filter(status='completed').count()
    total_customers = BarberCustomer.objects.count()
    
    return JsonResponse({
        'total_workers': total_workers,
        'available_workers': available_workers,
        'busy_workers': busy_workers,
        'waiting_customers': waiting_customers,
        'completed_customers': completed_customers,
        'total_customers': total_customers
    })


@require_http_methods(["GET"])
def api_debug(request):
    """نقطة نهاية للتصحيح - تعرض حالة قاعدة البيانات"""
    workers = BarberWorker.objects.all()
    customers = BarberCustomer.objects.all()
    
    return JsonResponse({
        'workers_count': workers.count(),
        'workers': list(workers.values()),
        'customers_count': customers.count(),
        'customers': list(customers.values()),
        'database_connected': True
    })


@require_http_methods(["POST"])
def api_clear_session(request):
    """مسح جميع البيانات (للاختبار) - اسم بديل لـ api_clear_data"""
    return api_clear_data(request)
@require_http_methods(["GET"])
def api_error_test(request):
    """اختبار بسيط لاكتشاف الأخطاء"""
    try:
        # اختبار جلب الصنايعية
        workers = BarberWorker.objects.all()
        workers_data = {w.name: {'status': w.status, 'skills': w.skills} for w in workers}
        
        return JsonResponse({
            'status': 'ok',
            'workers': workers_data,
            'workers_count': workers.count()
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
