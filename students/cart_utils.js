function updateNavbarCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;

        if (count > 0) {
            cartCountElement.classList.remove('hidden');
        } else {
            cartCountElement.classList.add('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-cart-count/')
        .then(response => response.json())
        .then(data => {
            updateNavbarCartCount(data.cart_count);
        })
        .catch(error => console.error('Error fetching cart count:', error));
});