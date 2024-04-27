document.getElementById('contact-button').addEventListener('click', function() {
    Swal.fire({
        title: 'Contact Us',
        html:
        '<input id="swal-input1" class="swal2-input" placeholder="Name">' +
        '<input id="swal-input2" class="swal2-input" placeholder="Email">' +
        '<textarea id="swal-input3" class="swal2-textarea" placeholder="Message" style="width: 370px; height: 250px; font-size: 13px;"></textarea>',
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: "Send",
        cancelButtonText: "Cancel",
        cancelButtonColor: "#FF0000",
        preConfirm: () => {
            const name = document.getElementById('swal-input1').value;
            const email = document.getElementById('swal-input2').value;
            const message = document.getElementById('swal-input3').value;

            // Following RFC-2822
            let reg_pattern = /(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/

            if (!email || !message) {
                Swal.showValidationMessage("Please enter email and message");
                return false;
            }

            else if (!(reg_pattern.test(email)))
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