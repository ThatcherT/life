from django.shortcuts import render
from tim3.utils.events import get_calendar_events, schedule_caledar_event
from datetime import datetime
from tim3.models import Event
from datetime import date
from tim3.utils.model_utils import schedule_from_event_obj
from tim3.utils.datetime_utils import get_date_from_weekday
from pytz import timezone
from datetime import timedelta


def refresh():
    print('hello refresh!')
    """
    This gets all calendar events of the month and saves them to database
    """

    # get all events of the month
    Event.objects.all().delete()
    events = get_calendar_events()

    # iterate through events and save them to database
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print('found event with start', start, 'and end', end)

        start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
        end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')

        title = event['summary']
        id = event['id']
        # i have no idea
        color = event.get('colorId', '10')

        # save the events to database
        e, created = Event.objects.get_or_create(
            start_time=start_time,
            end_time=end_time,
            title=title,
            google_id=id,
            color=str(color),
            duration=end_time-start_time,
        )
    return 0


def refresh_events(request):
    refresh()
    return home(request)


def home(request):
    print('hello home!')
    events = Event.objects.all()
    context = {'events': events}
    return render(request, 'home.html', context)


def create(request):
    if request.method == 'POST':
        # boundaries of event
        by_date = request.POST.get('byDate')
        within_start = request.POST.get('withinStart')
        within_end = request.POST.get('withinEnd')
        # helpful
        now = datetime.today().astimezone(timezone('US/Mountain'))
        weekday = now.weekday()
        available_days = [int(request.POST.get(day)) for day in [
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] if request.POST.get(day)]

        for day in available_days:
            # if day < weekday: move to the end of available_days, else break
            if day <= weekday:
                available_days.append(available_days.pop(0))
            else:
                break

        for day in available_days:
            by_datetime = datetime.strptime(by_date, '%Y-%m-%d')
            django_current_day = day + 1 % 7
            events = Event.objects.filter(
                # start_time__lte=by_date,
                start_time__year__lte=by_datetime.year,  # 2021
                start_time__month__lte=by_datetime.month,  # 9
                start_time__day__lte=by_datetime.day,  # 8

                # filter by week day
                start_time__week_day=django_current_day,  # 0 = Monday
                end_time__week_day=django_current_day,

                # filter by start and end hour
                start_time__hour__gte=int(within_start[:2]),  # 08
                end_time__hour__lte=int(within_end[:2]),  # 18
            )

            # if events don't exist, then add event
            current_day = 0
            if not events:
                # create event
                within_start_datetime = datetime.strptime(
                    within_start, '%H:%M')
                event_date = get_date_from_weekday(int(current_day))
                event_date = event_date.replace(
                    hour=within_start_datetime.hour, minute=within_start_datetime.minute, tzinfo=timezone('US/Central'))

                e = Event(
                    start_time=event_date,
                    end_time=event_date + timedelta(minutes=int(duration)),
                    title=title,
                    duration=duration,
                    google_id='',
                    color='',
                )
                e.save()

                # schedule event on calendar
                google_id = schedule_from_event_obj(e)
                print('event created! no events!')
                print('creating Event:', title)
                print('starts at ', event_date)
                print('ends at ', event_date +
                      timedelta(minutes=int(duration)))

                # initialize event start time
                within_start_datetime = datetime.strptime(
                    within_start, '%H:%M')
                new_event_start = get_date_from_weekday(int(current_day))
                new_event_start = new_event_start.replace(
                    hour=within_start_datetime.hour, minute=within_start_datetime.minute, tzinfo=timezone('US/Central'))

                new_event_end = new_event_start + \
                    timedelta(minutes=int(duration))

                print('iterating through events')
                for event in events:

                    # see if there is enough time after within_start and before event start to schedule
                    print('new_event_end', new_event_end)
                    print('event start', event.start_time)
                    print('tz event start', event.start_time.astimezone(
                        timezone('US/Central')))
                    print('id', event.id)
                    if new_event_end < event.start_time.astimezone(timezone('US/Central')):
                        print('new_event_end', new_event_end, 'is before',
                              event.start_time.astimezone(timezone('US/Central')))
                        # schedule this event
                        e = Event(
                            start_time=new_event_start,
                            end_time=new_event_end,
                            title=title,
                            duration=duration,
                            google_id='',
                            color='',
                        )
                        e.save()
                        # schedule event on calendar

                        google_id = schedule_from_event_obj(e)
                        print('event created!! at start')
                        break
                    else:
                        # the gap is not big enough, make new_event_start the end of this event and move on
                        new_event_start = event.end_time.astimezone(
                            timezone('US/Central'))
                        new_event_end = new_event_start + \
                            timedelta(minutes=int(duration))
                else:
                    # got to last event with no space in schedule
                    within_end_datetime = datetime.strptime(
                        within_end, '%H:%M')
                    end_of_block = get_date_from_weekday(int(current_day))
                    end_of_block = end_of_block.replace(
                        hour=within_end_datetime.hour, minute=within_end_datetime.minute, tzinfo=timezone('US/Central'))
                    print('comparing', new_event_end, 'to', end_of_block)
                    if new_event_end < end_of_block:
                        # schedule this event
                        # schedule this event
                        e = Event(
                            start_time=new_event_start,
                            end_time=new_event_end,
                            title=title,
                            duration=duration,
                            google_id='',
                            color='',
                        )
                        e.save()
                        # schedule event on calendar
                        google_id = schedule_from_event_obj(e)
                        print('event created')
                        break

    # today datetime
    next_week = date.today() + timedelta(days=7)
    context = {"today": next_week}
    return render(request, 'create.html', context)
