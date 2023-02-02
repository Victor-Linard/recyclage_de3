from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from authenticate.models import User
from django.views.decorators.http import require_http_methods
from capture_image.models import Scan
from django.db.models import Count
import datetime
from django.db.models import Sum
from capture_image.forms import UploadPictureToAnalyze

# Create your views here.


@login_required(login_url='/signin/')
def general(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    return render(request, 'general.html', context={"level_label": level_label, 'form': UploadPictureToAnalyze})


@login_required(login_url='/signin/')
def security(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    return render(request, 'security.html', context={"level_label": level_label, 'form': UploadPictureToAnalyze})


@require_http_methods(["GET"])
def stats(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    total_scans, total_scan_cardboard, total_scan_paper, total_scan_glass, \
        total_scan_metal, total_scan_trash, total_scan_plastic, total_points, result \
            = recover_data_profile(request.user.id)

    return render(request, 'stats.html', context={"level_label": level_label, 'form': UploadPictureToAnalyze, 'total_scans': total_scans, 'total_scan_cardboard': total_scan_cardboard, 'total_scan_paper': total_scan_paper,'total_scan_glass': total_scan_glass, 'total_scan_metal': total_scan_metal, 'total_scan_trash': total_scan_trash, 'total_scan_plastic': total_scan_plastic, 'total_points': total_points, 'result': result})


def recover_data_profile(user_id):
    total_scans = Scan.objects.filter(user_id=user_id).count()
    total_scans_per_waste = Scan.objects.filter(user_id=user_id).values('type_of_waste').annotate(
        total=Count('type_of_waste'))

    total_points = 0
    user = User.objects.get(id=user_id)
    total_points = user.points

    total_scan_cardboard = 0
    total_scan_paper = 0
    total_scan_glass = 0
    total_scan_metal = 0
    total_scan_trash = 0
    total_scan_plastic = 0

    for waste in total_scans_per_waste:
        if waste['type_of_waste'] == 'cardboard':
            total_scan_cardboard = waste['total']
        elif waste['type_of_waste'] == 'paper':
            total_scan_paper = waste['total']
        elif waste['type_of_waste'] == 'glass':
            total_scan_glass = waste['total']
        elif waste['type_of_waste'] == 'metal':
            total_scan_metal = waste['total']
        elif waste['type_of_waste'] == 'trash':
            total_scan_trash = waste['total']
        elif waste['type_of_waste'] == 'plastic':
            total_scan_plastic = waste['total']

    today = datetime.datetime.today()
    one_month_ago = today - datetime.timedelta(days=30)

    scans = Scan.objects.filter(date__range=[one_month_ago, today]).values('date').annotate(total=Count('date')).values(
        'date__date').annotate(total=Count('date'))
    result = {}
    for scan in scans:
        result[scan['date__date'].strftime("%Y-%m-%d")] = scan['total']


    return total_scans, total_scan_cardboard, total_scan_paper, total_scan_glass, total_scan_metal, total_scan_trash, total_scan_plastic, total_points, result

