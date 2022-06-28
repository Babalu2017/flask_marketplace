document.addEventListener('DOMContentLoaded', function () {
  // sidenav initialization
  let sidenav = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(sidenav);

  // Initialization modal
  let modal = document.querySelectorAll('.modal');
  var instances = M.Modal.init(modal);

  // datepicker initialization
  let datepicker = document.querySelectorAll(".datepicker");
  M.Datepicker.init(datepicker, {
    format: "dd mmmm, yyyy",
    i18n: { done: "Select" }
  });

  // select initialization
  let selects = document.querySelectorAll("select");
  M.FormSelect.init(selects);

  // Initialization Collapsible
  let collap = document.querySelectorAll('.collapsible');
  M.Collapsible.init(collap);

});




