document.addEventListener('DOMContentLoaded', function () {
  // sidenav initialization
  let sidenav = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(sidenav);

  // Initialization modal
  let modal = document.querySelectorAll('.modal');
  var instances = M.Modal.init(modal);
});


