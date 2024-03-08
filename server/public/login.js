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
  // Handle Login POST Request
  let login_form = document.querySelector('form[name=login_form]');
  if (login_form) { // in case we are not on the login page
    login_form.addEventListener('submit', (event) => {
      // Stop the default form behavior
      event.preventDefault();

      // Grab the needed form fields
      const action = login_form.getAttribute('action');
      const method = login_form.getAttribute('method');
      const data = Object.fromEntries(new FormData(login_form).entries());

      // Submit the POST request
      server_request(action, data, method, (response) => {
        if (response.session_id != 0) {
          location.replace('/home');
        }
        else {
          alert('Invalid Username or Password');
        }
      });
    });
  }

  // Handle logout POST request
  document.querySelector('.logout_button').addEventListener('click', (event) => {
      // Submit the POST request
      server_request('/logout', {}, 'POST', (response) => {
        if (response.session_id == 0) {
          location.replace('/login');
        }
      });

  });
});