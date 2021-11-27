import redis

host = "KITCapstone.iptime.org"
port = "6379"

# 레디스 연결
rd = redis.StrictRedis(host=host, port=port, db=0, password="8788", charset="utf-8", decode_responses=True)
