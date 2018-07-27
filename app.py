import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import flask
import redis
import time
import os
from tasks import hello
from redis_instance import r

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
    html.Button(id='hello', type='submit', children='Run "Hello" task'),
    html.Button(id='clear', type='submit', children='Clear all reports'),
    html.Div(id='target1'),
    html.Div(id='target2'),
    html.Div(id='status')
], className="container")


@app.callback(Output('target2', 'children'), [], [], [Event('clear', 'click')])
def clear_all():
    print 'DEBUG: clear_all callback hit'
    r.flushall()


@app.callback(Output('target1', 'children'), [], [], [Event('hello', 'click')])
def hello_callback():
    print 'DEBUG: hello callback hit'
    hello.delay(int(time.time()))


@app.callback(Output('status', 'children'), [Input('interval', 'n_intervals')])
def populate_table(n_intervals):

    inner_table = [
        html.Tr([
            html.Th(['Report ID']),
            html.Th(['Status'])
        ])
    ]

    print r.keys()

    for key in r.keys():
        if 'kombu' not in key:
            status = r.hget(key, 'status')
            inner_table.append(
                html.Tr([
                    html.Td([key]),
                    html.Td([status if status is not None else 'Task not found'])
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
