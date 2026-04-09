// static/payment/js/checkout.js

const stripe = Stripe(stripePublishableKey);

let elements;


fetch(createPaymentIntentUrl, {
    method: "POST",
    headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken 
    },
})
.then((r) => r.json())
.then((data) => {
    const clientSecret = data.clientSecret;
    elements = stripe.elements({ 
        clientSecret,
        appearance: {
            theme: 'stripe',
            variables: {
                colorPrimary: '#ff6969',
                colorBackground: '#ffffff',
                colorText: '#30313d',
                colorDanger: '#df1b41',
                colorSuccess: '#6be88a',
                colorInfo: '#1070ca',
                colorWarning: '#ffcb00',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSizeSm: '14px',
                fontSizeBase: '16px',
                fontSizeLg: '18px',
                borderRadius: '4px',
                boxShadow: 'none',
            },
            rules: {
                '.Input': {
                    padding: '10px 12px',
                    borderColor: '#ced4da',
                    borderRadius: '4px',
                    boxShadow: 'none',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #ced4da',
                },
                '.Input--invalid': {
                    borderColor: '#dc3545',
                },
                '.Label': {
                    fontWeight: 'bold',
                    marginBottom: '8px',
                    display: 'block',
                },
                '.Error': {
                    color: '#dc3545',
                    fontSize: '12px',
                    marginTop: '4px',
                },
                 '.Tab': {
                    backgroundColor: '#f8f9fa',
                    borderColor: '#ced4da',
                    borderWidth: '1px',
                    borderRadius: '4px',
                    padding: '8px 16px',
                    boxShadow: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                 },
                 '.Tab--selected': {
                    backgroundColor: '#ff696961',
                    color: '#ffffff',
                    borderColor: '#ff6969',
                 },
                 '.Tab--selected:hover': {
                    backgroundColor: '#e65c5c',
                 },
                 '.Button': {
                    backgroundColor: '#ff6969',
                    color: '#ffffff',
                    padding: '12px 20px',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                 },
                 '.Button:hover': {
                    backgroundColor: '#e65c5c',
                 }
            }
        }
    });

    const paymentElement = elements.create("payment");
    paymentElement.mount("#payment-element");
});



const form = document.getElementById("payment-form");
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    setLoading(true);

    const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {

            return_url: "http://127.0.0.1:8000/order/payment-complete/", 
        },
    });

    if (error) {
        showMessage(error.message);
        setLoading(false);
    }
});


function showMessage(messageText) {
    const messageContainer = document.querySelector("#payment-message");
    messageContainer.textContent = messageText;
}

function setLoading(isLoading) {
    const button = document.getElementById("submit-button");
    if (isLoading) {
        button.disabled = true;
        button.textContent = "Procesando...";
    } else {
        button.disabled = false;
        button.textContent = "Pagar";
    }
}
