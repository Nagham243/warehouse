from django.db import models
from accounts.models import ClubsModel
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile,CoachProfile


# Create your models here.


#Products
class ProductsClassificationModel(models.Model):
    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=254, null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

class ProductsModel(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        verbose_name="حالة الموافقة"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الموافقة"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_products',
        verbose_name="تمت الموافقة بواسطة"
    )

    approval_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="ملاحظات الموافقة/الرفض"
    )

    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=254, null=True)
    desc = models.TextField(null=True)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    stock = models.IntegerField(default=1, null=True)
    classification = models.ManyToManyField('ProductsClassificationModel', blank=True)
    is_enabled = models.BooleanField(default=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")
    manufacturing_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التصنيع")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="تاريخ انتهاء الصلاحية")

    @property
    def is_expiring_soon(self):
        if not self.expiration_date:
            return False

        import datetime
        one_month_later = datetime.date.today() + datetime.timedelta(days=30)
        return self.expiration_date <= one_month_later and self.expiration_date > datetime.date.today()

    @property
    def is_expired(self):
        if not self.expiration_date:
            return False

        import datetime
        return self.expiration_date < datetime.date.today()

    def __str__(self):
        return self.title

    def approve(self, approved_by_user, notes=""):
        """Approve the product"""
        self.approval_status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = approved_by_user
        self.approval_notes = notes
        self.is_enabled = True
        self.save()

    def reject(self, rejected_by_user, notes=""):
        """Reject the product"""
        self.approval_status = 'rejected'
        self.approved_at = timezone.now()
        self.approved_by = rejected_by_user
        self.approval_notes = notes
        self.is_enabled = False
        self.save()

    @property
    def can_be_sold(self):
        """Check if product can be sold (approved and not expired)"""
        return (
                self.approval_status == 'approved' and
                self.is_enabled and
                not self.is_expired and
                self.stock > 0
        )

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ['-creation_date']

class ProductsImage(models.Model):
    product = models.ForeignKey('ProductsModel', on_delete=models.CASCADE)
    img = models.ImageField(upload_to="Products/imgs/%Y/%m/%d", blank=True, null=True)
    img_base64 = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

class ProductsRate(models.Model):
    product = models.ForeignKey('ProductsModel', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    msg = models.TextField()
    rate = models.IntegerField()
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")





#Services
class ServicesClassificationModel(models.Model):
    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=254, null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

    def __str__(self):
        return self.title


class ServicesModel(models.Model):
    PRICING_PERIOD_CHOICES = [
        (1, '1 Month'),
        (2, '2 Months'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        verbose_name="حالة الموافقة"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الموافقة"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_services',
        verbose_name="تمت الموافقة بواسطة"
    )

    approval_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="ملاحظات الموافقة/الرفض"
    )

    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    coaches = models.ManyToManyField('accounts.CoachProfile', blank=True, related_name='services')
    title = models.CharField(max_length=254, null=True)
    desc = models.TextField(null=True)
    subscription_days = models.IntegerField(default=30, null=True, blank=True)
    age_from = models.IntegerField(default=0, null=True, blank=True)
    age_to = models.IntegerField(default=100, null=True, blank=True)

    # Pricing fields
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price for the specified pricing period")
    pricing_period_months = models.IntegerField(
        choices=PRICING_PERIOD_CHOICES,
        default=1,
        help_text="Number of months this price covers"
    )
    discounted_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    classification = models.ManyToManyField('ServicesClassificationModel', blank=True)
    is_enabled = models.BooleanField(default=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")
    duration = models.IntegerField(help_text="Duration in minutes", default=0)
    image = models.ImageField(upload_to='services/', null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def monthly_price(self):
        """Calculate the monthly price based on the pricing period"""
        current_price = self.discounted_price if self.discounted_price else self.price
        return current_price / self.pricing_period_months

    @property
    def total_subscription_days(self):
        """Calculate total subscription days based on pricing period"""
        return self.pricing_period_months * 30  # Approximate days per month

    def get_price_for_months(self, months):
        """Calculate price for a specific number of months"""
        monthly_rate = self.monthly_price
        return monthly_rate * months

    @property
    def effective_price(self):
        return self.discounted_price if self.discounted_price else self.price

    def approve(self, approved_by_user, notes=""):
        """Approve the product"""
        self.approval_status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = approved_by_user
        self.approval_notes = notes
        self.is_enabled = True
        self.save()

    def reject(self, rejected_by_user, notes=""):
        """Reject the product"""
        self.approval_status = 'rejected'
        self.approved_at = timezone.now()
        self.approved_by = rejected_by_user
        self.approval_notes = notes
        self.is_enabled = False
        self.save()

    @property
    def can_be_sold(self):
        """Check if product can be sold (approved and not expired)"""
        return (
                self.approval_status == 'approved' and
                self.is_enabled
        )

    class Meta:
        verbose_name = "خدمة"
        verbose_name_plural = "الخدمات"
        ordering = ['-creation_date']

class ServicesImage(models.Model):
    product = models.ForeignKey('ServicesModel', on_delete=models.CASCADE)
    img = models.ImageField(upload_to="Services/imgs/%Y/%m/%d", blank=True, null=True)
    img_base64 = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

class ServicesRate(models.Model):
    
    product = models.ForeignKey('ServicesModel', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    msg = models.TextField()
    rate = models.IntegerField()
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")



#Blog
class BlogClassificationModel(models.Model):
    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=254, null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class Blog(models.Model):
    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=254, null=True)
    desc = models.CharField(max_length=254, null=True)
    img = models.ImageField(upload_to="blog/imgs/%Y/%m/%d", blank=True, null=True)
    body = RichTextUploadingField(config_name='article_editor')  # Changed this line

    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

    def __str__(self):
        return self.title or "Untitled Article"



class ServiceOrderModel(models.Model):
    service = models.ForeignKey(ServicesModel, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    is_complited = models.BooleanField(default=False)
    end_datetime = models.DateTimeField()
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

    def has_subscription(self):
        if self.end_datetime > timezone.now():
            return True
        return False


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductsModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.product.price

class ServiceCartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(ServicesModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.title} ({self.quantity})"

    @property
    def total_price(self):
        price = self.service.discounted_price if self.service.discounted_price else self.service.price
        return self.quantity * price

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('cancelled', 'تم الإلغاء'),
        ('completed', 'مكتمل'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'بطاقة ائتمان'),
        ('cash_on_delivery', 'الدفع عند الاستلام'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    club = models.ForeignKey(ClubsModel, on_delete=models.CASCADE, related_name='orders', null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

    transfer_receipt = models.ImageField(upload_to='transfer_receipts/', null=True, blank=True, verbose_name="إثبات التحويل")
    transfer_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ رفع إثبات التحويل")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_vendor_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="إجمالي عمولة البائعين"
    )

    club_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="إيرادات النادي"
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def confirmed_orders_with_service(self, service, user=None):
        """
        Get confirmed orders containing a specific service
        """
        queryset = self.filter(
            status='confirmed',
            items__service=service
        )

        if user:
            queryset = queryset.filter(user=user)

        return queryset.distinct()

    def calculate_commission_breakdown(self):
        """Calculate commission breakdown for this order"""
        from decimal import Decimal
        print("\nStarting commission breakdown calculation...")
        print(f"Order ID: {self.id}, Total Price: {self.total_price}")

        commission_data = {
            'total_vendor_commission': Decimal('0.00'),
            'club_revenue': Decimal('0.00'),
            'vendor_breakdowns': []
        }

        # Group items by vendor
        vendor_items = {}
        print(f"\nProcessing {self.items.count()} items...")

        for item in self.items.filter(product__isnull=False):
            print(f"\nProcessing item ID: {item.id}, Product: {item.product.title if item.product else 'None'}")

            # Get vendor from product creator's coach profile
            vendor = None
            if item.product.creator:
                print(f"Product creator found: {item.product.creator}")
                if hasattr(item.product.creator, 'userprofile'):
                    print("Creator has userprofile")
                    if hasattr(item.product.creator.userprofile, 'Coach_profile'):
                        vendor = item.product.creator.userprofile.Coach_profile
                        print(f"Vendor found: {vendor}, ID: {vendor.id}")
                    else:
                        print("Creator's userprofile has no Coach_profile")
                else:
                    print("Creator has no userprofile")
            else:
                print("Product has no creator")

            if vendor:
                if vendor.id not in vendor_items:
                    commission_rate = Decimal(str(vendor.get_current_commission_rate()))
                    print(f"New vendor detected. Commission rate: {commission_rate}%")
                    vendor_items[vendor.id] = {
                        'vendor': vendor,
                        'items': [],
                        'total_amount': Decimal('0.00'),
                        'commission_rate': commission_rate,
                        'commission_amount': Decimal('0.00')
                    }

                item_total = Decimal(str(item.price)) * Decimal(str(item.quantity))
                print(f"Item total: {item_total} (price: {item.price}, quantity: {item.quantity})")

                vendor_items[vendor.id]['items'].append(item)
                vendor_items[vendor.id]['total_amount'] += item_total
                print(f"Updated vendor {vendor.id} total: {vendor_items[vendor.id]['total_amount']}")
            else:
                print("No vendor associated with this item")

        print("\nCalculating commissions for each vendor...")
        for vendor_id, vendor_data in vendor_items.items():
            print(f"\nProcessing vendor ID: {vendor_id}")
            print(f"Vendor total amount: {vendor_data['total_amount']}")
            print(f"Vendor commission rate: {vendor_data['commission_rate']}%")

            commission_rate = vendor_data['commission_rate'] / Decimal('100')
            commission_amount = vendor_data['total_amount'] * commission_rate

            print(f"Calculated commission amount: {commission_amount}")

            vendor_data['commission_amount'] = commission_amount
            commission_data['total_vendor_commission'] += commission_amount
            commission_data['vendor_breakdowns'].append(vendor_data)

            print(f"Updated total vendor commission: {commission_data['total_vendor_commission']}")

        # Calculate club revenue (total - commissions)
        commission_data['club_revenue'] =  commission_data['total_vendor_commission']
        print(f"\nFinal calculations:")
        print(f"Total order amount: {self.total_price}")
        print(f"Total vendor commission: {commission_data['total_vendor_commission']}")
        print(f"Club revenue: {commission_data['club_revenue']}")

        return commission_data

    def update_commission_fields(self):
        """Update commission fields in the order"""
        print("\nUpdating commission fields...")
        print(f"Current status: {self.status}")

        if self.status == 'confirmed':
            print("Status is confirmed, proceeding with commission calculation")
            breakdown = self.calculate_commission_breakdown()

            print("\nUpdating order fields:")
            print(f"Old total_vendor_commission: {self.total_vendor_commission}")
            print(f"New total_vendor_commission: {breakdown['total_vendor_commission']}")
            print(f"Old club_revenue: {self.club_revenue}")
            print(f"New club_revenue: {breakdown['club_revenue']}")

            self.total_vendor_commission = breakdown['total_vendor_commission']
            self.club_revenue = breakdown['club_revenue']
            self.save()
            print("Commission fields updated and saved")
        else:
            print("Status is not confirmed, skipping commission update")


class OrderVendorCommission(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='vendor_commissions'
    )
    vendor = models.ForeignKey(
        'accounts.CoachProfile',
        on_delete=models.CASCADE,
        verbose_name="البائع"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="إجمالي مبلغ البائع"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="نسبة العمولة (%)"
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="مبلغ العمولة"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عمولة بائع"
        verbose_name_plural = "عمولات البائعين"
        unique_together = ['order', 'vendor']

    def __str__(self):
        return f"Commission for {self.vendor.business_name} - Order #{self.order.id}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductsModel, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(ServicesModel, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        if self.product:
            return f"{self.product.title} ({self.quantity})"
        elif self.service:
            return f"{self.service.title} ({self.quantity})"
        return f"Order Item #{self.id}"

    def get_total(self):
        return self.price * self.quantity

    @property
    def vendor_commission_info(self):
        """Get vendor commission info for this item"""
        if not self.product:
            return None

        vendor = None
        if (self.product.creator and
                hasattr(self.product.creator, 'userprofile') and
                hasattr(self.product.creator.userprofile, 'Coach_profile')):
            vendor = self.product.creator.userprofile.Coach_profile

        if vendor:
            item_total = float(self.price * self.quantity)
            commission_rate = vendor.get_current_commission_rate()
            commission_amount = item_total * (commission_rate / 100)

            return {
                'vendor': vendor,
                'item_total': item_total,
                'commission_rate': commission_rate,
                'commission_amount': commission_amount,
                'club_revenue': item_total - commission_amount
            }
        return None

@property
def get_order_type(self):
    """Returns the type of the order: products, services, or mixed"""
    has_products = self.items.filter(product__isnull=False).exists()
    has_services = self.items.filter(service__isnull=False).exists()

    if has_products and has_services:
        return 'mixed'
    elif has_products:
        return 'products'
    elif has_services:
        return 'services'
    else:
        return 'unknown'

@property
def get_order_type_display(self):
    """Returns the display name for the order type in Arabic"""
    order_type = self.get_order_type
    if order_type == 'products':
        return 'منتجات'
    elif order_type == 'services':
        return 'خدمات'
    elif order_type == 'mixed':
        return 'منتجات وخدمات'
    else:
        return 'غير معروف'

class OrderCancellation(models.Model):
    CANCELLATION_REASONS = [
        ('customer_request', 'Customer requested cancellation'),
        ('payment_failed', 'Payment failed'),
        ('out_of_stock', 'Product/Service out of stock'),
        ('duplicate_order', 'Duplicate order'),
        ('technical_issue', 'Technical issue'),
        ('fraud_suspected', 'Fraud suspected'),
        ('other', 'Other'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='cancellation')
    reason = models.CharField(max_length=50, choices=CANCELLATION_REASONS)
    custom_reason = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    cancelled_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Cancellation"
        verbose_name_plural = "Order Cancellations"

    def __str__(self):
        return f"Cancellation for Order #{self.order.id}"

    def get_reason_display_text(self):
        if self.reason == 'other' and self.custom_reason:
            return self.custom_reason
        return dict(self.CANCELLATION_REASONS)[self.reason]