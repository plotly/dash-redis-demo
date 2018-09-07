import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import flask
import redis
import time
import os
from tasks import long_running_task, error_task
from redis_instance import r
import uuid

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('app', server=server)

if 'DYNO' in os.environ:
    if bool(os.getenv('DASH_PATH_ROUTING', 0)):
        app.config.requests_pathname_prefix = '/{}/'.format(
            os.environ['DASH_APP_NAME']
        )


app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    dcc.Interval(id='interval', interval=1000),
    html.H1('Redis INFO'),
    html.Div(children=html.Pre(str(r.info()))),
    html.Button(id='long', type='submit', children='Run "expensive" task'),
    html.Button(id='error', type='submit', children='Run "error" task'),
    html.Button(id='clear', type='submit', children='Clear all reports'),
    html.Div(id='target'),
    html.Div(id='status')
], className="container")


@app.callback(
    Output('target', 'children'),
    [Input('long', 'n_clicks_timestamp'), Input('error', 'n_clicks_timestamp'),
     Input('clear', 'n_clicks_timestamp')]
)
def task_or_clear(long, error, clear):
    if not long:
        long = 0
    if not error:
        error = 0
    if not clear:
        clear = 0
    if int(long) > int(clear) and int(long) > int(error):
        print('DEBUG: long task callback hit')
        long_running_task.delay(uuid.uuid4().hex)
    elif int(error) > int(long) and int(error) > int(clear):
        print('DEBUG: error task callback hit')
        error_task.delay(uuid.uuid4().hex)
    elif int(clear) > int(long) and int(clear) > int(error):
        print('DEBUG: clearing database')
        r.flushall()
    return ''


@app.callback(Output('status', 'children'), [Input('interval', 'n_intervals')])
def populate_table(n_intervals):

    inner_table = [
        html.Tr([
            html.Th(['Task ID']),
            html.Th(['Status'])
        ])
    ]

    for key in r.zrangebyscore('tasks', '-inf', 'inf'):
        print(key.decode('utf-8'))
        status = r.hget(key, 'status')
        print(status)
        inner_table.append(
            html.Tr([
                html.Td([key.decode('utf-8')]),
                html.Td([status.decode('utf-8')])
            ])
        )

    return html.Table(inner_table)


app.css.append_css({
    'external_url': (
        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/96e31642502632e86727652cf0ed65160a57497f/dash-hello-world.css'
    )
})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server()
