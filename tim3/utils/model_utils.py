from tim3.utils.events import schedule_caledar_event

def schedule_from_event_obj(e):
    title = e.title
    start = e.start_time.isoformat()
    end = e.end_time.isoformat()

    # change last 5 chars to 05:00
    print('start_bef-re_manual_change', start)
    print('end_b4_change', end)
    start_time = start[:-5] + '05:00'
    end_time = end[:-5] + '05:00'
    print(start_time, 'after')
    print(end_time, 'after')
    
    schedule_caledar_event(
        title,
        start=start_time,
        end=end_time,
        )
    return