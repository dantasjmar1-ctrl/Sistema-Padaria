const cartToggle = document.querySelector(".cart-toggle");
const cartClose = document.querySelector(".cart-close");
const cartPanel = document.querySelector(".cart-panel");
const cartOverlay = document.querySelector(".cart-overlay");
const cartItems = document.querySelector(".cart-items");
const cartCount = document.querySelector(".cart-count");
const cartTotal = document.querySelector(".cart-total strong");
const cart = new Map();

function parsePrice(value) {
    return Number(String(value).replace(".", "").replace(",", ".")) || 0;
}

function formatPrice(value) {
    return value.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}

function openCart() {
    document.body.classList.add("cart-open");
}

function closeCart() {
    document.body.classList.remove("cart-open");
}

function renderCart() {
    const items = Array.from(cart.values());
    const totalQuantity = items.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    cartCount.textContent = totalQuantity;
    cartTotal.textContent = formatPrice(totalPrice);

    if (items.length === 0) {
        cartItems.innerHTML = '<p class="cart-empty">Seu carrinho esta vazio.</p>';
        return;
    }

    cartItems.innerHTML = items.map((item) => `
        <div class="cart-item">
            <div>
                <strong>${item.name}</strong>
                <span>${formatPrice(item.price)} x ${item.quantity}</span>
            </div>
            <div class="cart-item-side">
                <span>${formatPrice(item.price * item.quantity)}</span>
                <button type="button" data-remove="${item.name}" aria-label="Remover ${item.name}">Remover</button>
            </div>
        </div>
    `).join("");
}

document.addEventListener("click", (event) => {
    const addButton = event.target.closest(".add-cart");
    const removeButton = event.target.closest("[data-remove]");

    if (addButton) {
        const name = addButton.dataset.name;
        const price = parsePrice(addButton.dataset.price);
        const existing = cart.get(name);

        cart.set(name, {
            name,
            price,
            quantity: existing ? existing.quantity + 1 : 1,
        });

        renderCart();
        openCart();
    }

    if (removeButton) {
        cart.delete(removeButton.dataset.remove);
        renderCart();
    }
});

cartToggle?.addEventListener("click", openCart);
cartClose?.addEventListener("click", closeCart);
cartOverlay?.addEventListener("click", closeCart);
renderCart();
