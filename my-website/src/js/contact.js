// contact.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const message = document.getElementById('message').value;

        console.log('Contact Form Submitted:', { name, email, message });
        alert('Thank you for your message, ' + name + '!');
        
        form.reset();
    });
});