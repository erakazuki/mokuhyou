from django.contrib import admin

from .models import CalendarRoom, Goal, WorkoutEntry


@admin.register(CalendarRoom)
class CalendarRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    readonly_fields = ['slug']


@admin.register(WorkoutEntry)
class WorkoutEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'date']
    list_filter = ['room', 'date']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'weekly_target']
