# 3p
from nose.plugins.attrib import attr

# project
from checks import AgentCheck
from tests.checks.common import AgentCheckTest


@attr(requires='couchdb')
class CouchTestCase(AgentCheckTest):

    TEST_ORDER = 0
    CHECK_NAME = 'couch'
    DB_NAMES = ['_users', '_replicator']
    CHECK_GAUGES = [
        'couchdb.by_db.disk_size',
        'couchdb.by_db.doc_count',
    ]

    def __init__(self, *args, **kwargs):
        AgentCheckTest.__init__(self, *args, **kwargs)

    def test_couch(self):
        config = {"instances": [{"server": "http://localhost:5984"}]}
        self.run_check(config,force_reload=True)
        for db_name in self.DB_NAMES:
            tags = ['instance:http://localhost:5984', 'db:{0}'.format(db_name)]
            for gauge in self.CHECK_GAUGES:
                self.assertMetric(gauge, tags=tags, count=1)

        self.assertServiceCheck(self.check.SERVICE_CHECK_NAME,
                                status=AgentCheck.OK,
                                tags=['instance:http://localhost:5984'],
                                count=1)

        self.coverage_report()

    def test_bad_config(self):
        self.assertRaises(
            Exception,
            lambda: self.run_check({"instances": [{"server": "http://localhost:5985"}]}, force_reload=True)
        )

        self.assertServiceCheck(self.check.SERVICE_CHECK_NAME,
                                status=AgentCheck.CRITICAL,
                                tags=['instance:http://localhost:5985'],
                                count=1)

    def test_whitelist(self):
        DB_WHITELIST = ["_replicator"]
        whitelist_config = {'instances': [{'db_whitelist': DB_WHITELIST, 'server': 'http://localhost:5984'}]}
        self.run_check(whitelist_config,force_reload=True)
        for db_name in self.DB_NAMES:
            tags = ['instance:http://localhost:5984', 'db:{0}'.format(db_name)]
            for gauge in self.CHECK_GAUGES:
                if db_name in DB_WHITELIST:
                    self.assertMetric(gauge, tags=tags, count=1)
                else:
                    self.assertMetric(gauge, tags=tags, count=0)

    def test_blacklist(self):
        DB_BLACKLIST = ["_replicator"]
        blacklist_config = {'instances': [{'db_blacklist': DB_BLACKLIST, 'server': 'http://localhost:5984'}]}
        self.run_check(blacklist_config,force_reload=True)
        for db_name in self.DB_NAMES:
            tags = ['instance:http://localhost:5984', 'db:{0}'.format(db_name)]
            for gauge in self.CHECK_GAUGES:
                if db_name in DB_BLACKLIST:
                    self.assertMetric(gauge, tags=tags, count=0)
                else:
                    self.assertMetric(gauge, tags=tags, count=1)
