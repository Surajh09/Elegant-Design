console.log("hello world")

var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId: ', productId, ' ', 'action: ', action)


        if (user === 'AnonymousUser') {
            console.log("User not logged in")
        }
        else {
            updateUserOrder(productId, action)
        }
    })
}
function updateUserOrder(productId, action) {
    console.log('User Authenticated, send data...')

    var url = '/update_item/'
    fetch(url, {
        Method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log("data:", data)
        })
}


function addCookieItem(productId, action) {
    console.log('User is not authenticated')

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = { 'quantity': 1 }

        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}