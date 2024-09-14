import streamlit as st

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches

st.set_page_config(layout="wide")

#################################### init
if 'markers' not in st.session_state:
    st.session_state['markers'] = []


left, right = st.columns(2)

with left:
    #################################### user input
    # route
    st.write('## route')

    st.number_input(
        'total route distance (nautical miles)',
        key = 'total_route_distance_nautical_miles',
        value = 15.0,
        step = 1.0
    )

    input_type = st.selectbox(
        'input type',
        ['start time + end time', 'start time + speed'],
        key = 'input_type'

    )

    if input_type == 'start time + end time':
        start_column, end_column = st.columns(2)
        with start_column:
            start_date = st.date_input(
                'start date',
                value = datetime.now().date()
            )
            start_time = st.time_input(
                'start time',
                step = timedelta(hours = 1),
                value = datetime.now().time()
            )
            st.session_state['start_datetime'] = datetime.combine(start_date, start_time)
        with end_column:
            default_duration = timedelta(hours = 12)
            end_date = st.date_input(
                'end date',
                value = st.session_state['start_datetime'] + default_duration
            )
            end_time = st.time_input(
                'end time',
                step = timedelta(hours = 1),
                value = st.session_state['start_datetime'] + default_duration
            )
            st.session_state['end_datetime'] = datetime.combine(end_date, end_time)

        st.session_state['total_duration'] = st.session_state['end_datetime'] - st.session_state['start_datetime']
        total_hours = st.session_state['total_duration'].total_seconds() /(60 * 60)
        if total_hours > 0:
            st.session_state['speed_knots'] = st.session_state['total_route_distance_nautical_miles'] / total_hours
        else:
            st.session_state['speed_knots'] = 0.0


    if input_type == 'start time + speed':
        start_column, speed_column = st.columns(2)
        with start_column:
            start_date = st.date_input(
                'start date'
            )
            start_time = st.time_input(
                'start time'
            )
            st.session_state['start_datetime'] = datetime.combine(start_date, start_time)
        with speed_column:
            st.number_input(
                'speed (knots)',
                key = 'speed_knots',
                value = st.session_state['speed_knots'],
                step = 1.0
            )


    # zero PIM sections
    st.divider()
    st.write('## zero PIM sections')

    st.number_input(
        'number of zero PIM sections',
        key = 'number_of_sections',
        value = 0,
        step = 1,
        min_value = 0
    )

    st.session_state['zero_PIM_data'] = [{} for i in range(st.session_state['number_of_sections'])]

    for i in range(st.session_state['number_of_sections']):
        st.write('### zero PIM section {}'.format(i + 1))

        start_column, end_column = st.columns(2)
        with start_column:
            start_date = st.date_input(
                'start date',
                key = 'zeroPIM{}_start_date'.format(i)
            )
            start_time = st.time_input(
                'start time',
                step = timedelta(hours = 0.5),
                key = 'zeroPIM{}_start_time'.format(i)
            )
            zone_start = datetime.combine(start_date, start_time)
        with end_column:
            end_date = st.date_input(
                'end date',
                key = 'zeroPIM{}_end_date'.format(i)
            )
            end_time = st.time_input(
                'end time',
                step = timedelta(hours = 0.5),
                key = 'zeroPIM{}_end_time'.format(i)
            )
            zone_end = datetime.combine(end_date, end_time)

        st.session_state['zero_PIM_data'][i] = {
            'start': zone_start,
            'end': zone_end
        }


    # water space management
    st.divider()
    st.write('## waterspace management constraints')

    st.number_input(
        'number of constraints',
        key = 'number_of_constraints',
        value = 0,
        min_value = 0,
    )

    st.session_state['waterspace_constraint_data'] = [{} for i in range(st.session_state['number_of_constraints'])]

    for i in range(st.session_state['number_of_constraints']):
        st.write('### constraint {}'.format(i + 1))

        start_time_column, end_time_column = st.columns(2)
        with start_time_column:
            start_date = st.date_input(
                'start date',
                key = 'constraint{}_start_date'.format(i)
            )
            start_time = st.time_input(
                'start time',
                step = timedelta(hours = 0.5),
                key = 'constraint{}_start_time'.format(i)
            )
            constraint_start_time = datetime.combine(start_date, start_time)
        with end_time_column:
            end_date = st.date_input(
                'end date',
                key = 'constraint{}_end_date'.format(i)
            )
            end_time = st.time_input(
                'end time',
                step = timedelta(hours = 0.5),
                key = 'constraint{}_end_time'.format(i)
            )
            constraint_end_time = datetime.combine(end_date, end_time)

        start_distance_column, end_distance_column = st.columns(2)
        with start_distance_column:
            start_distance = st.number_input(
                'start distance',
                step = 1.0,
                key = 'constraint{}_start_distance'.format(i)
            )
        with end_distance_column:
            end_distance = st.number_input(
                'end distance',
                step = 1.0,
                key = 'constraint{}_end_distance'.format(i)
            )

        st.session_state['waterspace_constraint_data'][i] = {
            'start_time': constraint_start_time,
            'end_time': constraint_end_time,
            'start_distance': start_distance,
            'end_distance': end_distance
        }

    # current time and position
    st.divider()
    st.write('## add marker')
    marker_date = st.date_input('date')
    marker_time = st.time_input('time')
    marker_distance = st.number_input('distance to end of route', step = 1.0)

    add_marker = st.button('add marker')
    if add_marker:
        st.session_state['markers'].append({
            'timestamp': datetime.combine(marker_date, marker_time),
            'distance': marker_distance
        })

