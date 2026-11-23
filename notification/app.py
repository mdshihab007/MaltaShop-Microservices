import os, sqlite3, json, time, logging
import pika
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
os.makedirs('/data',exist_ok=True);DB='/data/notifications.db'
with sqlite3.connect(DB) as c:c.execute('CREATE TABLE IF NOT EXISTS processed(order_id TEXT PRIMARY KEY, correlation_id TEXT)')
while True:
 try:
  connection=pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('BROKER_HOST','rabbitmq')))
  ch=connection.channel();ch.queue_declare(queue='order_placed',durable=True);ch.basic_qos(prefetch_count=1)
  def handle(channel,method,properties,body):
   event=json.loads(body)
   with sqlite3.connect(DB) as c:c.execute('INSERT OR IGNORE INTO processed VALUES (?,?)',(event['order_id'],event['correlation_id']))
   logging.info('OrderPlaced consumed order_id=%s correlation_id=%s',event['order_id'],event['correlation_id'])
   channel.basic_ack(delivery_tag=method.delivery_tag)
  ch.basic_consume(queue='order_placed',on_message_callback=handle);ch.start_consuming()
 except Exception:logging.exception('consumer reconnecting');time.sleep(5)
