# Overview

This document outlines the design of a microservices-based, event-driven crypto trading platform. The platform consists of the following services:

- User Service
- Order Service
- Trade Service
- Wallet Service
- Notification Service
- Product Service (new)

Each service is responsible for a specific domain and communicates with other services through events and REST APIs.

## Services

### 1. User Service

**Responsibilities:**

- Manage user accounts, authentication, and authorization.
- Provide user-related information to other services.

**Endpoints:**

- `POST /api/users/register`: Register a new user.
- `POST /api/users/login`: Authenticate a user.
- `GET /api/users/profile`: Get user profile.
- `POST /api/users/validate`: Validate a token.
- `POST /api/users/refresh_token`: Refresh an access token.

**Communication:**

- Exposes REST APIs for user management.
- Publishes events like `UserCreated`, `UserUpdated`, and `UserDeleted`.

### 2. Order Service

**Responsibilities:**

- Manage orders, including creation, retrieval, updating, and deletion.
- Validate orders and publish events for order processing.

**Endpoints:**

- `POST /api/orders`: Create a new order.
- `GET /api/orders/{id}`: Retrieve order details.
- `GET /api/orders`: Retrieve all orders.
- `PUT /api/orders/{id}`: Update order details.
- `DELETE /api/orders/{id}`: Cancel an order.

**Communication:**

- Exposes REST APIs for order management.
- Publishes events like `OrderCreated`, `OrderUpdated`, and `OrderCancelled`.
- Consumes events like `TradeExecuted` to update order status.

### 3. Trade Service

**Responsibilities:**

- Execute trades based on orders.
- Match buy and sell orders and publish trade execution events.

**Endpoints:**

- `POST /api/trades`: Execute a trade.
- `GET /api/trades/{id}`: Retrieve trade details.
- `GET /api/trades`: Retrieve all trades.
- `PUT /api/trades/{id}`: Update trade details.
- `DELETE /api/trades/{id}`: Delete a trade.

**Communication:**

- Exposes REST APIs for trade management.
- Consumes events like `OrderCreated` to execute trades.
- Publishes events like `TradeExecuted`.

### 4. Wallet Service

**Responsibilities:**

- Manage user wallets and balances.
- Update wallet balances based on trade executions.

**Endpoints:**

- `POST /api/wallets`: Create a new wallet.
- `GET /api/wallets/{id}`: Retrieve wallet details.
- `GET /api/wallets`: Retrieve all wallets.
- `PUT /api/wallets/{id}`: Update wallet balance.
- `DELETE /api/wallets/{id}`: Delete a wallet.

**Communication:**

- Exposes REST APIs for wallet management.
- Consumes events like `TradeExecuted` to update wallet balances.
- Publishes events like `WalletUpdated`.

### 5. Notification Service

**Responsibilities:**

- Send notifications to users about their trades, orders, and wallet updates.

**Endpoints:**

- `POST /api/notifications`: Send a notification.
- `GET /api/notifications/{id}`: Retrieve notification details.
- `GET /api/notifications`: Retrieve all notifications.

**Communication:**

- Exposes REST APIs for notification management.
- Consumes events like `OrderCreated`, `TradeExecuted`, and `WalletUpdated` to send notifications.

### 6. Product Service (New)

**Responsibilities:**

- Manage products and track the quantity of products a user owns.

**Endpoints:**

- `POST /api/products`: Create a new product.
- `GET /api/products/{id}`: Retrieve product details.
- `GET /api/products`: Retrieve all products.
- `PUT /api/products/{id}`: Update product details.
- `DELETE /api/products/{id}`: Delete a product.
- `GET /api/products/user/{userId}`: Retrieve products owned by a user.

**Communication:**

- Exposes REST APIs for product management.
- Consumes events like `TradeExecuted` to update product quantities.
- Publishes events like `ProductUpdated`.

## Event-Driven Communication

The services communicate with each other using an event-driven architecture. The following events are used:

**User Events:**

- `UserCreated`
- `UserUpdated`
- `UserDeleted`

**Order Events:**

