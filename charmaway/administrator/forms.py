from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import NON_FIELD_ERRORS
from catalog.models import Product, ProductImage, ProductSize, Category
from customer.models import Customer
from order.models import Order
from services.models import Service

class ProductImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProductImage
        fields = ['image', 'is_main', 'order_position']
        widgets = {
            'image': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de la imagen'}),
            'order_position': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px'}),
        }

class ProductForm(ModelForm):
    GENDER_CHOICES = [
        ('', 'Seleccionar Género'),
        ('Unisex', 'Unisex'),
        ('Mujer', 'Mujer'),
        ('Hombre', 'Hombre'),
    ]
    
    COLOR_CHOICES = [
        ('', 'Seleccionar Color'),
        ('Varios tonos', 'Varios tonos'),
        ('Varios colores', 'Varios colores'),
        ('Múltiples colores', 'Múltiples colores'),
        ('Negro', 'Negro'),
        ('Blanco', 'Blanco'),
        ('Grisáceo', 'Grisáceo'),
        ('Tonos Cálidos', 'Tonos Cálidos'),
        ('Tonos Rosados', 'Tonos Rosados'),
        ('Tonos Fríos', 'Tonos Fríos'),
    ]
    
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    color = forms.ChoiceField(choices=COLOR_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'price', 'offer_price', 'gender', 'color', 'stock', 'is_available', 'is_featured', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
       
ImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    form=ProductImageForm,
    fields=['image'],
    extra=0,
    min_num=1,
    max_num=1,
    can_delete=True,
    widgets={
        'image': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de la imagen'}),
    }
)

SizeFormSet = inlineformset_factory(
    Product, 
    ProductSize,
    fields=['size', 'stock'],
    extra=0,
    min_num=1,
    can_delete=True,
    widgets={
        'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estándar, 40g, 50ml'}),
        'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
    },
    error_messages = {
        NON_FIELD_ERRORS: {
            'unique_together': "Este nombre de talla ya está registrado para este producto.",
        }
    }
)

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'category', 'price', 'offer_price', 'duration', 'image', 'is_available', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.URLInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(department__name='Servicios')

class CustomerBaseForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'surnames', 'email', 'phone', 'address', 'city', 'zip_code', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surnames': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        cust = Customer.objects.filter(email=email)
        
        if self.instance.pk:
            cust = cust.exclude(pk=self.instance.pk)
            
        if cust.exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado por otro cliente.")
            
        return email
    
class CustomerCreateForm(CustomerBaseForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        help_text="La contraseña se guardará de forma segura."
    )
    
    class Meta(CustomerBaseForm.Meta):
        fields = CustomerBaseForm.Meta.fields + ['is_superuser', 'password']
        widgets = CustomerBaseForm.Meta.widgets.copy()
        widgets['is_superuser'] = forms.CheckboxInput(attrs={'class': 'form-check-input'})
        
    def save(self, commit=True):
        customer = super().save(commit=False)
        password = self.cleaned_data.get('password')
        customer.set_password(password)
        
        if commit:
            customer.save()
            
        return customer
        
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }