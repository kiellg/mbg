# Chow - Food Delivery App

> A full-stack food delivery web application with a React/Vite frontend and a FastAPI backend. All data is stored in-memory (Python data structures) without an external database.

## Project Overview

Chow is a food delivery application that allows customers to browse restaurants, add items to a cart, apply coupons, choose a delivery method, and optionally schedule orders for a future time. An admin interface provides management capabilities over restaurants, users, and orders.

## Key Features

-   **Restaurant browsing**: browse, search, and filter restaurants by category
-   **Cart management**: add/remove items, view subtotal
-   **Checkout**: select delivery method (Walk \$5 / Bike \$8 / Car \$10), apply coupon codes
-   **Scheduled orders**: toggle "Schedule for later", pick a future datetime; backend validates the time falls within the restaurant's opening hours
-   **Payment flow**: post-checkout payment page with order summary
-   **Delivery tracking**: track active deliveries
-   **Rating & Reviews**: rate restaurants and give a review comment (optional)
-   **Favourites**: save restaurant and/or menu item as favourites
-   **Admin panel**: manage restaurants, users, orders
-   **Notifications**: in-app notification feed
-   **Session-based auth**: login/register with session cookies

## Architecture

| Service | Technology | Port | Description |
|------------------|------------------|------------------|-------------------|
| **Backend** | Python 3.10 + FastAPI + Uvicorn | `8000` | REST API, business logic, in-memory data |
| **Frontend** | React 19 + Vite + MUI | `1573` | Display along with the styling |

## Tech Stack

### Backend

-   **Python 3.10**
-   **FastAPI 0.129**: web framework
-   **Uvicorn 0.41**
-   **Pydantic v2**: request/response schema validation
-   **pytest + pytest-mock**: test framework

### Frontend

-   **React 19**
-   **Vite 8**: dev server and bundler
-   **MUI (Material UI) v6**: component library
-   **React Router v7**: client-side routing
-   **Axios**: HTTP client

## Project Structure

```         
mbg/
├── .github/
│   └── workflows/
│       └── pylint.yml           # Python linting CI workflow
├── backend/
│   ├── app/
│   │   ├── data/                # In-memory data stores (users, restaurants, orders, etc.)
│   │   ├── repositories/        # Data access layer (cart_repo, user_repo, etc.)
│   │   ├── routers/             # FastAPI route handlers (auth, carts, orders, checkout, etc.)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic (checkout_service, order_service, etc.)
│   │   ├── utils/               # Helper utilities
│   │   ├── dependencies.py      # FastAPI dependency injection
│   │   └── __init__.py
│   ├── tests/                   # pytest test suite
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Backend container image
│   └── __init__.py
├── frontend/
│   ├── public/                  
│   ├── src/
│   │   ├── api/                 # Axios API client modules
│   │   ├── components/          # Reusable UI components
│   │   │   ├── cart/            # Cart-related components
│   │   │   ├── menu/            # Menu-related components
│   │   │   ├── orders/          # Orders-related components
│   │   │   ├── restaurant/      # Restaurant-related components
│   │   │   └── shared/          # Shared UI components
│   │   ├── context/             # React context (CartContext, etc.)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   │   ├── admin/           # Admin page
│   │   │   ├── auth/            # Auth pages (login, register)
│   │   │   ├── cart/            # Cart page
│   │   │   ├── delivery/        # Delivery pages
│   │   │   ├── orders/          # Orders pages
│   │   │   ├── payment/         # Payment page
│   │   │   ├── profile/         # Profile pages
│   │   │   ├── restaurant/      # Restaurant pages
│   │   │   └── FavouritesPage.jsx
│   │   ├── theme/               # MUI theme configuration
│   │   ├── App.jsx              # Root app component
│   │   └── main.jsx             # React entry point
│   ├── package.json             # Node dependencies and scripts
│   ├── vite.config.js           # Vite configuration
│   └── index.html               # HTML entry point
├── mbgvenv/                     # Python virtual environment
├── reports/                     # Project reports/documentation
├── scrum/                       # Scrum artifacts
├── .gitignore
├── LICENSE
└── README.md
```

## Prerequisites

Ensure the following are installed before proceeding:

| Tool               | Minimum Version |
|--------------------|-----------------|
| **Docker**         | 24.x            |
| **Docker Compose** | v2 (plugin)     |
| **Git**            | Any             |

## Step-by-step Setup
> No environment variables are required. All configuration uses defaults.

### Step 1: Clone the Repository

``` bash
git clone https://github.com/kiellg/mbg.git
cd mbg
```

### Step 2: Build and Start All Services

``` bash
docker compose up --build
```

Expected output:

```         
mbg-backend   | INFO:     Started server process
mbg-backend   | INFO:     Waiting for application startup.
mbg-backend   | INFO:     Application startup complete.
mbg-backend   | INFO:     Uvicorn running on http://0.0.0.0:8000
mbg-frontend  | INFO:     Accepting connections at http://localhost:1573
```

### Step 3: Access the App

| Service                  | URL                            |
|--------------------------|--------------------------------|
| **Frontend (App)**       | <http://localhost:1573>        |
| **Backend API**          | <http://localhost:8000>        |
| **API Health Check**     | <http://localhost:8000/health> |
| **Interactive API Docs** | <http://localhost:8000/docs>   |

### How to stop

``` bash
docker compose up down
```

## Running Tests

The backend test suite uses **pytest** with mocking support via `pytest-mock`.

### Inside Docker

``` bash
docker compose exec backend pytest
```

### Locally (with venv activated)

``` bash
cd backend
pytest
```

### With Coverage Report

``` bash
pytest --cov=app --cov-report=term-missing
```

Test files are located in `backend/tests/`.

## Available Routers

| Router        | Prefix           | Description                             |
|---------------|------------------|-----------------------------------------|
| Auth          | `/auth`          | Registration, login, session management |
| Restaurants   | `/restaurants`   | Browse and search restaurants           |
| Carts         | `/cart`          | Manage cart items                       |
| Checkouts     | `/checkout`      | Place and schedule orders               |
| Orders        | `/orders`        | View order history and status           |
| Payments      | `/payments`      | Process payments                        |
| Deliveries    | `/orders`        | Track deliveries                        |
| Profile       | `/profile`       | User profile management                 |
| Coupons       | `/admin/coupons` | Coupon validation and application       |
| Reviews       | `/reviews`       | Restaurant reviews                      |
| Favourites    | `/favourites`    | Saved restaurant favourites             |
| Notifications | `/notifications` | In-app notifications                    |
| Admin         | `/admin`         | Admin management panel                  |
| Users         | `/users`         | User management (admin)                 |

## Team

-   Edgar Damien Sipayung
-   Eleonora Ansella Kartono
-   Yohanes Amelio Turnip
-   Yehezkiel Lbn Gaol