- `OrderCreated`
- `OrderUpdated`
- `OrderCancelled`

**Trade Events:**

- `TradeExecuted`

**Wallet Events:**

- `WalletUpdated`

**Product Events:**

- `ProductUpdated`

## Detailed Flows

### 1. Order Placement Flow

**User places an order:**

1. The user sends a request to the Order Service to place an order.
2. The Order Service validates the order and checks the user's balance by querying the Wallet Service.

**Check user balance:**

1. The Order Service sends a request to the Wallet Service to check if the user has sufficient balance.
2. If the user has sufficient balance, the Order Service proceeds to create the order.
3. If the user does not have sufficient balance, the Order Service returns an error response.

**Create order:**

1. The Order Service creates the order and publishes an `OrderCreated` event.

**Order processing:**

1. The Trade Service consumes the `OrderCreated` event and attempts to match the order.
2. If the order is matched fully or partially, the Trade Service publishes a `TradeExecuted` event.

**Update wallet balance:**

1. The Wallet Service consumes the `TradeExecuted` event and updates the user's wallet balance.
2. The Wallet Service publishes a `WalletUpdated` event.

**Update product quantities:**

1. The Product Service consumes the `TradeExecuted` event and updates the quantities of products owned by the user.
2. The Product Service publishes a `ProductUpdated` event.

**Send notifications:**

1. The Notification Service consumes the `OrderCreated`, `TradeExecuted`, and `WalletUpdated` events to notify the user about the order status, trade execution, and wallet balance update.

### 2. Trade Execution Flow

**Order matching:**

1. The Trade Service consumes the `OrderCreated` event and attempts to match the order with existing orders.
2. If a match is found, the Trade Service executes the trade and publishes a `TradeExecuted` event.

**Update wallet balance:**

1. The Wallet Service consumes the `TradeExecuted` event and updates the user's wallet balance.
2. The Wallet Service publishes a `WalletUpdated` event.

**Update product quantities:**

1. The Product Service consumes the `TradeExecuted` event and updates the quantities of products owned by the user.
2. The Product Service publishes a `ProductUpdated` event.

**Send notifications:**

1. The Notification Service consumes the `TradeExecuted` and `WalletUpdated` events to notify the user about the trade execution and wallet balance update.

## Correlation Between Orders and Trades

**Order Creation:**

1. When a user places an order, the Order Service creates an order record with details such as the user ID, order type (buy/sell), symbol, quantity, price, and status.
2. The Order Service publishes an `OrderCreated` event with the order details.

**Order Matching:**

1. The Trade Service consumes the `OrderCreated` event and attempts to match the order with existing orders in the order book.
2. If a match is found, the Trade Service creates a trade record with details such as the trade ID, buy order ID, sell order ID, symbol, quantity, price, and status.
3. The Trade Service publishes a `TradeExecuted` event with the trade details.

**Updating Wallets:**
**Publish WalletUpdated event:**
### Example Flows

#### Example Flow 1: User Registration and Order Placement

1. **User Registration:**
    - The user sends a `POST /api/users` request to the User Service to create a new account.
    - The User Service creates the user and publishes a `UserCreated` event.

2. **Order Placement:**
    - The user sends a `POST /api/orders` request to the Order Service to place a new order.
    - The Order Service validates the order and checks the user's balance by querying the Wallet Service.
    - If the balance is sufficient, the Order Service creates the order and publishes an `OrderCreated` event.

3. **Order Processing:**
    - The Trade Service consumes the `OrderCreated` event and attempts to match the order.
    - If a match is found, the Trade Service executes the trade and publishes a `TradeExecuted` event.

4. **Wallet Update:**
    - The Wallet Service consumes the `TradeExecuted` event and updates the user's wallet balance.
    - The Wallet Service publishes a `WalletUpdated` event.

5. **Notification:**
    - The Notification Service consumes the `OrderCreated`, `TradeExecuted`, and `WalletUpdated` events to notify the user about the order status, trade execution, and wallet balance update.

#### Example Flow 2: Product Management

