# Admin Dashboard & Management System - Complete Documentation

## Overview
The GhanaHomes platform now includes a comprehensive admin dashboard for managing users, properties, payments, subscriptions, and analytics. All admin features are restricted to staff members and provide real-time insights into platform performance.

## Access & Authentication

### Staff Member Access
All admin features are protected by the `@staff_member_required` decorator. To access admin features:

1. User must be marked as `is_staff=True` in Django admin
2. Navigate to admin dropdown menu in navbar (visible only for staff)
3. Select the desired admin panel

### Admin Dropdown Menu
Once authenticated and marked as staff, users see the admin section in their profile dropdown:
- Admin Dashboard (main KPI view)
- Manage Users
- Manage Properties
- Manage Payments
- Manage Subscriptions
- Analytics & Reports

## Admin Views & Features

### 1. Admin Dashboard (`/admin/dashboard/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L1)

Main KPI dashboard showing comprehensive platform overview.

**Key Metrics**:
- **User Statistics**: Total users, landlord/tenant breakdown, verified count, new users (week/month)
- **Property Statistics**: Total, available, rented, pending, new this week
- **Subscription Statistics**: Active, expired, free vs paid
- **Payment Statistics**: Total, completed, failed, pending
- **Revenue Statistics**: Total, this month, this week
- **Chat Statistics**: Total chats, messages, active conversations

**Visualizations** (Chart.js):
- 7-day user registration trend (line chart)
- 7-day revenue trend (line chart)
- User type breakdown (doughnut chart)
- Property status breakdown (doughnut chart)

**Recent Activity**:
- Last 5 registered users
- Last 5 listed properties
- Last 5 payments
- Top performing subscription plans

**Template**: [templates/admin/dashboard.html](templates/admin/dashboard.html)

### 2. User Management (`/admin/users/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L68)

Complete user management with filtering and search capabilities.

**Features**:
- **Search**: By username, email, or full name
- **Filter by User Type**: Landlords or Tenants
- **Filter by Verification Status**: Verified or Unverified
- **Quick Edit**: Direct link to Django admin for detailed editing
- **Display**: Username, email, user type, verification status, join date

**Template**: [templates/admin/users.html](templates/admin/users.html)

### 3. Property Management (`/admin/properties/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L90)

Full property management with status and type filtering.

**Features**:
- **Search**: By title, description, or location
- **Filter by Status**: Available, Rented, or Pending
- **Filter by Type**: Apartment, House, Villa, etc.
- **Display**: Title, owner, type, status, price, posted date
- **Quick Edit**: Direct link to Django admin

**Template**: [templates/admin/properties.html](templates/admin/properties.html)

### 4. Payment Management (`/admin/payments/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L112)

Payment tracking and analysis.

**Features**:
- **Search**: By payment reference or user email
- **Filter by Status**: Completed, Pending, or Failed
- **Display**: Payment reference, user, amount, status, associated plan, timestamp
- **Metrics**: Total payments, total amount collected, breakdown by status
- **Quick View**: Direct link to Django admin for detailed info

**Template**: [templates/admin/payments.html](templates/admin/payments.html)

### 5. Subscription Management (`/admin/subscriptions/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L135)

Subscription lifecycle management.

**Features**:
- **Search**: By user email or username
- **Filter by Status**: Active or Expired
- **Filter by Plan**: Dropdown list of all subscription plans
- **Display**: User, plan, status, start date, end date, duration
- **Quick Edit**: Direct link to Django admin

**Template**: [templates/admin/subscriptions.html](templates/admin/subscriptions.html)

