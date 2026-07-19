import calendar
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import GoalForm, SignUpForm
from .models import CalendarRoom, Goal, WorkoutEntry

USER_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63']


def get_room(slug):
    return get_object_or_404(CalendarRoom, slug=slug)


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'アカウントを作成しました。')
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'tracker/signup.html', {'form': form})


@login_required
def index(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'join':
            slug = request.POST.get('slug', '').strip()
            room = CalendarRoom.objects.filter(slug=slug).first()
            if room:
                Goal.objects.get_or_create(
                    room=room, user=request.user, defaults={'weekly_target': 3}
                )
                return redirect('calendar', slug=room.slug)
            messages.error(request, 'カレンダーが見つかりません。URLを確認してください。')
        elif action == 'create':
            name = request.POST.get('name', '筋トレカレンダー').strip() or '筋トレカレンダー'
            room = CalendarRoom.objects.create(name=name)
            Goal.objects.get_or_create(
                room=room, user=request.user, defaults={'weekly_target': 3}
            )
            messages.success(request, '共有カレンダーを作成しました。URLを相手に共有してください。')
            return redirect('calendar', slug=room.slug)

    return render(request, 'tracker/index.html')


@login_required
def calendar_view(request, slug):
    room = get_room(slug)
    today = date.today()

    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        year, month = today.year, today.month

    if month < 1:
        month, year = 12, year - 1
    elif month > 12:
        month, year = 1, year + 1

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    entries = WorkoutEntry.objects.filter(room=room, date__range=[start, end])
    entry_map = {}
    for entry in entries:
        entry_map.setdefault(entry.date, []).append(entry.user_id)

    members = {}
    for entry in entries:
        members[entry.user_id] = entry.user.username
    for goal in Goal.objects.filter(room=room).select_related('user'):
        members[goal.user_id] = goal.user.username
    members[request.user.id] = request.user.username

    user_colors = {}
    for i, uid in enumerate(sorted(members.keys())):
        user_colors[uid] = USER_COLORS[i % len(USER_COLORS)]

    calendar_weeks = []
    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(None)
                continue
            d = date(year, month, day)
            user_ids = entry_map.get(d, [])
            colors = [user_colors[uid] for uid in user_ids if uid in user_colors]
            row.append({
                'day': day,
                'date': d.isoformat(),
                'is_today': d == today,
                'is_future': d > today,
                'mine': request.user.id in user_ids,
                'colors': colors,
                'has_workout': bool(user_ids),
            })
        calendar_weeks.append(row)

    goal, _ = Goal.objects.get_or_create(
        room=room, user=request.user, defaults={'weekly_target': 3}
    )

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_names = [
        '', '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月',
    ]

    legend = [
        {'username': members[uid], 'color': user_colors[uid], 'is_me': uid == request.user.id}
        for uid in sorted(members.keys())
    ]

    context = {
        'room': room,
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'calendar_weeks': calendar_weeks,
        'today': today,
        'legend': legend,
        'goal': goal,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'weekday_labels': ['日', '月', '火', '水', '木', '金', '土'],
        'share_url': request.build_absolute_uri(),
    }
    return render(request, 'tracker/calendar.html', context)


@login_required
@require_POST
def toggle_workout(request, slug):
    room = get_room(slug)
    date_str = request.POST.get('date')
    try:
        workout_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        messages.error(request, '日付が不正です。')
        return redirect('calendar', slug=slug)

    if workout_date > date.today():
        messages.error(request, '未来の日付は記録できません。')
        return redirect('calendar', slug=slug)

    entry, created = WorkoutEntry.objects.get_or_create(
        room=room, user=request.user, date=workout_date
    )
    if not created:
        entry.delete()
        messages.info(request, f'{workout_date.strftime("%m/%d")} の記録を解除しました。')
    else:
        messages.success(request, f'{workout_date.strftime("%m/%d")} を筋トレ日として記録しました。')

    year = workout_date.year
    month = workout_date.month
    return redirect(f'{reverse("calendar", kwargs={"slug": slug})}?year={year}&month={month}')


@login_required
def goals_view(request, slug):
    room = get_room(slug)
    goal, _ = Goal.objects.get_or_create(
        room=room, user=request.user, defaults={'weekly_target': 3}
    )

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, '目標を保存しました。')
            return redirect('goals', slug=slug)
    else:
        form = GoalForm(instance=goal)

    all_goals = Goal.objects.filter(room=room).select_related('user')
    return render(request, 'tracker/goals.html', {
        'room': room,
        'form': form,
        'all_goals': all_goals,
    })
