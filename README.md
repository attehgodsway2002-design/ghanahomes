# 🏠 GhanaHomes - Property Rental Platform

[![Django](https://img.shields.io/badge/Django-5.2.8-darkgreen.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A modern, full-featured property rental platform built with Django. Connect landlords and tenants across Ghana with secure transactions, real-time communication, and comprehensive management tools.

**Demo:** [ghanahomes.com](https://ghanahomes.com) | **Docs:** [View Documentation](./docs/) | **Support:** [Report Issues](https://github.com/yourusername/ghanahomes/issues)

---

## ✨ Features

### 🏘️ Property Management
- **List Properties** - Create detailed listings with images and videos
- **Advanced Search** - Filter by location, price, type, amenities
- **Favorites System** - Save properties for later viewing
- **Reviews & Ratings** - Community feedback and property ratings
- **View Analytics** - Track property views and user interest

### 👥 User System
- **Secure Authentication** - Email verification and secure password reset
- **User Profiles** - Comprehensive profile customization
- **Subscription Plans** - Flexible pricing tiers for landlords
- **Verification System** - Admin approval for landlord verification
- **Audit Trail** - Complete logging of login history and system changes
- **Admin Dashboard** - Real-time KPI monitoring and bulk actions

### 💬 Real-time Communication
- **WebSocket Chat** - Instant messaging between landlords and tenants
- **Conversation History** - Access full chat archives
- **Read Receipts** - Know when messages are read
- **Chat Room Management** - Organized by property inquiries

### 💰 Payment Integration
- **Paystack Integration** - Secure online payment processing
- **Transaction Tracking** - Complete payment history and receipts
- **Invoice Management** - Automated digital invoices with PDF export
- **Multi-currency Support** - GHS, USD, EUR (via Paystack)
- **Admin Notifications** - Real-time alerts for high-value payments

### 📊 Admin Dashboard & Monitoring
- **KPI Dashboard** - Real-time metrics and analytics
- **User Management** - Create, verify, and manage users
- **Property Verification** - Review and approve property listings
- **Payment Tracking** - Monitor all transactions and refunds
- **Audit Reports** - Complete action logs and security audit trails
- **Bulk Actions** - Mark featured, verify, deactivate, and more
- **Email Notifications** - Automatic alerts for verification requests, payments, inquiries

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | Django | 5.2.8 |
| **Python Version** | Python | 3.11.9 |
| **Frontend** | Bootstrap 5 + Chart.js | Latest |
| **Database** | SQLite/PostgreSQL | 12+ |
| **Real-time Communication** | Django Channels | Latest |
| **Payments** | Paystack API | v2 |
| **Email** | SMTP (Gmail/Custom) | Configurable |
| **Task Queue** | Django-Q | Optional |
| **Caching** | Redis | Optional |
| **Web Server** | Gunicorn/Daphne | Production Ready |

---

## 📁 Project Structure

```
ghanahomes/
├── accounts/                    # User authentication, verification & audit
│   ├── models.py               # User, VerificationRequest, AuditLog models
│   ├── views.py                # Auth, verification, profile views
│   ├── admin.py                # User admin customization
│   ├── email_utils.py          # Email templates and sending functions
│   ├── verification_admin_views.py  # Verification dashboard & actions
│   ├── forms.py                # Registration, login, verification forms
│   └── migrations/             # Database migrations
│
├── properties/                  # Property listings and management
│   ├── models.py               # Property, Category, Image, Review models
│   ├── views.py                # Property CRUD, search, analytics
│   ├── admin.py                # Property admin with filters
│   ├── forms.py                # Property creation & editing
│   ├── signals.py              # Auto-generated signals
│   └── migrations/
│
├── subscriptions/              # Subscription & plan management
│   ├── models.py               # SubscriptionPlan, Subscription models
│   ├── views.py                # Plan selection & management
│   ├── admin.py                # Subscription admin
│   ├── free_tier_utils.py      # Free tier restrictions
│   └── management/commands/    # Periodic renewal tasks
│
├── payments/                   # Payment processing & tracking
│   ├── models.py               # Payment transaction model
│   ├── views.py                # Paystack integration, callbacks
│   ├── admin.py                # Payment tracking admin
│   ├── utils.py                # Paystack utilities & verification
│   ├── pdf.py                  # PDF invoice generation
│   ├── tasks.py                # Email notifications
│   └── email_monitoring.py     # Webhook verification
│
├── chat/                       # Real-time messaging system
│   ├── models.py               # ChatRoom, Message models
│   ├── views.py                # Chat listing, messaging
│   ├── consumers.py            # WebSocket consumers
│   ├── admin.py                # Chat admin
│   ├── forms.py                # Message form
│   ├── routing.py              # WebSocket URL routing
│   └── signals.py              # Chat signals
│
├── ghanahomes/                 # Project configuration
│   ├── settings.py             # Django settings & configuration
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI configuration
│   ├── asgi.py                 # ASGI configuration (Channels)
│   ├── admin_views.py          # Custom admin dashboard views
│   ├── caching.py              # Caching configuration
│   ├── security.py             # Security settings
│   ├── error_handling.py       # Error handlers
│   └── patches.py              # Library patches
│
├── templates/                  # HTML templates
│   ├── base.html               # Base template with navigation
│   ├── accounts/               # Login, register, profile templates
│   ├── properties/             # Property listing & detail templates
│   ├── subscriptions/          # Plan selection templates
│   ├── payments/               # Payment confirmation templates
│   ├── chat/                   # Chat interface templates
│   ├── admin/                  # Custom admin templates
│   ├── emails/                 # Email templates (35+ templates)
│   ├── errors/                 # Error page templates
│   └── includes/               # Reusable template components
│
├── static/                     # Static assets (collected via collectstatic)
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Static images
│
├── media/                      # User-uploaded files (in .gitignore)
│   ├── properties/images/      # Property photos
│   ├── receipts/               # Payment PDF receipts
│   └── verifications/          # User verification documents
│
├── logs/                       # Application logs (in .gitignore)
│
├── docs/                       # Documentation
│   ├── ADMIN_COMPLETE_AUDIT.md
│   ├── ADMIN_DASHBOARD_COMPLETE.md
│   ├── ADMIN_NOTIFICATIONS_SETUP.md
│   └── VERIFICATION_SYSTEM.md
│
├── scripts/                    # Utility scripts
│   ├── create_subscription_plans.py
│   ├── list_payments.py
│   └── payment_flow_summary.py
│
├── manage.py                   # Django management CLI
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (NEVER commit)
├── .gitignore                  # Git ignore rules
├── db.sqlite3                  # Development database (in .gitignore)
└── README.md                   # This file
```

### Key Directories
- **`accounts/`** - 5 models, 18+ forms and views
- **`properties/`** - 7 models, advanced search and analytics
- **`payments/`** - Paystack integration with webhook handling
- **`chat/`** - WebSocket real-time messaging
- **`templates/emails/`** - 35+ email templates for all events

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip and virtualenv
- PostgreSQL 12+ (optional, SQLite for development)
- Git

### Installation & Setup

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/ghanahomes.git
cd ghanahomes
```

**2. Create Virtual Environment**
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
```bash
# Create .env file
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - uses SQLite by default)
# DATABASE_URL=postgresql://user:password@localhost:5432/ghanahomes

# Email Configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Paystack (payment processing)
PAYSTACK_PUBLIC_KEY=your-paystack-pk-key
PAYSTACK_SECRET_KEY=your-paystack-sk-key

# Admin Email (for notifications)
ADMIN_EMAIL=admin@example.com
```

**5. Run Migrations**
```bash
python manage.py migrate
```

**6. Create Superuser (Admin Account)**
```bash
python manage.py createsuperuser
# Follow the prompts to create admin account
```

**7. Create Subscription Plans**
```bash
python manage.py shell
>>> from subscriptions.models import SubscriptionPlan
>>> SubscriptionPlan.objects.create(
...     name="Free",
...     is_free=True,
...     property_limit=1
... )
>>> SubscriptionPlan.objects.create(
...     name="Professional",
...     is_free=False,
...     property_limit=10,
...     price_monthly=99.99
... )
```

**8. Run Development Server**
```bash
python manage.py runserver
```

**Access the Application:**
- **Frontend:** http://localhost:8000
- **Admin Dashboard:** http://localhost:8000/admin/
- **Verification Dashboard:** http://localhost:8000/accounts/admin/verification/

---

## 👨‍💼 Admin Dashboard & Features

### Access Points
- **Django Admin** - Full model CRUD at `/admin/` 
- **KPI Dashboard** - Real-time metrics at `/admin/dashboard/`
- **Verification Dashboard** - Review requests at `/accounts/admin/verification/`
- **User Management** - User administration at `/admin/accounts/user/`
- **Property Management** - Property approval at `/admin/properties/property/`
- **Payment Tracking** - Transaction monitoring at `/admin/payments/payment/`

### Admin Capabilities
✅ **18 Models** fully registered with enhanced admin interfaces  
✅ **User Verification** - Approve/decline landlord verification requests  
✅ **Property Moderation** - Feature properties, manage listings  
✅ **Payment Monitoring** - Track all transactions with webhooks  
✅ **Bulk Actions** - Multi-select operations (mark featured, verify, etc.)  
✅ **Search & Filtering** - Advanced filters on all models  
✅ **Admin Notifications** - Email alerts for important events (7 notification types)  
✅ **Read-only Audit** - Immutable audit logs for compliance  
✅ **Inline Editing** - Edit related objects inline  
✅ **Image Previews** - Thumbnail previews in list views  

### Key Admin Models
| Model | Count | Admin Features |
|-------|-------|----------------|
| **User** | Custom | Verification status, audit trail |
| **Property** | 7 | Bulk feature, image gallery, filters |
| **Payment** | 1 | Status tracking, amount filters |
| **Subscription** | 2 | Plan management, renewal tracking |
| **VerificationRequest** | NEW | Dashboard, approve/decline actions |
| **Audit Models** | 4 | Read-only compliance logs |
| **Chat** | 2 | Search conversations, moderation |

## 📊 Database Schema

### User-Related (5 models)
- **User** - Custom user with verification, company info
- **VerificationRequest** - Landlord verification requests with documents
- **AuditLog** - System action logging (read-only)
- **LoginHistory** - Login tracking and session info
- **PaymentAudit** - Payment state change tracking (read-only)

### Property-Related (7 models)
- **Property** - Main property listing with details
- **PropertyCategory** - Property type categories
- **PropertyType** - Apartment, house, commercial, etc.
- **PropertyImage** - Property photos with ordering
- **PropertyVideo** - Video links and embedded media
- **PropertyReview** - User ratings and reviews
- **PropertyView** - Analytics on view counts
- **Favorite** - User saved properties

### Transaction-Related (1 model)
- **Payment** - Paystack transaction records with webhook data

### Communication (2 models)
- **ChatRoom** - Conversations between landlord/tenant
- **Message** - Individual messages with read receipts

### Subscription (2 models)
- **SubscriptionPlan** - Pricing tiers and feature limits
- **Subscription** - User subscription status and renewal

**Total: 18+ models with complete admin interface**

---

## � User Roles & Permissions

### Landlord/Property Owner
- ✅ Register account and get verified
- ✅ Post unlimited properties (based on subscription plan)
- ✅ Upload multiple images and videos per property
- ✅ Manage property listings and pricing
- ✅ View property analytics (views, inquiries)
- ✅ Subscribe to premium plans for higher property limits
- ✅ Receive inquiries from potential tenants
- ✅ Chat with interested tenants
- ✅ Access transaction history

### Tenant/Property Seeker
- ✅ Browse all available properties
- ✅ Search with advanced filters
- ✅ Save favorite properties
- ✅ Leave reviews and ratings
- ✅ Message property owners
- ✅ Schedule property viewings
- ✅ View complete property details and images
- ✅ No subscription required

### Admin/Platform Manager
- ✅ Complete system access
- ✅ Verify landlord accounts
- ✅ Approve/decline property listings
- ✅ Monitor all transactions
- ✅ Manage subscription plans
- ✅ View audit logs and analytics
- ✅ Send bulk notifications
- ✅ Configure system settings
- ✅ Generate reports

---

## 🔧 Common Tasks

### Verify User as Admin
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(username='john')
>>> user.is_verified = True
>>> user.save()
```

### Create Test Property
```bash
python manage.py shell
>>> from properties.models import Property
>>> Property.objects.create(
...     title="Test Property",
...     owner=user,
...     price=5000,
...     bedrooms=2,
...     bathrooms=1
... )
```

### Run Management Commands
```bash
# Check subscription expiries
python manage.py check_subscription_reminders

# Mark expired properties
python manage.py mark_expired_properties

# Verify payment status
python manage.py verify_payments
```

---

## 📊 Database Models

### Accounts (5 models)
- **User** - Custom user model with verification
- **AuditLog** - System action tracking
- **LoginHistory** - User login records
- **PaymentAudit** - Payment change tracking
- **PropertyEditHistory** - Property modification log

### Properties (7 models)
- **Property** - Main property model
- **PropertyCategory** - Property types
- **PropertyImage** - Property photos
- **PropertyVideo** - Property videos
- **Favorite** - User favorites
- **PropertyView** - View analytics
- **PropertyReview** - User reviews

### Subscriptions (2 models)
- **SubscriptionPlan** - Pricing tiers
- **Subscription** - User subscriptions

### Payments (1 model)
- **Payment** - Transaction records

### Chat (2 models)
- **ChatRoom** - Conversations
- **Message** - Messages

---

## 🔐 Security Features

### Authentication & Authorization
✅ **Custom User Model** - Email-based authentication  
✅ **Secure Password** - PBKDF2 hashing with salt  
✅ **Email Verification** - Token-based account verification  
✅ **Password Reset** - Time-limited secure reset links  
✅ **Session Management** - Secure session handling  
✅ **CSRF Protection** - CSRF tokens on all forms  
✅ **Permission Checks** - View-level access control  

### Data Protection
✅ **SQL Injection Prevention** - Django ORM + parameterized queries  
✅ **XSS Protection** - Template auto-escaping  
✅ **Rate Limiting** - API rate limiting on payments  
✅ **Input Validation** - Form and model validation  
✅ **File Upload Security** - Restricted file types and sizes  

### Audit & Compliance
✅ **Audit Logging** - All changes logged (read-only)  
✅ **Login Tracking** - Login history with timestamps  
✅ **Payment Audit Trail** - Transaction state changes logged  
✅ **Property Edit History** - All modifications tracked  
✅ **Data Integrity** - Immutable audit models  

### API Security
✅ **Webhook Verification** - Paystack signature validation  
✅ **HTTPS Ready** - Secure header configuration  
✅ **Secure Headers** - XSS-Protection, CSP, etc.  
✅ **CORS Configuration** - Configurable cross-origin requests  

### Sensitive Data
⚠️ **Never commit:** `.env` files, database files, media uploads  
✅ **Environment variables** - All secrets in .env  
✅ **Database isolation** - Separate dev/production databases  
✅ **Media files** - Excluded from git via .gitignore  

---

## 📚 Documentation

The project includes comprehensive documentation:

- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[ADMIN_NOTIFICATIONS_SETUP.md](ADMIN_NOTIFICATIONS_SETUP.md)** - Admin email notification system
- **[VERIFICATION_SYSTEM.md](docs/VERIFICATION_SYSTEM.md)** - User verification workflow
- **[ADMIN_DASHBOARD_COMPLETE.md](docs/ADMIN_DASHBOARD_COMPLETE.md)** - Admin interface features
- **[ADMIN_COMPLETE_AUDIT.md](docs/ADMIN_COMPLETE_AUDIT.md)** - Full model inventory
- **[docs/](docs/)** - Additional documentation and guides

---

## 🧪 Testing

Run tests to ensure everything works correctly:

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test properties
python manage.py test payments

# Run with verbosity
python manage.py test --verbosity=2

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Files
- `accounts/tests_auth.py` - Authentication tests
- `accounts/tests_audit.py` - Audit logging tests
- `accounts/tests_password_reset.py` - Password reset tests
- `properties/tests.py` - Property model and view tests
- `properties/tests_views.py` - Property view tests
- `payments/tests.py` - Payment integration tests
- `chat/tests.py` - Chat functionality tests
- `subscriptions/tests.py` - Subscription tests

---

## 📦 Deployment

### Pre-Deployment Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure production `ALLOWED_HOSTS`
- [ ] Use strong, randomly generated `SECRET_KEY`
- [ ] Setup PostgreSQL (recommended for production)
- [ ] Configure SSL/HTTPS certificate
- [ ] Setup email backend (SMTP)
- [ ] Configure Paystack (use live mode, not test)
- [ ] Setup Redis for caching (optional but recommended)
- [ ] Configure static files collection
- [ ] Setup logging and monitoring
- [ ] Enable security middleware

### Environment Variables for Production
```env
DEBUG=False
SECRET_KEY=your-strong-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/ghanahomes

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Paystack (Live mode)
PAYSTACK_PUBLIC_KEY=your-live-pk-key
PAYSTACK_SECRET_KEY=your-live-sk-key
```

### Deploy with Gunicorn + Nginx

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Run with Gunicorn:**
```bash
gunicorn ghanahomes.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --access-logfile - \
    --error-logfile -
```

**Systemd Service (Linux):**
```ini
[Unit]
Description=GhanaHomes Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/ghanahomes/app
ExecStart=/home/ghanahomes/app/.venv/bin/gunicorn \
    ghanahomes.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4

[Install]
WantedBy=multi-user.target
```

**Nginx Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ghanahomes/app/staticfiles/;
    }

    location /media/ {
        alias /home/ghanahomes/app/media/;
    }
}
```

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "ghanahomes.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t ghanahomes .
docker run -p 8000:8000 --env-file .env ghanahomes
```

