# Savannah E-commerce API

A modern, secure REST API built with Django REST Framework that provides e-commerce functionality with Google OAuth integration and SMS notifications.

## 🚨 Deployment Note

> **Important:** This API is deployed on Render's free tier. The server may go to sleep after periods of inactivity and could take 30-60 seconds to wake up on the first request. Please be patient if your initial request seems slow.

## ✨ Features

- **Google OAuth Authentication**: Secure user authentication without password storage
- **Cookie-Based Authentication**: Enhanced security with HTTP-only cookies
- **Order Management**: Create and track orders with unique order codes
- **SMS Notifications**: Automatic order confirmation via Africa's Talking SMS gateway
- **Comprehensive Test Suite**: Unit, integration, and acceptance tests with pytest
- **API Documentation**: Interactive documentation with Swagger and ReDoc

## 🔄 API Flow

1. **Authentication**
   - User initiates Google OAuth flow
   - Backend exchanges OAuth code for tokens
   - Tokens are stored securely in HTTP-only cookies
   - Access token refreshed automatically when expired

2. **Customer Management**
   - New Google users get a customer profile automatically
   - **Important:** Before placing orders, new users must update their phone number

3. **Order Processing**
   - Authenticated users can create orders
   - System generates unique order codes automatically
   - SMS confirmation sent to customer's phone after order creation

## 🔐 Authentication Details

We chose cookie-based authentication over JWT tokens for these reasons:

- **Enhanced Security**: HTTP-only cookies cannot be accessed by JavaScript, protecting against XSS attacks
- **Simplified Flow**: No need for manual token management in frontend code
- **Automatic Transmission**: Cookies are sent automatically with each request
- **Built-in Expiration**: Cookie lifetimes managed by the browser

### Drawbacks of Our Approach

- **CSRF Vulnerability**: Requires proper CSRF protection for non-GET requests
- **Same-Origin Limitation**: Cookies work best when frontend and API are on same domain
- **Device Limitations**: Some mobile apps may have issues with cookie handling
- **Scaling Challenges**: Session state can complicate horizontal scaling

## 📚 API Endpoints

### Authentication
- `GET /accounts/login/` - Initiates Google OAuth flow
- `GET /accounts/google/login/callback/` - OAuth callback handler
- `POST /refresh-token/` - Refreshes an expired access token

### Customer Management
- `GET /api/customers/` - List current user's customer profile
- `POST /api/customers/` - Update customer profile (required before ordering)
- `GET /profile/` - View user profile details

### Order Management
- `GET /api/orders/` - List all orders for the current user
- `POST /api/orders/` - Create a new order
- `GET /api/orders/{id}/` - Get details of a specific order

### API Documentation
- `GET /api/v1/schema` - OpenAPI schema
- `GET /api/v1/schema/swagger-ui/` - Swagger UI documentation
- `GET /api/v1/schema/redoc/` - ReDoc documentation

## ⚡ Quick Start for New Users

1. **Authenticate with Google**
   - Visit `/accounts/login/` to sign in with your Google account

2. **Update Your Phone Number**
   - Before placing orders, send a POST request to `/api/customers/` with:
   ```json
   {
     "phone_number": "+1234567890"
   }
   ```
   - This step is **mandatory** before creating orders

3. **Create Your First Order**
   - Send a POST request to `/api/orders/` with:
   ```json
   {
     "total_amount": "99.99"
   }
   ```
   - You'll receive an SMS confirmation if your phone number is valid

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_coverage.py
```

## 🧑‍💻 Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## 📋 Technologies Used

- Django 5.1
- Django REST Framework
- PostgreSQL
- Google OAuth
- Africa's Talking SMS API
- drf-spectacular for API documentation