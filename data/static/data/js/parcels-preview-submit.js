const write_db_btn = document.querySelector('#write-db-btn')
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


const write_parcels = () => {
    fetch("/write-parcels/", {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin', // Do not send CSRF token to another domain.
    })
}

write_db_btn.addEventListener('click', write_parcels)

