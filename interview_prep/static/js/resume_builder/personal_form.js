// Real-time preview updates
document.getElementById('personal-form').addEventListener('input', (e) => {
    const field = e.target;
    
    switch(field.id) {
        case 'fullName':
            document.getElementById('preview-name').textContent = field.value;
            break;
        case 'email':
        case 'phone':
        case 'address':
            updateContactPreview();
            break;
        case 'summary':
            document.getElementById('preview-summary').textContent = field.value;
            break;
    }
});

function updateContactPreview() {
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;
    
    document.getElementById('preview-contact').innerHTML = `
        <span id="preview-address">${address}</span> ◆ 
        <span id="preview-phone">${phone}</span> ◆ 
        <span id="preview-email">${email}</span>
    `;
}