---

## 🤝 Support & Troubleshooting

### Common Issues & Solutions

**Issue: Database connection error**
```bash
# Check PostgreSQL is running and accessible
psql -U username -d database_name

# Verify DATABASE_URL in .env is correct
# Test connection with Django
python manage.py dbshell
```

**Issue: Static files not loading in production**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL in settings
# Verify Nginx/web server is configured to serve /static/
```

**Issue: Email not sending**
```bash
# Check email configuration in .env
# For Gmail: Enable "App passwords" (2FA required)
# Test email sending
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
```

**Issue: Paystack webhook not working**
```bash
# Check PAYSTACK_SECRET_KEY is set correctly in .env
# Verify webhook URL in Paystack dashboard matches your deployment
# Check webhook logs in Django admin
```

**Issue: WebSocket/Chat not connecting**
```bash
# Ensure Daphne is installed: pip install daphne
# For development, run: daphne -b 0.0.0.0 -p 8000 ghanahomes.asgi:application
# For production, ensure ASGI is properly configured with your web server
# Check that WebSocket URL in templates matches your domain
```

**Issue: Migrations not applying**
```bash
# Check for migration conflicts
python manage.py showmigrations

# If stuck, create empty migration
python manage.py makemigrations --empty app_name --name migration_name

# Check migration file for issues and manually fix if needed
```

### Logging & Debugging

Enable debug logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Getting Help

1. **Check Documentation** - See [docs/](docs/) folder
2. **Review Issue** - Browse [GitHub Issues](https://github.com/yourusername/ghanahomes/issues)
3. **Check Logs** - Review application logs in `logs/` folder
4. **Run Tests** - Execute `python manage.py test` to identify issues
5. **Create Issue** - [Report a bug](https://github.com/yourusername/ghanahomes/issues/new)

---

## 📋 Version & Updates

### Current Version: v1.0.0

**Latest Release Features:**
- ✅ Complete user authentication system with email verification
- ✅ Property listing and management with images/videos
- ✅ Real-time chat messaging via WebSocket (Django Channels)
- ✅ Subscription plans with different property limits
- ✅ Paystack payment integration with webhook handling
- ✅ Comprehensive admin dashboard with 18 models
- ✅ Email notification system (35+ templates)
- ✅ Complete audit logging for compliance
- ✅ User verification system for landlords
- ✅ Advanced property search and filtering
- ✅ Favorites, reviews, and analytics
- ✅ Production-ready deployment guides

### Planned Features

**v1.1.0 (Coming Soon)**
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Bulk property upload
- [ ] Property scheduling/calendar
- [ ] Enhanced search with maps
- [ ] Video call integration
- [ ] SMS notifications
- [ ] Multi-language support

**v1.2.0 (Future)**
- [ ] AI property recommendations
- [ ] Property valuation tool
- [ ] Virtual tours (3D)
- [ ] Mortgage calculator
- [ ] Tenant background checks
- [ ] Property insurance integration
- [ ] Maintenance request system

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and updates.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
4. **Make your changes** and commit (`git commit -m 'Add AmazingFeature'`)
5. **Push to your branch** (`git push origin feature/AmazingFeature`)
6. **Open a Pull Request** with a clear description

### Development Guidelines
- Follow Django and Python best practices
- Write tests for new features
- Update documentation
- Ensure code passes `flake8` linting
- Use meaningful commit messages

## 👨‍💻 Authors

- **Huntsman** - Initial development and project lead
- **Contributors** - Welcome to contribute!

## 📞 Contact & Support

- **Email:** [your-email@example.com](mailto:your-email@example.com)
- **Twitter:** [@yourusername](https://twitter.com/yourusername)
- **LinkedIn:** [Your Profile](https://linkedin.com/in/yourprofile)
- **Website:** [yourdomain.com](https://yourdomain.com)

---

## 🙏 Acknowledgments

Special thanks to:
- Django community for the excellent framework
- Bootstrap for UI components
- Paystack for payment processing
- Chart.js for analytics visualizations
- All contributors and supporters

---

<div align="center">

**Made with ❤️ for Ghana's Real Estate Community**

⭐ If you find this project helpful, please consider giving it a star on GitHub!

[Star on GitHub](https://github.com/yourusername/ghanahomes) · [Report Bug](https://github.com/yourusername/ghanahomes/issues) · [Request Feature](https://github.com/yourusername/ghanahomes/issues)

</div>
