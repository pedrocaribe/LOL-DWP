document.getElementById('contact-button').addEventListener('click', function() {
    Swal.fire({
        title: 'Contact Us',
        html:
        '<input id="swal-input1" class="swal2-input" placeholder="Name">' +
        '<input id="swal-input2" class="swal2-input" placeholder="Email">' +
        '<textarea id="swal-input3" class="swal2-textarea" placeholder="Message" style="width: 370px; height: 250px; font-size: 13px;"></textarea>',
        focusConfirm: false,
        preConfirm: () => {
            const name = document.getElementById('swal-input1').value;
            const email = document.getElementById('swal-input2').value;
            const message = document.getElementById('swal-input3').value;
            if (!email || !message) {
                Swal.showValidationMessage("Please enter email and message");
                return false;
            }

            else if (!(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email)))
            {
                Swal.showValidationMessage("Please enter a valid email address")
                return false;
            }
        
            // Assuming you have a server-side endpoint set up to handle POST requests
            fetch('/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, message })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                Swal.fire('Sent!', 'Your message has been sent.', 'success');
            })
            .catch((error) => {
                console.error('Error:', error);
                Swal.fire('Oops...', 'Something went wrong!', 'error');
            });
        
            return false; // Prevent the SweetAlert2 modal from closing automatically
        }
        
    });
});