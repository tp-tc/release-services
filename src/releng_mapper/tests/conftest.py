# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import pytest

import backend_common
from releng_mapper.models import Project


def db_setup(app):
    session = app.db.session
    project = Project(name='proj')
    session.add(project)
    session.commit()


@pytest.fixture(scope='function')
def app():
    '''Load releng_mapper in test mode
    '''
    import releng_mapper

    config = backend_common.testing.get_app_config({
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    app = releng_mapper.create_app(config)

    with app.app_context():
        backend_common.testing.configure_app(app)
        db_setup(app)

        yield app