1. **Product Creation:**
    - An admin sends a `POST /api/products` request to the Product Service to create a new product.
    - The Product Service creates the product and publishes a `ProductUpdated` event.

2. **Product Update:**
    - The admin sends a `PUT /api/products/{id}` request to update product details.
    - The Product Service updates the product and publishes a `ProductUpdated` event.

3. **Product Deletion:**
    - The admin sends a `DELETE /api/products/{id}` request to delete a product.
    - The Product Service deletes the product and publishes a `ProductUpdated` event.

4. **Product Quantity Update:**
    - The Product Service consumes the `TradeExecuted` event to update the quantities of products owned by the user.
    - The Product Service publishes a `ProductUpdated` event.

5. **Notification:**
    - The Notification Service consumes the `ProductUpdated` event to notify users about product updates.


6. After updating the wallet balances, the Wallet Service publishes a `WalletUpdated` event.
7. This event contains details about the updated wallet balances, including the user ID and the new balance.

### Example Flow

#### 1. Order Creation

- User A places a buy order for 10 BTC at $50,000 each.
- The Order Service creates an order record:
  ```json
  {
    "orderId": "order123",
    "userId": "userA",
    "type": "buy",
    "symbol": "BTC",
    "quantity": 10,
    "price": 50000,
    "status": "pending"
  }

#### 2. Order Matching

- User B places a sell order for 5 BTC at $50,000 each.

- The Order Service creates an order record:
  ```json
  {
  "orderId": "order456",
  "userId": "userB",
  "type": "sell",
  "symbol": "BTC",
  "quantity": 5,
  "price": 50000,
  "status": "pending"
  }

- The Order Service publishes an OrderCreated event:
  ```json
  {
  "orderId": "order456",
  "userId": "userB",
  "type": "sell",
  "symbol": "BTC",
  "quantity": 5,
  "price": 50000
  }

- The Trade Service consumes the OrderCreated events and matches the buy order from User A with the sell order from User B.
- The Trade Service creates a trade record:
  ```json
  {
  "tradeId": "trade789",
  "buyOrderId": "order123",
  "sellOrderId": "order456",
  "symbol": "BTC",
  "quantity": 5,
  "price": 50000,
  "status": "executed"
  }

- The Trade Service publishes a TradeExecuted event:
  ```json
  {
  "tradeId": "trade789",
  "buyOrderId": "order123",
  "sellOrderId": "order456",
  "symbol": "BTC",
  "quantity": 5,
  "price": 50000
  }

#### 3. Updating Wallets

- The Wallet Service consumes the TradeExecuted event and updates the wallets of User A and User B.
- User A's Wallet:
- User A's wallet balance is decreased by the total cost of the trade (5 BTC * $50,000 = $250,000).
- User A's wallet balance is updated
  ```json
  {
    "userId": "userA",
    "balance": {
        "USD": previous_balance - 250000,
        "BTC": previous_balance + 5
    }
  }
- User B's Wallet:
  - User B's wallet balance is increased by the total cost of the trade (5 BTC * $50,000 = $250,000).
  - User B's wallet balance is updated:
    ```json
    {
      "userId": "userB",
      "balance": {
          "USD": previous_balance + 250000,
          "BTC": previous_balance - 5
      }
    }
    ```

- The Wallet Service publishes WalletUpdated events for both users:
  ```json
  {
    "userId": "userA",
    "balance": {
        "USD": updated_balance,
        "BTC": updated_balance
    }
  }
  ```
  ```json
  {
  "userId": "userB",
  "balance": {
        "USD": updated_balance,
        "BTC": updated_balance
    }
  }
  ```
**Notify user:**

1. The Notification Service consumes the `WalletUpdated` event.
2. It sends a notification to the user about the updated wallet balance.

## Conclusion

This document provides a detailed overview of the microservices-based, event-driven architecture for a crypto trading platform. Each service is designed to handle specific responsibilities and communicate with other services through well-defined events and REST APIs. This architecture ensures scalability, maintainability, and flexibility in handling various aspects of the trading platform.