### 6. Analytics & Reporting (`/admin/analytics/`)
**File**: [ghanahomes/admin_views.py](ghanahomes/admin_views.py#L158)

Historical analytics and trend analysis.

**Features**:
- **12-Month Revenue Trends**: Bar chart showing monthly revenue
- **12-Month User Growth**: Line chart showing new user registrations
- **Subscription Breakdown by Plan**: 
  - Plan name
  - Active subscriptions count
  - Total revenue generated
  - Average revenue per subscription

**Template**: [templates/admin/analytics.html](templates/admin/analytics.html)

## Database Queries & Optimization

All admin views use optimized Django ORM queries:

### Query Optimization Techniques:
1. **select_related()**: For ForeignKey relationships (user, owner, plan)
2. **prefetch_related()**: For reverse relationships
3. **aggregation**: Using Count(), Sum(), F() for efficient calculations
4. **filter()**: Efficient database-level filtering

### Example Query Patterns:
```python
# Dashboard - get all user stats
User.objects.aggregate(
    total=Count('id'),
    landlords=Count('id', filter=Q(user_type='landlord')),
    verified=Count('id', filter=Q(is_verified=True))
)

# Recent users - optimized with select_related
User.objects.select_related(
    'subscription'
).order_by('-created_at')[:5]

# Payment totals - aggregation
Payment.objects.filter(status='completed').aggregate(Sum('amount'))
```

## Management Commands

Automated tasks for scheduled operations. Run with:
```bash
python manage.py <command_name>
```

### 1. Send Subscription Reminders
**Command**: `send_subscription_reminders`
**File**: [subscriptions/management/commands/send_subscription_reminders.py](subscriptions/management/commands/send_subscription_reminders.py)
**Purpose**: Send renewal reminder emails to users 7 days before subscription expiry
**Schedule**: Run daily via cron or Celery

**Usage**:
```bash
python manage.py send_subscription_reminders
```

### 2. Check Expired Subscriptions
**Command**: `check_expired_subscriptions`
**File**: [subscriptions/management/commands/check_expired_subscriptions.py](subscriptions/management/commands/check_expired_subscriptions.py)
**Purpose**: Mark subscriptions as expired and send expiration emails
**Schedule**: Run daily via cron or Celery

**Usage**:
```bash
python manage.py check_expired_subscriptions
```

### 3. Check Expired Properties
**Command**: `check_expired_properties`
**File**: [properties/management/commands/check_expired_properties.py](properties/management/commands/check_expired_properties.py)
**Purpose**: Mark properties as expired/unavailable and send expiration emails
**Schedule**: Run daily via cron or Celery

**Usage**:
```bash
python manage.py check_expired_properties
```

### 4. Send Property Reminders
**Command**: `send_property_reminders`
**File**: [properties/management/commands/send_property_reminders.py](properties/management/commands/send_property_reminders.py)
**Purpose**: Send property expiry reminder emails to landlords 7 days before expiry
**Schedule**: Run daily via cron or Celery

**Usage**:
```bash
python manage.py send_property_reminders
```

## Setting Up Scheduled Tasks

### Option 1: Using Celery Beat (Recommended)
If Celery is configured, add these periodic tasks to your celery beat schedule:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-subscription-reminders': {
        'task': 'subscriptions.tasks.send_subscription_reminders',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'check-expired-subscriptions': {
        'task': 'subscriptions.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    'check-expired-properties': {
        'task': 'properties.tasks.check_expired_properties',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'send-property-reminders': {
        'task': 'properties.tasks.send_property_reminders',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

### Option 2: Using Cron Jobs
Add to server's crontab:

```bash
# Send subscription reminders at midnight
0 0 * * * cd /path/to/project && python manage.py send_subscription_reminders >> logs/cron.log 2>&1

# Check expired subscriptions at 1 AM
0 1 * * * cd /path/to/project && python manage.py check_expired_subscriptions >> logs/cron.log 2>&1

# Check expired properties at 2 AM
0 2 * * * cd /path/to/project && python manage.py check_expired_properties >> logs/cron.log 2>&1

# Send property reminders at 3 AM
0 3 * * * cd /path/to/project && python manage.py send_property_reminders >> logs/cron.log 2>&1
```

### Option 3: Using APScheduler (Django)
Install: `pip install django-apscheduler`

## URL Routing

All admin routes are configured in [ghanahomes/urls.py](ghanahomes/urls.py):

```python
# Admin Dashboard Routes
path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
path('admin/users/', admin_views.admin_users, name='admin_users'),
path('admin/properties/', admin_views.admin_properties, name='admin_properties'),
path('admin/payments/', admin_views.admin_payments, name='admin_payments'),
path('admin/subscriptions/', admin_views.admin_subscriptions, name='admin_subscriptions'),
path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
```

## Template Structure

All admin templates extend [templates/base.html](templates/base.html) and share consistent styling:

- **Card-based layout**: For clean organization
- **Bootstrap 5 components**: Tables, badges, charts
- **Chart.js integration**: For data visualization
- **Responsive design**: Works on mobile and desktop
- **Filter forms**: GET-based filtering for bookmarkable views
- **Search functionality**: Full-text search across key fields

### Common Template Patterns:

**Filter Form**:
```django-html
<form method="get" class="row g-3">
    <input type="text" name="q" class="form-control" placeholder="Search...">
    <select name="status" class="form-select">
        <option value="">All</option>
    </select>
    <button type="submit" class="btn btn-primary">Filter</button>
</form>
```

**Data Table**:
```django-html
<table class="table table-hover">
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td>{{ item.field }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Chart Integration**:
```javascript
const ctx = document.getElementById('chartId').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartData.map(d => d.label),
        datasets: [{
            label: 'Series',
            data: chartData.map(d => d.value),
            borderColor: '#0d6efd'
        }]
    },
    options: { responsive: true }
});
```

## Security Considerations

1. **Authentication**: All views protected by `@staff_member_required` decorator
2. **Authorization**: Only staff members can access admin features
3. **Data Protection**: No sensitive data exposed in templates
4. **CSRF Protection**: All forms include CSRF tokens
5. **SQL Injection**: Protected by Django ORM
6. **XSS Protection**: Template auto-escaping enabled

## Navigation Integration

Admin links added to user dropdown in navbar ([templates/base.html](templates/base.html)):

```django-html
{% if user.is_staff %}
<li><a class="dropdown-item" href="{% url 'admin_dashboard' %}">Admin Dashboard</a></li>
<li><a class="dropdown-item" href="{% url 'admin_users' %}">Manage Users</a></li>
<li><a class="dropdown-item" href="{% url 'admin_properties' %}">Manage Properties</a></li>
<li><a class="dropdown-item" href="{% url 'admin_payments' %}">Manage Payments</a></li>
<li><a class="dropdown-item" href="{% url 'admin_analytics' %}">Analytics</a></li>
{% endif %}
```

## Performance Tips

1. **Caching**: Consider caching dashboard statistics using Django cache framework
2. **Pagination**: Add pagination to large data tables
3. **Export**: Add CSV/PDF export functionality
4. **Bulk Operations**: Consider bulk edit/delete operations
5. **Async Tasks**: Use Celery for slow operations like email sending

## Troubleshooting

### Admin links not visible
- Ensure user `is_staff = True` in Django admin
- Clear browser cache
- Verify user is properly authenticated

### Data not showing in dashboard
- Check database queries are returning results
- Verify related objects exist (users for payments, etc.)
- Check filters aren't too restrictive

### Email reminders not sending
- Verify management command runs without errors
- Check email configuration in settings
- Verify recipients have valid email addresses
- Check logs in `logs/` directory

## Future Enhancements

1. **Bulk Actions**: Delete, verify, or modify multiple items
2. **Audit Logging**: Track admin actions for compliance
3. **Export Features**: CSV, PDF, Excel exports
4. **Advanced Analytics**: More detailed charts and metrics
5. **Permission System**: Fine-grained role-based access control
6. **Admin Notifications**: Real-time alerts for important events
7. **A/B Testing**: Feature flagging for experiments
8. **Advanced Filtering**: Date range filters, custom queries
