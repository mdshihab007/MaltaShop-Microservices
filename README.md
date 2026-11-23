# MaltaShop place-order prototype
Two Python services and RabbitMQ. Order owns orders.db; Notification owns notifications.db. A POST creates an order and publishes OrderPlaced. The consumer saves a processed marker and logs the shared correlation ID.

## Start
`docker compose up --build`

## Test
`curl -i -X POST http://localhost:5000/orders -H 'Content-Type: application/json' -H 'X-Correlation-ID: demo-123' -d '{"item":"headphones"}'`

`docker compose logs order notification`

## Configuration
`BROKER_HOST` (default rabbitmq). Port 5000 is published for local testing. Persistent SQLite data is in Docker volumes.

## Important limitations
Educational demonstration only. Not production ready: no authentication, no payment/inventory, no transactional outbox, no dead-letter queue, no TLS, and no production-grade HTTP server. A broker failure after the database insert can leave an event unpublished. Add an outbox worker before real deployment. Screenshots and actual CI results must be captured by running the code.
