from django.db import models
import datetime
from datetime import timedelta
import django

# google calendar colors
COLOR_CHOICES = [
    # ('Tomato', '11'),
    # ('Basil', '10'),
    # ('Blueberry', '9'),
    # ('Graphite', '8'),
    # ('Peacock', '7'),
    # ('Tangerine', '6'),
    # ('Banana', '5'),
    # ('Flamingo', '4'),
    # ('Grape', '3'),
    # ('Sage', '2'),
    # ('Lavender', '1'),
    ('11', 'Tomato'),
    ('10', 'Basil'),
    ('9', 'Blueberry'),
    ('8', 'Graphite'),
    ('7', 'Peacock'),
    ('6', 'Tangerine'),
    ('5', 'Banana'),
    ('4', 'Flamingo'),
    ('3', 'Grape'),
    ('2', 'Sage'),
    ('1', 'Lavender'),
]


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=2, choices=COLOR_CHOICES)
    user = models.ForeignKey(
        'auth.User', related_name='categories', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


days_dict = {
    'Monday': True,
    'Tuesday': True,
    'Wednesday': True,
    'Thursday': True,
    'Friday': True,
    'Saturday': False,
    'Sunday': False,
}


def days():
    return days_dict


class Event(models.Model):

    # event general
    google_id = models.CharField(max_length=255, unique=False)
    title = models.CharField(max_length=100)

    duration = models.DurationField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # event organize
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    color = models.CharField(max_length=2, choices=COLOR_CHOICES)

    # days available
    # TODO: make this a JSON field

    days = django.db.models.JSONField(default=days)

    # this is the magic, how we can move things around
    within_start = models.TimeField(
        default=datetime.time(hour=8, minute=0))  # 8a
    within_end = models.TimeField(
        default=datetime.time(hour=18, minute=0))  # 6p
    by_date = models.DateField(null=True, blank=True)

    def human_color(self):
        return dict(COLOR_CHOICES)[self.color]

    def css_color(self):
        css_color_dict = {
            '11': 'red',
            '10': 'green',
            '9': 'blue',
            '8': 'gray',
            '7': 'dodgerblue',
            '6': 'orange',
            '5': 'yellow',
            '4': 'hotpink',
            '3': 'purple',
            '2': 'darkseagreen',
            '1': 'cornflowerblue',
        }
        return css_color_dict[self.color]

    def __str__(self):
        return self.title

    # sort by most recent
    class Meta:
        ordering = ['-start_time']


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    # separate each event by a certain amount of time maybe
    time_between_events = models.DurationField(default=timedelta(minutes=15))
    gcal_api_token = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
