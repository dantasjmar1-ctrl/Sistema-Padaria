const cartToggle = document.querySelector(".cart-toggle");
const cartClose = document.querySelector(".cart-close");
const cartPanel = document.querySelector(".cart-panel");
const cartOverlay = document.querySelector(".cart-overlay");
const cartItems = document.querySelector(".cart-items");
const cartCount = document.querySelector(".cart-count");
const cartTotal = document.querySelector(".cart-total strong");
const cart = carregarCarrinho();

function carregarCarrinho() {
    const salvo = localStorage.getItem("carrinhoPadaria");
    if (salvo) {
        try {
            return new Map(JSON.parse(salvo));
        } catch (erro) {
            return new Map();
        }
    }
    return new Map();
}

function salvarCarrinho() {
    localStorage.setItem("carrinhoPadaria", JSON.stringify(Array.from(cart.entries())));
}

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
    salvarCarrinho();
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
                <span>${formatPrice(item.price)} un.</span>
                <div class="cart-qtd">
                    <button type="button" data-diminuir="${item.name}" aria-label="Diminuir">-</button>
                    <span>${item.quantity}</span>
                    <button type="button" data-aumentar="${item.name}" aria-label="Aumentar">+</button>
                </div>
            </div>
            <div class="cart-item-side">
                <span>${formatPrice(item.price * item.quantity)}</span>
                <button type="button" data-remove="${item.name}" aria-label="Remover ${item.name}">Remover</button>
            </div>
        </div>
    `).join("");
}
function atualizarPrecoCard(control) {
    const card = control.closest(".produto-card");
    const botao = card.querySelector(".add-cart");
    const precoSpan = card.querySelector(".preco");
    const precoUnitario = parsePrice(botao.dataset.price);
    const quantidade = Number(control.querySelector(".qtd-valor").textContent);
    precoSpan.textContent = formatPrice(precoUnitario * quantidade);
}

document.addEventListener("click", (event) => {
    const addButton = event.target.closest(".add-cart");
    const removeButton = event.target.closest("[data-remove]");
    const aumentarButton = event.target.closest("[data-aumentar]");
    const diminuirButton = event.target.closest("[data-diminuir]");

    if (aumentarButton) {
        const item = cart.get(aumentarButton.dataset.aumentar);
        if (item) {
            item.quantity += 1;
            renderCart();
        }
    }

    if (diminuirButton) {
        const item = cart.get(diminuirButton.dataset.diminuir);
        if (item) {
            if (item.quantity > 1) {
                item.quantity -= 1;
            } else {
                cart.delete(diminuirButton.dataset.diminuir);
            }
            renderCart();
        }
    }
const maisCard = event.target.closest(".qtd-mais-card");
const menosCard = event.target.closest(".qtd-menos-card");

if (maisCard) {
    const control = maisCard.closest(".qtd-control");
    const span = control.querySelector(".qtd-valor");
    span.textContent = Number(span.textContent) + 1;
    atualizarPrecoCard(control);
}

if (menosCard) {
    const control = menosCard.closest(".qtd-control");
    const span = control.querySelector(".qtd-valor");
    const atual = Number(span.textContent);
    if (atual > 1) span.textContent = atual - 1;
    atualizarPrecoCard(control);
}

if (addButton) {
    let name = addButton.dataset.name;
    let price = parsePrice(addButton.dataset.price);
    const card = addButton.closest(".produto-card");
    let quantidade = 1;

    if (addButton.dataset.unit === "peso") {
        const select = card.querySelector(".peso-select");
        const gramas = Number(select.value);
        name = `${name} - ${gramas}g`;
        price = (price / 1000) * gramas;
    } else {
        const qtdSpan = card.querySelector(".qtd-valor");
        if (qtdSpan) {
            quantidade = Number(qtdSpan.textContent);
            qtdSpan.textContent = "1";
            card.querySelector(".preco").textContent = formatPrice(price);
        }
    }

    const existing = cart.get(name);

    cart.set(name, {
        name,
        price,
        quantity: existing ? existing.quantity + quantidade : quantidade,
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

document.querySelector(".cart-finish")?.addEventListener("click", () => {
    if (cart.size === 0) return;
    window.location.href = "/finalizar-pedido";
});
