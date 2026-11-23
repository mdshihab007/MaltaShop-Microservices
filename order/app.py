import os, json, uuid, sqlite3, time
from flask import Flask, request, jsonify
import pika
app=Flask(__name__)
DB='/data/orders.db'
os.makedirs('/data',exist_ok=True)
with sqlite3.connect(DB) as c:c.execute('CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, item TEXT, status TEXT)')
def publish(payload):
    for attempt in range(12):
        try:
            conn=pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('BROKER_HOST','rabbitmq')))
            channel=conn.channel();channel.queue_declare(queue='order_placed',durable=True)
            channel.basic_publish(exchange='',routing_key='order_placed',body=json.dumps(payload),properties=pika.BasicProperties(delivery_mode=2))
            conn.close();return
        except pika.exceptions.AMQPError:
            if attempt==11:raise
            time.sleep(2)
@app.post('/orders')
def order():
    body=request.get_json(silent=True) or {}
    if not isinstance(body.get('item'),str) or not body['item'].strip():return jsonify(error='item is required'),400
    cid=request.headers.get('X-Correlation-ID') or str(uuid.uuid4());oid=str(uuid.uuid4())
    with sqlite3.connect(DB) as c:c.execute('INSERT INTO orders VALUES(?,?,?)',(oid,body['item'],'PLACED'))
    event={'type':'OrderPlaced','order_id':oid,'item':body['item'],'correlation_id':cid}
    try:publish(event)
    except Exception:
        app.logger.exception('event publish failed correlation_id=%s',cid)
        return jsonify(error='order saved but event delivery pending',order_id=oid,correlation_id=cid),503
    app.logger.info('order placed order_id=%s correlation_id=%s',oid,cid)
    return jsonify(order_id=oid,status='PLACED',correlation_id=cid),201
@app.get('/health')
def health():return {'status':'ok'}
