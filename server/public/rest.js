document.addEventListener("DOMContentLoaded", () => {

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Define the 'request' function to handle interactions with the server
  function server_request(url, data={}, verb, callback) {
    return fetch(url, {
      credentials: 'same-origin',
      method: verb,
      body: JSON.stringify(data),
      headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(response => {
      if(callback)
        callback(response);
    })
    .catch(error => console.error('Error:', error));
  }

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // References to frequently accessed elements
  let main = document.querySelector('main');
  let table = document.querySelector('.grid_table');
  let template = document.querySelector('#new_row');
  let add_form = document.querySelector('form[name=add_user]');
  let edit_form = document.querySelector('form[name=edit_user]');

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Handle POST Requests
  add_form.addEventListener('submit', (event) => {
    // Stop the default form behavior
    event.preventDefault();

    // Grab the needed form fields
    const action = add_form.getAttribute('action');
    const method = add_form.getAttribute('method');
    const data = Object.fromEntries(new FormData(add_form).entries());

    // Submit the POST request
    server_request(action, data, method, (response) => {
      // Add the template row content to the table
      table.insertAdjacentHTML('beforeend', template.innerHTML);

      // Update the content of the newly added row
      let row = table.lastElementChild;
      row.dataset.id = response['id'];
      let columns = row.querySelectorAll('span');
      columns[0].innerText = response['id'];
      columns[1].innerText = response['first_name'];
      columns[2].innerText = response['last_name'];
      columns[3].innerText = response['username'];

      // Clear the input form and bring focus to the first field again
      let inputs = add_form.querySelectorAll('input');
      for (let i = 0; i < inputs.length-1; i++) {
        inputs[i].value = '';
      }
      inputs[0].focus();
    });
  });

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Handle PUT and DELETE Requests
  main.addEventListener('click', (event) => {

    // Open edit form
    if(event.target.classList.contains('edit_button')) {
      main.dataset.mode = 'editing';

      let row = event.target.closest('.row');
      edit_form.querySelector('input[name=first_name]').value = row.children[1].innerText.trim();
      edit_form.querySelector('input[name=last_name]').value = row.children[2].innerText.trim();
      edit_form.querySelector('input[name=username]').value = row.children[3].innerText.trim();
      edit_form.querySelector('input[name=password]').value = '';
      edit_form.dataset.id = row.dataset.id;
    }

    // Close edit form
    if(event.target.classList.contains('cancel_button')) {
      main.dataset.mode = 'viewing';
    }

    // Submit PUT request from the edit form
    if(event.target.classList.contains('save_button')) {
      const id = edit_form.dataset.id;
      let data = Object.fromEntries(new FormData(edit_form).entries());
      server_request(`/users/${id}`, data, 'PUT', function(response) {
        if(response.success) {
          let row = table.querySelector(`.row[data-id='${id}']`);
          row.children[1].innerText = data.first_name;
          row.children[2].innerText = data.last_name;
          row.children[3].innerText = data.username;
        }
        else {
          console.log('Nothing changed.');
        }
        main.dataset.mode = 'viewing';
      });
    }

    // Submit DELETE request and delete the row if successful
    if(event.target.classList.contains('delete_button')) {
      let row = event.target.closest('.row');
      server_request(`/users/${row.dataset.id}`, {}, 'DELETE', function(response) {
        if(response.success) {
          row.remove();
        }
      });
    }
  });

});