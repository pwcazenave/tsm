#!/usr/bin/env python
"""
Store TSM mounted volumes backup status for easy identification of volumes not being backed up.

Pierre Cazenave - pwcazenave@gmail.com

ChangeLog
    14/02/2021 First release.

"""

# TODO:
#   - Add a simple UI with host/paths/tick|cross for quickly identifying which
#   hosts are correctly configured
#   - Add filter for only showing improperly configured hosts
#   - Add front-end for adding exclusions

import logging
import os

import flask
import flask_wtf
from flask_sqlalchemy import SQLAlchemy

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 8000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '1') == '1'

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.info('Starting app')

app = flask.Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///tsm.db'
app.config['SECRET_KEY'] = os.urandom(32)
# Create a base database object.
db = SQLAlchemy(app)

# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)
app.config['SECRET_KEY'] = os.urandom(32)
csrf.init_app(app)

# Remove unnecessary whitespace in the rendered HTML
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


class HostDirectory(db.Model):
    """
    Our database table for the host config. One row per host per mount.

    """

    __tablename__ = 'backup'
    __table_args__ = {'extend_existing': True}

    # Set up the database columns
    id_primary = db.Column('id', db.Integer, primary_key=True)
    hostname = db.Column('hostname', db.String(200))
    mountpoint = db.Column('mountpoint', db.String(500))
    backedup = db.Column('backedup', db.Integer, default=0)
    ignore = db.Column('ignore', db.Integer, default=0)


@app.route('/')
def root():
    """
    Show all the hosts in the database in an easy to view manner.

    """

    hostinfo = HostDirectory.query.filter_by().order_by(HostDirectory.hostname, HostDirectory.backedup, HostDirectory.mountpoint).all()

    return flask.render_template('index.html', hostinfo=hostinfo)


@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    Add or update a host backup path and its backup status.

    """

    if flask.request.method == 'POST':
        hostname = flask.request.form['set-leave-month']
        mountpoint = flask.request.form['mountpoint']
        backedup = flask.request.form['backedup']
        ignore = flask.request.form['ignore']
    else:
        hostname = flask.request.args.get('hostname')
        mountpoint = flask.request.args.get('mountpoint')
        backedup = flask.request.args.get('backedup')
        ignore = flask.request.args.get('ignore')

    if backedup is None:
        backedup = 0
    if ignore is None:
        ignore = 0

    # Remove the existing entry for this host/path combo and replace it with the new data.
    hostdir = HostDirectory.query.filter_by(hostname=hostname, mountpoint=mountpoint)
    if hostdir:
        hostdir.delete()
    hostdir = HostDirectory(hostname=hostname, mountpoint=mountpoint, backedup=backedup, ignore=ignore)

    db.session.add(hostdir)
    db.session.commit()

    response = {'status': True, 'status_code': 200}

    return flask.jsonify(response)


@app.route('/query', methods=['GET', 'POST'])
def query():
    """
    Find out the current backup status for a given host.

    """

    if flask.request.method == 'POST':
        hostname = flask.request.form['set-leave-month']
        mountpoint = flask.request.form['mountpoint']
    else:
        hostname = flask.request.args.get('hostname')
        mountpoint = flask.request.args.get('mountpoint')

    hostdir = HostDirectory.query.filter_by(hostname=hostname, mountpoint=mountpoint).first()

    response = {'status': True, 'status_code': 200}
    if hostdir:
        response['backedup'] = hostdir.backedup
    else:
        response['backedup'] = 0

    return flask.jsonify(response)


@app.route('/exceptions', methods=['GET', 'POST'])
def exceptions():
    """
    Show hosts and paths which are being ignored.

    """
    exceptions = HostDirectory.query.filter_by(ignore=1).all()

    return flask.render_template('exceptions.html', exceptions=exceptions)


def main():
    app.run(host=host,
            port=port,
            debug=debug,
            use_reloader=use_reloader,
            extra_files=['./app/templates/index.html',
                         './app/static/css/style.css'])


if __name__ == '__main__':

    db.create_all()
    main()
