$('#slider1, #slider2, #slider3, #slider4').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$(".plus-cart").click(function(){
    var id = $(this).attr("pid").toString();
    var elt = this.parentNode.children[2]
    $.ajax({
        type: "GET",
        url: "/pluscart/",
        data: {
            prod_id: id
        },
        success: function(data){
            elt.innerText = data.quantity
            document.getElementById("amount").innerText = data.amount
            document.getElementById("total_amount").innerText = data.total_amount
            if(data.amount > 0){
                place_order.classList.remove("disabled")
            }
        }
    })
})

$(".minus-cart").click(function(){
    var id = $(this).attr("pid").toString();
    var elt = this.parentNode.children[2]
    var place_order = document.getElementById("place_order")
    $.ajax({
        type: "GET",
        url: "/minuscart/",
        data: {
            prod_id: id
        },
        success: function(data){
            elt.innerText = data.quantity
            document.getElementById("amount").innerText = data.amount
            document.getElementById("total_amount").innerText = data.total_amount
            if(data.amount == 0){
                place_order.classList.add("disabled")
            }
        }
    })
})

$(".remove-cart").click(function(){
    var id = $(this).attr("pid").toString();
    var elt = this
    var place_order = document.getElementById("place_order")
    $.ajax({
        type: "GET",
        url: "/removecart/",
        data: {
            prod_id: id
        },
        success: function(data){
            document.getElementById("amount").innerText = data.amount
            document.getElementById("total_amount").innerText = data.total_amount
            cart_count.innerText = data.tot_itm
            if(data.amount == 0){
                place_order.classList.add("disabled")
            }
            if(data.total_items == 0){
                cart_count.style.display = "none"
            }
            document.getElementById("cart-item").remove()
        }
    })
})

var cart_count = document.getElementById("cart-count")
if(tot_itm > 0){
    cart_count.style.display = "inline"
}
else{
    cart_count.style.display = "none"
}

var chk = document.getElementById("chkout")

function check_ip(){
    if(chk.classList.contains("disabled")){
        chk.classList.remove("disabled")
    }    
}