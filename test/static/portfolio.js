document.addEventListener('DOMContentLoaded', function() {
    let buy_buttons = document.getElementsByName('buy_button');
    let sell_buttons = document.getElementsByName('sell_button');
    for (let button1 of buy_buttons) {
        button1.onclick = function() {
            var symbol = button1.value;
            document.getElementById('stock_symbol').innerHTML = symbol;
            document.getElementById('popup_form').action = '/buy';
            document.getElementById('symbol').value = symbol;
            document.getElementById('popup_button').innerHTML = 'Buy';
            document.getElementById('popup').style.display = 'block';
            document.getElementById('popup').scrollIntoView();

        }
    }
    for (let button2 of sell_buttons) {
        button2.onclick = function() {
            var symbol = button2.value;
            document.getElementById('stock_symbol').innerHTML = symbol;
            document.getElementById('popup_form').action = '/sell';
            document.getElementById('symbol').value = symbol;
            document.getElementById('popup_button').innerHTML = 'Sell';
            document.getElementById('popup').style.display = 'block';
            document.getElementById('popup').scrollIntoView();
        }
    }

    document.getElementById('cancel_button').onclick = function() {
        document.getElementById('popup').style.display = 'none';
    }

    let number = document.getElementById('shares1');
    number.oninput = function() {
        if (Number.isInteger(Number(number.value)) == false) {
            document.getElementById('warning').innerHTML = "Number of shares must be an integer!";
            document.getElementById('popup_button').disabled = true;
        } else {
            document.getElementById('warning').innerHTML = "";
            document.getElementById('popup_button').disabled = false;
        }
    }
});