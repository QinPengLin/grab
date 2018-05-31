# coding=utf-8
"""


"""
import sys
import os
import re
import redis


project_path = os.path.split(os.path.realpath(__file__))[0] + '/../..'
os.chdir(project_path)
sys.path.append(project_path)

from hym.core import Context, Pipeline
from hym.live.steps import *

reload(sys)
sys.setdefaultencoding('utf-8')

# if __name__ == '__main__':
# 	context=Context()

# 	steps=[
# 	Init,
# 	runs
# 	]
# 	pipeline=Pipeline(context, steps)
# 	pipeline.start()
# 	pass
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
print r.get('foo')