with right:
    #################################### overview
    st.write('## overview')

    # st.sidebar.write(st.session_state)
    total_route_distance_nautical_miles = st.session_state['total_route_distance_nautical_miles']

    total_duration      = st.session_state['total_duration']
    total_time_minutes  = total_duration.total_seconds() / 60
    total_time_hours    = total_duration.total_seconds() / (60 * 60)

    start_datetime  = st.session_state['start_datetime']
    end_datetime    = st.session_state['end_datetime']

    speed_knots = st.session_state['speed_knots']

    overview = {
        'total distance': '{:.2f} nautical miles'.format(total_route_distance_nautical_miles),
        'total duration': '{:.2f} hours'.format(total_time_hours),
        'start datetime': datetime.strftime(start_datetime, '%Y-%m-%d %H:%M'),
        'end datetime':   datetime.strftime(end_datetime, '%Y-%m-%d %H:%M'),
        'speed':          '{:.2f} knots'.format(speed_knots)
    }
    st.table(overview)


    #################################### plot
    st.write('## plot')
    figure = plt.figure()
    ax = plt.gca()

    # raw speed of advance (SOA)
    minutes = range(0, int(total_time_minutes) + 1)
    datetimes = [start_datetime + timedelta(minutes = m) for m in minutes]
    distances = [total_route_distance_nautical_miles - speed_knots * m/60.0 for m in minutes]

    plt.plot(
        datetimes,
        distances,
        label = 'SOA'
    )

    # speed plan
    for index, zone in enumerate(st.session_state['zero_PIM_data']):
        plt.plot(
            [zone['start'], zone['end']],
            [total_route_distance_nautical_miles, total_route_distance_nautical_miles],
            color = 'green',
            linewidth = 5,
            # label = 'zero PIM zone {}'.format(index)
        )

    # water space management
    for index, zone in enumerate(st.session_state['waterspace_constraint_data']):

        ax.add_patch(patches.Rectangle(
            xy = (zone['start_time'], zone['start_distance']),
            width = zone['end_time'] - zone['start_time'],
            height = zone['end_distance'] - zone['start_distance'],
            color = 'red',
            # label = 'waterspace constraint {}'.format(index)
        ))


    # current position plotting
    annotate = st.checkbox('annotate markers')
    for marker in st.session_state['markers']:
        plt.plot(
            marker['timestamp'],
            marker['distance'],
            marker = 'x',
            linestyle = ' ',
            color = 'black',
            # label = marker['timestamp']
        )
        if annotate:
            plt.annotate(
                marker['timestamp'],
                xy = (marker['timestamp'], marker['distance']),
                xytext = (0, 50),
                textcoords = 'offset points',
                ha = 'center',
                va = 'bottom',
                fontsize = 8,
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
            )

    # add stuff
    plt.annotate(
        '😍',
        xy = (0.1, 0.1),
        xycoords = 'axes fraction',
        fontname='Segoe UI Emoji',
        fontsize = 20,
        ha = 'left',
        va = 'bottom'
    )
    plt.annotate(
        '😡',
        xy = (0.9, 0.9),
        xycoords = 'axes fraction',
        fontname='Segoe UI Emoji',
        fontsize = 20,
        ha = 'right',
        va = 'top'
    )

    plt.title('passage graph')
    plt.xlabel('time')
    plt.ylabel('distance to go (nautical miles)')
    plt.legend(loc = 'center left', bbox_to_anchor = (1, 0.5))

    # format
    ax.xaxis.set_major_locator(mdates.HourLocator(interval = 1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
    plt.xticks(rotation = 90)

    # show
    st.pyplot(figure)



    #################################### download
    st.write('## download')

    generate = st.button('generate file for download')

    if generate:

        filename = datetime.strftime(start_datetime, '%Y-%m-%d') + '_to_' + datetime.strftime(end_datetime, '%Y-%m-%d %H:%M') + '.png'

        plt.savefig(filename)
        st.write('generated ', filename)

        st.download_button('download plot', 'plot.png', filename, 'image/png')


