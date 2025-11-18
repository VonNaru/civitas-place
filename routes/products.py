from flask import Blueprint, render_template
from utils.decorators import login_required
from models.cart import CartManager
from models.products import ProductsManager

# Buat blueprint untuk product routes
products_bp = Blueprint('products', __name__, url_prefix='/barang')

@products_bp.route('/<product_template>')
@login_required
def product_page(product_template):
    """
    Dynamic render: /barang/Barang1.html  => product id mapping inside template usage
    For backward compatibility, detect product id from template name.
    """
    cart_count = CartManager.get_cart_count()
    # map template name to product_id (simple mapping)
    mapping = {
        'Barang1.html': 'p_produk_1',
        'barang2.html': 'p_sepatu_2',
        'barang3.html': 'p_headphone_3',
        'barang4.html': 'p_laptop_4'
    }
    product_id = mapping.get(product_template)
    product = ProductsManager.get(product_id) if product_id else None
    return render_template(f'barang/{product_template}', cart_count=cart_count, product=product)