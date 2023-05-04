from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Basket
from django.db.models import F, FloatField, Sum
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.


def index_view(request):

    categories = Category.objects.filter(parent__isnull=True)
    products = Product.objects.annotate(
        discount = Coalesce('discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price = F('price') - F('discount')
    ).annotate(
        percentage = (1-F('total_price')/F('price'))*100
    ).order_by("-created_at")

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'products/index.html', context)

def product_detail_view(request, id):
    products = Product.objects.annotate(
        discount = Coalesce('discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price = F('price') - F('discount')
    ).annotate(
        percentage = (1-F('total_price')/F('price'))*100
    ).all()

    product = products.get(id=id)
    related_products = products.filter(category = product.category).exclude(id=product.id)

    context = {
        'product': product,
        'related_products': related_products, 
    }

    return render(request, 'products/detail.html', context)

@login_required(login_url='/login/')
def product_list_view(request):

    products = Product.objects.annotate(
        discount=Coalesce('discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price=F('price') - F('discount')
    ).annotate(
        percentage=(1 - F('total_price') / F('price')) * 100
    ).order_by("-created_at")
    categories = Category.objects.filter(parent__isnull=True)

    filter_dict = {}

    category = request.GET.get('category', None)
    if category:
        products = products.filter(
            category__in = Category.objects.get(id=int(category)).get_descendants(include_self=True)
        )
        filter_dict['category_id'] = int(category)

    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    if min_price:
        products = products.filter(total_price__gte=min_price)
        filter_dict["min_price"] = min_price
    if max_price:
        products = products.filter(total_price__lte=max_price)
        filter_dict["max_price"] = max_price

    order = request.GET.get('order', None)
    if order:
        filter_dict["order"] = 'latest'
        if order == 'name':
            products = products.order_by('name')
            filter_dict["order"] = order
        elif order == 'price':
            products = products.order_by('-total_price')
            filter_dict["order"] = order

    namecontain = request.GET.get('namecontain', None)
    if namecontain:
        filter_dict['namecontain'] = namecontain
        products = products.filter(name__icontains = namecontain)

    paginator = Paginator(products, 8)
    page = request.GET.get("page", 1)
    product_list = paginator.get_page(page)


    context = {
        'categories': categories,
        'products': product_list,
        'paginator': paginator,
        'filter_dict': filter_dict,
    }

    return render(request, 'products/list.html', context)

def product_wish_view(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    data = {}

    if request.user in product.wishlist.all():
        product.wishlist.remove(request.user)
        data['success'] = False
    else:
        product.wishlist.add(request.user)
        data['success'] = True

    return JsonResponse(data)

@login_required(login_url='/login/')
def wishlist_view(request):
    products = Product.objects.filter(wishlist__in = [request.user]).annotate(
        discount = Coalesce('discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price = F('price') - F('discount')
    )
    context = {
        "products": products
    }

    return render(request, 'wishlist/list.html', context)

@login_required(login_url='/login/')
def basket_list_view(request):
    baskets = Basket.objects.filter(user=request.user).annotate(
        discount = Coalesce('product__discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price = F('product__price') - F('discount')
    ).annotate(
        subtotal = F('total_price')*F("quantity")
    )
    total_price = baskets.aggregate(total=Coalesce(Sum("subtotal"), 0, output_field=FloatField()))['total']

    context = {
        "baskets": baskets,
        "total_price": total_price
    }
    return render(request, 'basket/list.html', context)


def add_basket_view(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    data = {}
    value = request.POST.get('value', None)
    basket_obj, created = Basket.objects.annotate(
        discount=Coalesce('product__discount_price', 0, output_field=FloatField())
    ).annotate(
        total_price=F('product__price') - F('discount')
    ).get_or_create(
        product=product, user=request.user, defaults={'quantity': 1}
    )

    if not value:
        if not created:
            basket_obj.quantity += 1
            basket_obj.save()
    else:
        basket_obj.quantity = int(value)
        basket_obj.save()
        data["subtotal"] = basket_obj.quantity * basket_obj.total_price
        baskets = Basket.objects.filter(user=request.user).annotate(
        discount = Coalesce('product__discount_price', 0, output_field=FloatField())
        ).annotate(
            total_price = F('product__price') - F('discount')
        ).annotate(
            subtotal = F('total_price') * F("quantity")
        )
        data["total"] = baskets.aggregate(total=Coalesce(Sum("subtotal"), 0, output_field=FloatField()))['total']




    return JsonResponse(data)


def remove_basket_view(request):
    product_id = request.POST.get('product_id')

    if product_id:
        removed_basket = Basket.objects.get(product__id=product_id, user=request.user)
        removed_basket.delete()
    return JsonResponse({})